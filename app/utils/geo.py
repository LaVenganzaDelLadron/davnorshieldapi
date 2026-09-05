"""Geographic normalization helpers for Davao del Norte."""

from __future__ import annotations

from app.utils.constants import DAVAO_DEL_NORTE_MUNICIPALITIES

_MUNICIPALITY_ALIASES = {
    "igacos": "island garden city of samal",
    "island garden city of samal": "island garden city of samal",
    "samal": "island garden city of samal",
    "tagum": "tagum city",
    "tagum city": "tagum city",
    "braulio e dujali": "braulio e. dujali",
    "braulio e. dujali": "braulio e. dujali",
    "sto tomas": "santo tomas",
    "santo tomas": "santo tomas",
    "new corella": "new corella",
    "kapalong": "kapalong",
    "carmen": "carmen",
    "san isidro": "san isidro",
    "talaingod": "talaingod",
}


def normalize_barangay_name(name: str) -> str:
    """Normalize a barangay name for comparison."""

    return " ".join(name.strip().lower().split())


def normalize_municipality_name(name: str) -> str:
    """Normalize a municipality name for comparison."""

    normalized = " ".join(name.strip().lower().split())
    return _MUNICIPALITY_ALIASES.get(normalized, normalized)


def get_municipality_from_barangay(barangay_name: str) -> str | None:
    """Return the municipality name that commonly contains the barangay."""

    normalized_barangay = normalize_barangay_name(barangay_name)
    for municipality, barangays in DAVAO_DEL_NORTE_MUNICIPALITIES.items():
        if normalized_barangay in barangays:
            return municipality
    return None
