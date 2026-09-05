"""AI threat intelligence engine."""

from app.ai.classifier import ThreatClassification, classify_threat
from app.ai.cyber_weather_engine import CyberWeatherAnalysis, generate_cyber_weather
from app.ai.keyword_model import KEYWORD_PROFILES, KeywordProfile, detect_profile
from app.ai.outbreak_detector import OutbreakResult, detect_outbreak
from app.ai.pattern_engine import PatternCluster, PatternComparison, cluster_reports, compare_reports
from app.ai.phishing_detector import detect_phishing
from app.ai.qr_detector import analyze_qr, detect_qr_threat
from app.ai.recommendation_engine import generate_recommendations
from app.ai.reputation_engine import ReputationEngine, ReputationRecord
from app.ai.sms_detector import detect_sms_scam
