"""Central APScheduler configuration."""

from __future__ import annotations

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.config import settings
from app.workers.analytics_worker import run_analytics_job
from app.workers.cleanup_worker import run_cleanup_job
from app.workers.cyber_weather_worker import run_cyber_weather_job
from app.workers.notification_worker import run_notification_job
from app.workers.outbreak_worker import run_outbreak_job

scheduler = AsyncIOScheduler(timezone=settings.SCHEDULER_TIMEZONE)


def register_jobs() -> None:
    """Register all scheduled background jobs."""

    scheduler.add_job(
        run_cyber_weather_job,
        trigger="interval",
        hours=settings.WEATHER_INTERVAL_HOURS,
        id="cyber_weather_job",
        replace_existing=True,
        max_instances=1,
        coalesce=True,
    )
    scheduler.add_job(
        run_outbreak_job,
        trigger="interval",
        minutes=settings.OUTBREAK_INTERVAL_MINUTES,
        id="outbreak_job",
        replace_existing=True,
        max_instances=1,
        coalesce=True,
    )
    scheduler.add_job(
        run_notification_job,
        trigger="interval",
        seconds=settings.NOTIFICATION_INTERVAL_SECONDS,
        id="notification_job",
        replace_existing=True,
        max_instances=1,
        coalesce=True,
    )
    scheduler.add_job(
        run_cleanup_job,
        trigger="cron",
        hour=settings.CLEANUP_CRON_HOUR,
        id="cleanup_job",
        replace_existing=True,
        max_instances=1,
        coalesce=True,
    )
    scheduler.add_job(
        run_analytics_job,
        trigger="interval",
        seconds=settings.ANALYTICS_INTERVAL_SECONDS,
        id="analytics_job",
        replace_existing=True,
        max_instances=1,
        coalesce=True,
    )


def start_scheduler() -> None:
    """Start the background scheduler if enabled."""

    if not settings.SCHEDULER_ENABLED:
        return
    if not scheduler.running:
        register_jobs()
        scheduler.start()


def shutdown_scheduler() -> None:
    """Stop the scheduler gracefully."""

    if scheduler.running:
        scheduler.shutdown(wait=False)
