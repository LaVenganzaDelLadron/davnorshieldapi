"""URL parsing and normalization helpers."""

from __future__ import annotations

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

    parsed = urlparse(url.strip())
    scheme = parsed.scheme.lower()
    netloc = parsed.netloc.lower()
    path = parsed.path.rstrip("/") or "/"
    query = remove_tracking_parameters(url)
    query_string = urlparse(query).query
    normalized = urlunparse((scheme, netloc, path, "", query_string, ""))
    return normalized


def extract_domain(url: str) -> str:
    """Extract the registered host portion from a URL."""

    parsed = urlparse(url.strip())
    host = parsed.netloc.lower()
    return host.split(":")[0]


def remove_tracking_parameters(url: str) -> str:
    """Remove common tracking query parameters from a URL."""

    parsed = urlparse(url.strip())
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
    parts = host.split(".")
    if len(parts) == 4 and all(part.isdigit() for part in parts):
        return all(0 <= int(part) <= 255 for part in parts)
    return False

