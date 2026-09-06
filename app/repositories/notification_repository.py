from __future__ import annotations
from collections.abc import Mapping
from uuid import UUID
from sqlalchemy import func, select
from app.models.notification import Notification
from app.repositories.base import RepositoryBase


class NotificationRepository(RepositoryBase):
    """Database operations for notifications."""

    async def create_notification(self, notification_data: Mapping[str, object]) -> Notification:
        """Create a notification."""

        notification = Notification(**self._mapping_data(notification_data))
        self.db.add(notification)
        await self.db.commit()
        await self.db.refresh(notification)
        return notification

    async def get_notifications(
        self,
        user_id: UUID,
        *,
        page: int = 1,
        size: int = 20,
        only_unread: bool = False,
    ) -> tuple[list[Notification], int]:
        """List notifications for a user."""

        stmt = select(Notification).where(Notification.user_id == user_id)
        count_stmt = self._count_statement(Notification, Notification.user_id == user_id)
        if only_unread:
            stmt = stmt.where(Notification.is_read.is_(False))
            count_stmt = count_stmt.where(Notification.is_read.is_(False))
        stmt = stmt.order_by(Notification.created_at.desc())
        return await self._paginate(stmt, count_stmt, page=page, size=size)

    async def mark_as_read(self, notification_id: UUID) -> Notification | None:
        """Mark a notification as read."""

        result = await self.db.execute(
            select(Notification).where(Notification.id == notification_id)
        )
        notification = result.scalar_one_or_none()
        if notification is None:
            return None
        notification.is_read = True
        await self.db.commit()
        await self.db.refresh(notification)
        return notification

    async def mark_all_read(self, user_id: UUID) -> int:
        """Mark all notifications for a user as read."""

        result = await self.db.execute(
            select(Notification).where(
                Notification.user_id == user_id,
                Notification.is_read.is_(False),
            )
        )
        notifications = list(result.scalars().all())
        for notification in notifications:
            notification.is_read = True
        await self.db.commit()
        return len(notifications)

    async def unread_count(self, user_id: UUID) -> int:
        """Count unread notifications for a user."""

        stmt = select(func.count()).select_from(Notification).where(
            Notification.user_id == user_id,
            Notification.is_read.is_(False),
        )
        return int(await self.db.scalar(stmt) or 0)

