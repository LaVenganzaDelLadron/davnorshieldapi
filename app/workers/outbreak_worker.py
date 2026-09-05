"""Outbreak detection worker."""

from __future__ import annotations

from app.constants import AlertLevel
from app.database.session import AsyncSessionLocal
from app.repositories.barangay_repository import BarangayRepository
from app.repositories.municipality_repository import MunicipalityRepository
from app.services.alert_service import AlertService
from app.services.notification_service import NotificationService
from app.services.outbreak_service import OutbreakService
from app.repositories.threat_repository import ThreatRepository


async def run_outbreak_job() -> dict[str, object]:
    """Detect outbreaks and create/broadcast alerts."""

    async with AsyncSessionLocal() as db:
        municipalities = await MunicipalityRepository(db).list_municipalities()
        barangays = await BarangayRepository(db).list_barangays()
        outbreaks = OutbreakService(db)
        alerts = AlertService(db)
        threats = ThreatRepository(db)
        broadcasted = 0

        top_patterns = await threats.top_patterns(limit=1)
        top_pattern = top_patterns[0] if top_patterns else None
        if top_pattern is None:
            return {"processed": 0, "broadcasted": 0}

        for municipality in municipalities:
            metadata = await outbreaks.calculate_municipality_outbreak(municipality.id)
            if metadata.detected:
                await alerts.broadcast_alert(
                    threat_pattern_id=top_pattern.id,
                    municipality_id=municipality.id,
                    barangay_id=None,
                    alert_level=AlertLevel.CRITICAL if metadata.severity == "critical" else AlertLevel.HIGH,
                    title="Cyber threat outbreak detected",
                    message=metadata.message,
                )
                broadcasted += 1

        for barangay in barangays:
            metadata = await outbreaks.calculate_barangay_outbreak(barangay.id)
            if metadata.detected:
                await alerts.broadcast_alert(
                    threat_pattern_id=top_pattern.id,
                    municipality_id=barangay.municipality_id,
                    barangay_id=barangay.id,
                    alert_level=AlertLevel.CRITICAL if metadata.severity == "critical" else AlertLevel.HIGH,
                    title="Barangay cyber threat outbreak detected",
                    message=metadata.message,
                )
                broadcasted += 1

        return {"processed": len(municipalities) + len(barangays), "broadcasted": broadcasted}
