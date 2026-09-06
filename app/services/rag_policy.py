from __future__ import annotations

import re


PUBLIC_RAG_SOURCES = frozenset(
    {
        "alerts",
        "barangays",
        "cyber_weather",
        "municipalities",
        "rag_scam_reports",
        "schools",
        "threat_patterns",
        "documents",
    }
)

_PRIVATE_QUERY_PATTERNS = (
    r"\busers?\b",
    r"\badmins?\b",
    r"\baudit logs?\b",
    r"\bnotifications?\b",
    r"\bconversations?\b",
    r"\bmessages?\b",
    r"\bemail addresses?\b",
    r"\bphone numbers?\b",
    r"\bpersonal information\b",
    r"\bprivate\b",
    r"\bpasswords?\b",
    r"\b(?:user|reporter|admin)[-_ ]?(?:id|name)\b",
)

_PII_PATTERNS = (
    (re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.I), "[REDACTED_EMAIL]"),
    (re.compile(r"(?<!\d)(?:\+?63|0)9\d{9}(?!\d)"), "[REDACTED_PHONE]"),
)


class OutOfScopeQueryError(ValueError):
    """Raised when a request targets private or administrative data."""


def validate_public_query(prompt: str) -> None:
    """Reject requests that target private records rather than public intelligence."""

    normalized = " ".join(prompt.lower().split())
    if any(re.search(pattern, normalized) for pattern in _PRIVATE_QUERY_PATTERNS):
        raise OutOfScopeQueryError(
            "I can answer about public cybersecurity intelligence in Davao del Norte, "
            "but I cannot provide personal information, private conversations, user "
            "records, notifications, or audit data."
        )


def sanitize_for_rag(value: str) -> str:
    """Remove common PII before text is sent to retrieval or an LLM."""

    sanitized = value
    for pattern, replacement in _PII_PATTERNS:
        sanitized = pattern.sub(replacement, sanitized)
    return sanitized
