"""Input validation helpers."""

from __future__ import annotations

import ipaddress
import re
from urllib.parse import urlparse

EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
PHONE_PATTERN = re.compile(r"^(?:\+?63|0)?9\d{9}$|^(?:\+?63|0)?\d{7,15}$")


def validate_email(email: str) -> str:
    """Validate an email address."""

    if not EMAIL_PATTERN.match(email.strip()):
        raise ValueError("Invalid email address.")
    return email.strip().lower()


def validate_phone_number(phone_number: str) -> str:
    """Validate a Philippine or international phone number."""

    normalized = re.sub(r"[\s\-()]+", "", phone_number.strip())
    if not PHONE_PATTERN.match(normalized):
        raise ValueError("Invalid phone number.")
    return normalized


def validate_url(url: str) -> str:
    """Validate that a URL uses http or https."""

    parsed = urlparse(url.strip())
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise ValueError("Invalid URL.")
    return url.strip()


def validate_qr_data(qr_data: str) -> str:
    """Validate QR payload text."""

    cleaned = qr_data.strip()
    if not cleaned:
        raise ValueError("QR data cannot be empty.")
    return cleaned


def is_valid_ip_address(value: str) -> bool:
    """Return True when a value is a valid IP address."""

    try:
        ipaddress.ip_address(value)
        return True
    except ValueError:
        return False

