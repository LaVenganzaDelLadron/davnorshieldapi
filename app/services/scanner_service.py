from __future__ import annotations
from collections.abc import Mapping
from app.ai.phishing_detector import detect_phishing
from app.ai.qr_detector import detect_qr_threat
from app.ai.sms_detector import detect_sms_scam
from app.models.enums import ThreatCategory
from app.schemas.scanner import QRScanRequest, SMSScanRequest, ScanResponse, URLScanRequest
from app.utils.recommendation import get_recommendations_for_category
from app.utils.risk_calculator import calculate_risk_score
from app.utils.sms_parser import clean_message, extract_keywords, extract_links
from app.utils.url_parser import extract_domain, is_ip_address_url
from app.utils.validator import validate_qr_data, validate_url


class ScannerService:
    """Heuristic scanner service for URLs, SMS, and QR payloads."""

    @staticmethod
    def _normalize_scan_result(result: Mapping[str, object]) -> ScanResponse:
        """Convert AI detector output into the public scanner schema."""

        category_value = result.get("category", ThreatCategory.other)
        if isinstance(category_value, ThreatCategory):
            category = category_value
        else:
            try:
                category = ThreatCategory(str(category_value))
            except ValueError:
                category = ThreatCategory.other
        score = result.get("risk_score", result.get("score", 0.0))
        risk_level = str(result.get("risk_level", "SAFE"))
        explanation = str(result.get("explanation", "No explanation available."))
        recommendations = result.get("recommendations", [])
        if not isinstance(recommendations, list):
            recommendations = list(recommendations)  # type: ignore[arg-type]
        return ScanResponse(
            risk_score=float(score),
            risk_level=risk_level,
            threat_category=category,
            explanation=explanation,
            recommendations=[str(item) for item in recommendations],
        )

    async def scan_url(self, payload: URLScanRequest) -> ScanResponse:
        """Scan a URL for phishing indicators."""

        url = validate_url(str(payload.url))
        result = detect_phishing(url)
        return self._normalize_scan_result(result)

    async def scan_sms(self, payload: SMSScanRequest) -> ScanResponse:
        """Scan an SMS message for scam patterns."""

        message = clean_message(payload.message)
        result = detect_sms_scam(message)
        return self._normalize_scan_result(result)

    async def scan_qr(self, payload: QRScanRequest) -> ScanResponse:
        """Scan QR text payloads for scam patterns."""

        qr_data = validate_qr_data(payload.qr_data)
        result = detect_qr_threat(qr_data)
        return self._normalize_scan_result(result)

    async def analyze_text(self, text: str) -> ScanResponse:
        """Analyze arbitrary text for threat indicators."""

        cleaned = clean_message(text)
        links = extract_links(cleaned)
        keywords = extract_keywords(cleaned)
        malicious_url = bool(links)
        suspicious_keywords = len(keywords)
        category = ThreatCategory.sms_scam if len(cleaned) < 280 else ThreatCategory.other
        if malicious_url:
            category = ThreatCategory.phishing
        if "qr" in cleaned.lower():
            category = ThreatCategory.qr_scam
        risk_score = calculate_risk_score(
            malicious_url=malicious_url,
            suspicious_keywords=suspicious_keywords,
            duplicate_reports=0,
            outbreak_score=0.0,
            suspicious_phone=False,
            qr_match=category == ThreatCategory.qr_scam,
        )
        if malicious_url and links and is_ip_address_url(links[0]):
            risk_score = min(100.0, risk_score + 10.0)
        recommendations = get_recommendations_for_category(category)
        domain = extract_domain(links[0]) if links else "n/a"
        return ScanResponse(
            risk_score=risk_score,
            risk_level="DANGEROUS" if risk_score >= 75 else "SUSPICIOUS" if risk_score >= 35 else "SAFE",
            threat_category=category,
            explanation=f"Analyzed text with domain context {domain}.",
            recommendations=recommendations,
        )
