"""File upload helpers for report screenshots."""

from __future__ import annotations

import imghdr
from pathlib import Path
from uuid import uuid4

from app.utils.constants import ALLOWED_IMAGE_EXTENSIONS, MAX_UPLOAD_SIZE_BYTES


def generate_unique_filename(original_filename: str) -> str:
    """Generate a collision-resistant file name while preserving extension."""

    suffix = Path(original_filename).suffix.lower()
    if suffix not in ALLOWED_IMAGE_EXTENSIONS:
        raise ValueError("Unsupported image format.")
    return f"{uuid4().hex}{suffix}"


def _detect_image_extension(file_bytes: bytes) -> str | None:
    """Detect a supported image type from raw bytes."""

    if file_bytes.startswith(b"\x89PNG\r\n\x1a\n"):
        return ".png"
    if file_bytes.startswith((b"\xff\xd8\xff",)):
        return ".jpg"
    if file_bytes[0:4] == b"RIFF" and file_bytes[8:12] == b"WEBP":
        return ".webp"
    detected = imghdr.what(None, h=file_bytes)
    if detected == "jpeg":
        return ".jpg"
    if detected == "png":
        return ".png"
    if detected == "webp":
        return ".webp"
    return None


def save_report_image(
    file_bytes: bytes,
    original_filename: str,
    upload_dir: str | Path = "uploads/reports",
) -> Path:
    """Persist an uploaded report image to disk after validation."""

    if len(file_bytes) > MAX_UPLOAD_SIZE_BYTES:
        raise ValueError("File exceeds the 10 MB limit.")

    filename = generate_unique_filename(original_filename)
    suffix = Path(filename).suffix.lower()
    detected_suffix = _detect_image_extension(file_bytes)
    if detected_suffix is None:
        raise ValueError("Unsupported image format.")
    if detected_suffix not in ALLOWED_IMAGE_EXTENSIONS:
        raise ValueError("Unsupported image format.")
    allowed_suffixes = {suffix}
    if suffix == ".jpeg":
        allowed_suffixes.add(".jpg")
    if suffix == ".jpg":
        allowed_suffixes.add(".jpeg")
    if detected_suffix not in allowed_suffixes:
        # Preserve the requested extension but reject mismatched payloads.
        raise ValueError("Image extension does not match file contents.")
    destination_dir = Path(upload_dir)
    destination_dir.mkdir(parents=True, exist_ok=True)
    destination_path = destination_dir / filename
    destination_path.write_bytes(file_bytes)
    return destination_path


def delete_image(image_path: str | Path) -> bool:
    """Delete an image file if it exists."""

    path = Path(image_path)
    if path.exists():
        path.unlink()
        return True
    return False
