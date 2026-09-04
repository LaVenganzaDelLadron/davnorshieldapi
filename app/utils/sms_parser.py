"""SMS parsing helpers."""

from __future__ import annotations

import re

LINK_PATTERN = re.compile(r"https?://[^\s]+", re.IGNORECASE)
PHONE_PATTERN = re.compile(
    r"(?:\+?63|0)?(?:9\d{9}|\d{7,15})"
)
WORD_PATTERN = re.compile(r"[A-Za-z0-9@._\-#]{3,}")
STOPWORDS = {
    "the",
    "and",
    "for",
    "your",
    "this",
    "that",
    "with",
    "from",
    "have",
    "are",
    "was",
    "you",
    "your",
    "please",
    "click",
    "here",
}


def clean_message(message: str) -> str:
    """Normalize whitespace and strip control characters."""

    return re.sub(r"\s+", " ", message.strip())


def extract_links(message: str) -> list[str]:
    """Extract HTTP/HTTPS links from an SMS message."""

    return LINK_PATTERN.findall(message)


def extract_phone_numbers(message: str) -> list[str]:
    """Extract likely phone numbers from an SMS message."""

    return PHONE_PATTERN.findall(message)


def extract_keywords(message: str) -> list[str]:
    """Extract normalized keywords from a message."""

    words = [match.group(0).lower() for match in WORD_PATTERN.finditer(message)]
    return [word for word in words if word not in STOPWORDS]

