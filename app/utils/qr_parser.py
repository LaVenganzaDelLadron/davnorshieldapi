"""QR payload parsing helpers."""

from __future__ import annotations

import re
from urllib.parse import urlparse

URL_PATTERN = re.compile(r"^https?://", re.IGNORECASE)
PAYMENT_HINTS = {"gcash", "maya", "paymaya", "pay", "payment", "qrph"}
CONTACT_HINTS = {"tel:", "sms:", "mailto:", "vcard", "contact"}


def decode_qr_text(data: str) -> str:
    """Return a cleaned QR payload string."""

    return data.strip()


def classify_qr_type(data: str) -> str:
    """Classify a QR payload into URL, payment, contact, or text."""

    cleaned = decode_qr_text(data).lower()
    if URL_PATTERN.match(cleaned):
        return "url"
    if any(hint in cleaned for hint in PAYMENT_HINTS):
        return "payment"
    if any(hint in cleaned for hint in CONTACT_HINTS):
        return "contact"
    parsed = urlparse(cleaned)
    if parsed.scheme and parsed.netloc:
        return "url"
    return "text"


def extract_destination(data: str) -> str:
    """Extract the destination encoded in the QR payload."""

    cleaned = decode_qr_text(data)
    qr_type = classify_qr_type(cleaned)
    if qr_type == "url":
        return cleaned
    if qr_type == "contact":
        return cleaned
    if qr_type == "payment":
        return cleaned
    return cleaned

