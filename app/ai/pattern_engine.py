"""Similarity and clustering engine for report patterns."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from typing import Iterable
from uuid import UUID

from app.ai.keyword_model import detect_profile
from app.utils.geo import normalize_barangay_name, normalize_municipality_name
from app.utils.qr_parser import extract_destination
from app.utils.url_parser import extract_domain, normalize_url


@dataclass(slots=True)
class PatternComparison:
    """Result of comparing two report signals."""

    similarity_score: float
    matched_features: list[str] = field(default_factory=list)


@dataclass(slots=True)
class PatternCluster:
    """Cluster of similar reports."""

    signature: str
    report_ids: list[UUID] = field(default_factory=list)


def compare_reports(left: dict[str, object], right: dict[str, object]) -> PatternComparison:
    """Compare two report payloads and compute a similarity score."""

    score = 0.0
    matched: list[str] = []

    left_phone = str(left.get("phone_number") or "").strip().lower()
    right_phone = str(right.get("phone_number") or "").strip().lower()
    if left_phone and left_phone == right_phone:
        score += 25.0
        matched.append("phone_number")

    left_url = str(left.get("suspicious_url") or "").strip()
    right_url = str(right.get("suspicious_url") or "").strip()
    if left_url and right_url:
        if normalize_url(left_url) == normalize_url(right_url):
            score += 25.0
            matched.append("domain")
        elif extract_domain(left_url) == extract_domain(right_url):
            score += 18.0
            matched.append("domain")

    left_qr = str(left.get("qr_data") or "").strip()
    right_qr = str(right.get("qr_data") or "").strip()
    if left_qr and right_qr and extract_destination(left_qr) == extract_destination(right_qr):
        score += 20.0
        matched.append("qr_destination")

    left_keywords = set(detect_profile(f"{left.get('title', '')} {left.get('description', '')}"))
    right_keywords = set(detect_profile(f"{right.get('title', '')} {right.get('description', '')}"))
    overlap = left_keywords & right_keywords
    if overlap:
        score += min(10.0 + (len(overlap) * 5.0), 25.0)
        matched.append("keywords")

    if normalize_barangay_name(str(left.get("barangay_name", ""))) == normalize_barangay_name(str(right.get("barangay_name", ""))):
        score += 10.0
        matched.append("barangay")

    if normalize_municipality_name(str(left.get("municipality_name", ""))) == normalize_municipality_name(str(right.get("municipality_name", ""))):
        score += 7.0
        matched.append("municipality")

    return PatternComparison(similarity_score=min(score, 100.0), matched_features=matched)


def cluster_reports(reports: Iterable[dict[str, object]], threshold: float = 60.0) -> list[PatternCluster]:
    """Cluster report dictionaries by shared signal signature."""

    clusters: dict[str, PatternCluster] = {}
    for report in reports:
        parts = [
            str(report.get("phone_number") or "").strip().lower(),
            extract_domain(str(report.get("suspicious_url") or "")).lower(),
            extract_destination(str(report.get("qr_data") or "")).lower(),
            normalize_barangay_name(str(report.get("barangay_name") or "")),
            normalize_municipality_name(str(report.get("municipality_name") or "")),
        ]
        signature = "|".join(sorted(part for part in parts if part))
        cluster = clusters.setdefault(signature, PatternCluster(signature=signature))
        report_id = report.get("id")
        if isinstance(report_id, UUID):
            cluster.report_ids.append(report_id)
    return [cluster for cluster in clusters.values() if len(cluster.report_ids) >= 2 or threshold <= 0]

