"""File upload helpers for report screenshots."""

from __future__ import annotations

from pathlib import Path
from uuid import uuid4

from app.utils.constants import ALLOWED_IMAGE_EXTENSIONS, MAX_UPLOAD_SIZE_BYTES


def generate_unique_filename(original_filename: str) -> str:
    """Generate a collision-resistant file name while preserving extension."""

    suffix = Path(original_filename).suffix.lower()
    if suffix not in ALLOWED_IMAGE_EXTENSIONS:
        raise ValueError("Unsupported image format.")
    return f"{uuid4().hex}{suffix}"


def save_report_image(
    file_bytes: bytes,
    original_filename: str,
    upload_dir: str | Path = "uploads/reports",
) -> Path:
    """Persist an uploaded report image to disk after validation."""

    if len(file_bytes) > MAX_UPLOAD_SIZE_BYTES:
        raise ValueError("File exceeds the 10 MB limit.")

    filename = generate_unique_filename(original_filename)
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

