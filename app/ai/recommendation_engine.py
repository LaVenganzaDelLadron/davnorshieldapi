"""Localized recommendation generation."""

from __future__ import annotations

from app.constants import ThreatCategory


RECOMMENDATIONS: dict[str, dict[str, list[str]]] = {
    ThreatCategory.phishing.value: {
        "en": ["Do not click the link.", "Verify the sender.", "Report the message."],
        "tl": ["Huwag i-click ang link.", "Beripikahin ang sender.", "I-report ang mensahe."],
        "ceb": ["Ayaw i-click ang link.", "Susiha ang tigpadala.", "Ireport ang mensahe."],
    },
    ThreatCategory.sms_scam.value: {
        "en": ["Ignore unknown SMS.", "Do not share OTPs.", "Block the sender."],
        "tl": ["Huwag pansinin ang di kilalang SMS.", "Huwag ibahagi ang OTP.", "I-block ang sender."],
        "ceb": ["Ayaw tagda ang wala mailhi nga SMS.", "Ayaw ihatag ang OTP.", "I-block ang sender."],
    },
    ThreatCategory.qr_scam.value: {
        "en": ["Verify the merchant.", "Do not scan unknown QR codes.", "Inspect the destination."],
        "tl": ["Beripikahin ang merchant.", "Huwag i-scan ang di kilalang QR code.", "Suriin ang destinasyon."],
        "ceb": ["Susiha ang merchant.", "Ayaw i-scan ang dili kaila nga QR code.", "Tan-awa ang destinasyon."],
    },
    ThreatCategory.marketplace_scam.value: {
        "en": ["Verify the seller.", "Avoid advance payments.", "Use trusted payment channels."],
        "tl": ["Beripikahin ang seller.", "Iwasan ang advance payment.", "Gumamit ng trusted payment channels."],
        "ceb": ["Susiha ang seller.", "Likayi ang advance payment.", "Gamita ang kasaligan nga payment channels."],
    },
    ThreatCategory.fake_job.value: {
        "en": ["Verify the company.", "Never pay to apply.", "Check the job posting independently."],
        "tl": ["Beripikahin ang kumpanya.", "Huwag magbayad para ma-hire.", "Suriin ang job posting."],
        "ceb": ["Susiha ang kompanya.", "Ayaw bayad para ma-apply.", "Tinoa ang job posting."],
    },
    ThreatCategory.fake_investment.value: {
        "en": ["Be skeptical of guaranteed profits.", "Check licenses.", "Avoid rushing into deposits."],
        "tl": ["Magduda sa garantisadong kita.", "Suriin ang lisensya.", "Huwag magmadali sa deposit."],
        "ceb": ["Pagmatngon sa sigurado nga kita.", "Susiha ang lisensya.", "Ayaw pagdali sa deposit."],
    },
    ThreatCategory.identity_theft.value: {
        "en": ["Protect personal information.", "Monitor accounts.", "Report unauthorized activity."],
        "tl": ["Protektahan ang personal na impormasyon.", "I-monitor ang accounts.", "I-report ang hindi awtorisadong aktibidad."],
        "ceb": ["Protektahi ang personal nga impormasyon.", "Bantayi ang accounts.", "Ireport ang dili awtorisadong kalihokan."],
    },
    ThreatCategory.malware.value: {
        "en": ["Do not open the file.", "Run a security scan.", "Isolate the device."],
        "tl": ["Huwag buksan ang file.", "Magpatakbo ng security scan.", "Ihiwalay ang device."],
        "ceb": ["Ayaw ablihi ang file.", "Magpadagan og security scan.", "Ihiwalay ang device."],
    },
}


def generate_recommendations(category: ThreatCategory | str, language: str = "en") -> list[str]:
    """Return localized recommendations for a category."""

    key = category.value if isinstance(category, ThreatCategory) else str(category)
    language_key = language.lower()
    category_map = RECOMMENDATIONS.get(key, RECOMMENDATIONS[ThreatCategory.phishing.value])
    return category_map.get(language_key, category_map["en"])

