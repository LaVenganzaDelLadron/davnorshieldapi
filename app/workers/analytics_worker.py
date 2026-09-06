from __future__ import annotations

from app.database.session import AsyncSessionLocal
from app.services.dashboard_service import DashboardService

ANALYTICS_CACHE: dict[str, object] = {}


async def run_analytics_job() -> dict[str, object]:
    """Compute dashboard analytics and cache the result in memory."""

    async with AsyncSessionLocal() as db:
        analytics = await DashboardService(db).generate_dashboard()
        ANALYTICS_CACHE.clear()
        ANALYTICS_CACHE.update(analytics)
        return analytics

