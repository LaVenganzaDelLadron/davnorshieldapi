"""URL parsing and normalization helpers."""

from __future__ import annotations

import ipaddress
from urllib.parse import parse_qsl, urlencode, urlparse, urlunparse

TRACKING_PARAMETERS = {
    "fbclid",
    "gclid",
    "igshid",
    "mc_cid",
    "mc_eid",
    "ref",
    "ref_src",
    "utm_campaign",
    "utm_content",
    "utm_medium",
    "utm_source",
    "utm_term",
}


def normalize_url(url: str) -> str:
    """Normalize a URL to make comparisons more stable."""

    raw = url.strip()
    parsed = urlparse(raw if "://" in raw else f"https://{raw}")
    scheme = (parsed.scheme or "https").lower()
    netloc = parsed.netloc.lower()
    path = parsed.path.rstrip("/") or "/"
    filtered_query = [
        (key, value)
        for key, value in parse_qsl(parsed.query, keep_blank_values=True)
        if key not in TRACKING_PARAMETERS
    ]
    return urlunparse((scheme, netloc, path, "", urlencode(filtered_query), ""))


def extract_domain(url: str) -> str:
    """Extract the registered host portion from a URL."""

    raw = url.strip()
    parsed = urlparse(raw if "://" in raw else f"https://{raw}")
    host = parsed.netloc.lower() or parsed.path.lower()
    return host.split(":")[0]


def remove_tracking_parameters(url: str) -> str:
    """Remove common tracking query parameters from a URL."""

    raw = url.strip()
    parsed = urlparse(raw if "://" in raw else f"https://{raw}")
    filtered_query = [
        (key, value)
        for key, value in parse_qsl(parsed.query, keep_blank_values=True)
        if key not in TRACKING_PARAMETERS
    ]
    return urlunparse(
        (
            parsed.scheme,
            parsed.netloc,
            parsed.path,
            parsed.params,
            urlencode(filtered_query),
            parsed.fragment,
        )
    )


def is_ip_address_url(url: str) -> bool:
    """Return True when the URL host is an IP address."""

    host = extract_domain(url)
    try:
        ipaddress.ip_address(host)
        return True
    except ValueError:
        return False
