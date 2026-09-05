"""Localized keyword intelligence for scam classification."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True, frozen=True)
class KeywordProfile:
    """Keyword groups for a scam category."""

    category: str
    english: tuple[str, ...] = field(default_factory=tuple)
    tagalog: tuple[str, ...] = field(default_factory=tuple)
    cebuano: tuple[str, ...] = field(default_factory=tuple)


KEYWORD_PROFILES: tuple[KeywordProfile, ...] = (
    KeywordProfile(
        category="banking_scams",
        english=("bank", "account", "otp", "card", "wallet", "transfer", "secure"),
        tagalog=("bangko", "account", "otp", "card", "wallet", "ilipat", "segurado"),
        cebuano=("bangko", "account", "otp", "card", "wallet", "balhin", "sigurado"),
    ),
    KeywordProfile(
        category="marketplace_scams",
        english=("marketplace", "seller", "buyer", "reservation", "downpayment"),
        tagalog=("marketplace", "nagbebenta", "bumibili", "reservation", "downpayment"),
        cebuano=("marketplace", "baligya", "mamalit", "reservation", "downpayment"),
    ),
    KeywordProfile(
        category="fake_jobs",
        english=("job", "hiring", "work from home", "salary", "interview", "application"),
        tagalog=("trabaho", "hiring", "sahod", "interview", "aplikasyon"),
        cebuano=("trabaho", "hiring", "sweldo", "interview", "aplikasyon"),
    ),
    KeywordProfile(
        category="fake_investments",
        english=("investment", "roi", "profit", "guaranteed", "double your money"),
        tagalog=("invest", "kita", "garantisado", "doble", "puhunan"),
        cebuano=("invest", "kita", "sigurado", "doble", "kapital"),
    ),
    KeywordProfile(
        category="fake_delivery",
        english=("delivery", "package", "courier", "parcel", "customs"),
        tagalog=("delivery", "pakete", "kargamento", "parcel", "adwana"),
        cebuano=("delivery", "pakete", "kargamento", "parcel", "adwana"),
    ),
    KeywordProfile(
        category="fake_sim_registration",
        english=("sim registration", "register your sim", "verify sim"),
        tagalog=("rehistro ng sim", "iparehistro ang sim", "i-verify ang sim"),
        cebuano=("rehistro sa sim", "parehistro ang sim", "i-verify ang sim"),
    ),
    KeywordProfile(
        category="fake_national_id",
        english=("national id", "philid", "id verification", "identity verification"),
        tagalog=("national id", "philid", "beripikasyon ng id", "pagkakakilanlan"),
        cebuano=("national id", "philid", "beripikasyon sa id", "pagpakita sa identidad"),
    ),
)


def detect_profile(text: str) -> list[str]:
    """Return matching keyword profile categories for a text."""

    lower = text.lower()
    matches: list[str] = []
    for profile in KEYWORD_PROFILES:
        phrases = profile.english + profile.tagalog + profile.cebuano
        if any(keyword in lower for keyword in phrases):
            matches.append(profile.category)
    return matches

