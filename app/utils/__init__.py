"""Reusable helper utilities for the CyberShield DN backend."""

from app.utils.constants import (
    ALLOWED_IMAGE_EXTENSIONS,
    DAVAO_DEL_NORTE_MUNICIPALITIES,
    DEFAULT_OUTBREAK_THRESHOLD,
    DEFAULT_PAGE_SIZE,
    MAX_PAGE_SIZE,
    OUTBREAK_WINDOW_HOURS,
    AlertLevel,
    ReportStatus,
    ThreatCategory,
)
from app.utils.date_utils import format_timestamp, today_date, utc_now, within_last_24_hours
from app.utils.file_upload import delete_image, generate_unique_filename, save_report_image
from app.utils.geo import (
    get_municipality_from_barangay,
    normalize_barangay_name,
    normalize_municipality_name,
)
from app.utils.qr_parser import classify_qr_type, decode_qr_text, extract_destination
from app.utils.recommendation import get_recommendations_for_category
from app.utils.risk_calculator import calculate_confidence_score, calculate_risk_score
from app.utils.sms_parser import clean_message, extract_keywords, extract_links, extract_phone_numbers
from app.utils.url_parser import (
    extract_domain,
    is_ip_address_url,
    normalize_url,
    remove_tracking_parameters,
)
from app.utils.validator import (
    is_valid_ip_address,
    validate_email,
    validate_phone_number,
    validate_qr_data,
    validate_url,
)
