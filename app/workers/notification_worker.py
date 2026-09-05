"""Notification delivery worker."""

from __future__ import annotations

from app.core.firebase import FirebaseService
from app.database.session import AsyncSessionLocal
from app.repositories.notification_repository import NotificationRepository
from app.repositories.user_repository import UserRepository


async def run_notification_job() -> dict[str, object]:
    """Attempt to resend unread notifications via Firebase."""

    async with AsyncSessionLocal() as db:
        notifications = NotificationRepository(db)
        users = UserRepository(db)
        firebase = FirebaseService()
        total_sent = 0
        all_users, _ = await users.list_users(page=1, size=1000, is_active=True)
        for user in all_users:
            unread, _ = await notifications.get_notifications(user.id, page=1, size=1000, only_unread=True)
            for notification in unread:
                firebase.send_notification(
                    token=None,
                    topic=f"user-{user.id}",
                    title=notification.title,
                    body=notification.message,
                    data={"notification_id": str(notification.id)},
                )
                total_sent += 1
        return {"sent": total_sent}

