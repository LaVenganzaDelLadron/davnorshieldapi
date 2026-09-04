"""Threat pattern analysis service."""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.enums import ThreatCategory
from app.models.scam_report import ScamReport
from app.models.threat_pattern import ThreatPattern
from app.repositories.report_repository import ReportRepository
from app.repositories.threat_repository import ThreatRepository
from app.utils.date_utils import utc_now
from app.utils.geo import normalize_barangay_name, normalize_municipality_name
from app.utils.qr_parser import extract_destination
from app.utils.risk_calculator import calculate_confidence_score
from app.utils.sms_parser import extract_keywords
from app.utils.url_parser import extract_domain, normalize_url


@dataclass(slots=True)
class PatternAnalysisResult:
    """Result of analyzing a scam report against threat patterns."""

    pattern: ThreatPattern
    created: bool
    similarity_score: float


class PatternService:
    """Pattern-engine logic for consolidating related reports."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.threats = ThreatRepository(db)
        self.reports = ReportRepository(db)

    def _keywords_for_report(self, report: ScamReport) -> str:
        combined = f"{report.title} {report.description}"
        if report.qr_data:
            combined = f"{combined} {report.qr_data}"
        keywords = extract_keywords(combined)
        return " ".join(keywords[:12])

    def _similarity_score(self, report: ScamReport, pattern: ThreatPattern) -> float:
        score = 0.0
        report_domain = (
            extract_domain(normalize_url(report.suspicious_url))
            if report.suspicious_url
            else None
        )
        report_phone = report.phone_number
        report_qr = extract_destination(report.qr_data) if report.qr_data else None
        report_keywords = self._keywords_for_report(report)

        if pattern.malicious_domain and report_domain:
            if pattern.malicious_domain.lower() == report_domain.lower():
                score += 35.0
        if pattern.malicious_phone and report_phone:
            if pattern.malicious_phone == report_phone:
                score += 35.0
        if pattern.keyword_signature and report_keywords:
            pattern_keywords = set(pattern.keyword_signature.lower().split())
            report_keywords_set = set(report_keywords.lower().split())
            overlap = len(pattern_keywords & report_keywords_set)
            if overlap:
                score += min(20.0 + overlap * 5.0, 35.0)
        if report_qr and pattern.keyword_signature:
            if report_qr.lower() in pattern.keyword_signature.lower():
                score += 20.0
        if pattern.threat_category == report.threat_category:
            score += 10.0
        return min(score, 100.0)

    async def analyze_report_patterns(self, report: ScamReport) -> PatternAnalysisResult:
        """Find or create a threat pattern for a report."""

        report_domain = (
            extract_domain(normalize_url(report.suspicious_url))
            if report.suspicious_url
            else None
        )
        report_keywords = self._keywords_for_report(report)
        report_qr = extract_destination(report.qr_data) if report.qr_data else None
        pattern = await self.threats.find_matching_pattern(
            malicious_domain=report_domain,
            malicious_phone=report.phone_number,
            keyword_signature=report_keywords,
            threat_category=report.threat_category,
        )
        if pattern is not None:
            similarity = self._similarity_score(report, pattern)
            confidence = calculate_confidence_score(
                evidence_points=3 if similarity >= 50 else 2,
                corroborating_reports=pattern.reports_count,
                outbreak_score=similarity,
            )
            updated = await self.threats.update_pattern(
                pattern.id,
                {
                    "confidence_score": confidence,
                    "reports_count": pattern.reports_count + 1,
                    "last_seen": utc_now(),
                    "malicious_domain": pattern.malicious_domain or report_domain,
                    "malicious_phone": pattern.malicious_phone or report.phone_number,
                    "keyword_signature": pattern.keyword_signature or report_keywords,
                    "threat_category": pattern.threat_category or report.threat_category,
                },
            )
            if updated is None:
                raise RuntimeError("Failed to update matched threat pattern.")
            return PatternAnalysisResult(pattern=updated, created=False, similarity_score=similarity)

        pattern_name_parts = [
            report.threat_category.value,
            report_domain or report.phone_number or (report_qr or "general"),
            str(report.id)[:8],
        ]
        confidence = calculate_confidence_score(
            evidence_points=2,
            corroborating_reports=0,
            outbreak_score=0.0,
        )
        created_pattern = await self.threats.create_pattern(
            {
                "pattern_name": "-".join(part.replace(" ", "-") for part in pattern_name_parts),
                "threat_category": report.threat_category,
                "malicious_domain": report_domain,
                "malicious_phone": report.phone_number,
                "keyword_signature": report_keywords,
                "confidence_score": confidence,
                "reports_count": 1,
                "first_seen": utc_now(),
                "last_seen": utc_now(),
            }
        )
        return PatternAnalysisResult(pattern=created_pattern, created=True, similarity_score=100.0)

    async def detect_campaign(self, reports: list[ScamReport]) -> dict[str, object]:
        """Detect a coordinated campaign from related reports."""

        if not reports:
            return {"detected": False, "reason": "No reports supplied."}
        grouped: Counter[str] = Counter()
        for report in reports:
            key = self._campaign_key(report)
            grouped[key] += 1
        top_key, top_count = grouped.most_common(1)[0]
        return {
            "detected": top_count >= 3,
            "signature": top_key,
            "report_count": top_count,
            "groups": dict(grouped),
        }

    async def merge_similar_reports(self, reports: list[ScamReport]) -> dict[str, object]:
        """Cluster reports that share a common signature."""

        clusters: dict[str, list[UUID]] = {}
        for report in reports:
            clusters.setdefault(self._campaign_key(report), []).append(report.id)
        duplicates = {signature: ids for signature, ids in clusters.items() if len(ids) > 1}
        return {
            "cluster_count": len(clusters),
            "duplicate_groups": duplicates,
        }

    async def update_pattern_statistics(
        self,
        pattern_id: UUID,
        *,
        reports_count: int = 1,
        confidence_score: float | None = None,
        last_seen: datetime | None = None,
    ) -> ThreatPattern | None:
        """Update aggregate statistics for a threat pattern."""

        pattern = await self.threats.get_pattern(pattern_id)
        if pattern is None:
            return None
        payload: dict[str, object] = {
            "reports_count": pattern.reports_count + reports_count,
            "last_seen": last_seen or utc_now(),
        }
        if confidence_score is not None:
            payload["confidence_score"] = confidence_score
        updated = await self.threats.update_pattern(pattern_id, payload)
        return updated

    def _campaign_key(self, report: ScamReport) -> str:
        parts: list[str] = []
        if report.suspicious_url:
            parts.append(extract_domain(normalize_url(report.suspicious_url)).lower())
        if report.phone_number:
            parts.append(report.phone_number.lower())
        if report.qr_data:
            parts.append(extract_destination(report.qr_data).lower())
        parts.extend(extract_keywords(f"{report.title} {report.description}"))
        barangay = normalize_barangay_name(str(report.barangay_id))
        municipality = normalize_municipality_name(str(report.municipality_id))
        parts.extend([barangay, municipality])
        return "|".join(sorted(set(parts)))

