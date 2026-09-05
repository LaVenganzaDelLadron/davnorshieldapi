"""File upload helpers for report screenshots."""

from __future__ import annotations

from pathlib import Path
from uuid import uuid4

from app.config import settings
from app.utils.constants import ALLOWED_IMAGE_EXTENSIONS


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
    return None


def save_report_image(
    file_bytes: bytes,
    original_filename: str,
    upload_dir: str | Path | None = None,
) -> Path:
    """Persist an uploaded report image to disk after validation."""

    max_size = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024
    if len(file_bytes) > max_size:
        raise ValueError(f"File exceeds the {settings.MAX_UPLOAD_SIZE_MB} MB limit.")

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
    destination_dir = Path(upload_dir or settings.REPORT_IMAGE_DIR)
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
