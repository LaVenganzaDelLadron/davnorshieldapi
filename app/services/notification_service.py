from __future__ import annotations
from dataclasses import dataclass
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.firebase import FirebaseService
from app.models.enums import UserRole
from app.models.notification import Notification
from app.repositories.barangay_repository import BarangayRepository
from app.repositories.municipality_repository import MunicipalityRepository
from app.repositories.notification_repository import NotificationRepository
from app.repositories.school_repository import SchoolRepository
from app.repositories.user_repository import UserRepository


@dataclass(slots=True)
class DeliveryResult:
    """Notification delivery summary."""

    recipients: int
    firebase_success: bool
    topic: str


class NotificationService:
    """Create in-app notifications and optionally deliver via Firebase."""

    def __init__(self, db: AsyncSession, firebase_service: FirebaseService | None = None) -> None:
        self.db = db
        self.notifications = NotificationRepository(db)
        self.users = UserRepository(db)
        self.barangays = BarangayRepository(db)
        self.municipalities = MunicipalityRepository(db)
        self.schools = SchoolRepository(db)
        self.firebase = firebase_service or FirebaseService()

    async def _create_user_notification(
        self,
        user_id: UUID,
        title: str,
        message: str,
        data: dict[str, str] | None = None,
        topic: str | None = None,
    ) -> Notification:
        """Persist a notification and attempt Firebase delivery."""

        notification = await self.notifications.create_notification(
            {
                "user_id": user_id,
                "title": title,
                "message": message,
                "is_read": False,
            }
        )
        self.firebase.send_notification(
            token=None,
            topic=topic or f"user-{user_id}",
            title=title,
            body=message,
            data=data or {},
        )
        return notification

    async def notify_user(
        self,
        user_id: UUID,
        title: str,
        message: str,
        *,
        data: dict[str, str] | None = None,
    ) -> Notification:
        """Notify one user."""

        return await self._create_user_notification(user_id, title, message, data=data)

    async def notify_barangay(
        self,
        barangay_id: UUID,
        title: str,
        message: str,
        *,
        data: dict[str, str] | None = None,
    ) -> DeliveryResult:
        """Notify all users assigned to a barangay."""

        users, _ = await self.users.list_users_by_barangay(barangay_id, page=1, size=500)
        for user in users:
            await self._create_user_notification(
                user.id,
                title,
                message,
                data=data,
                topic=f"barangay-{barangay_id}",
            )
        firebase_result = self.firebase.send_notification(
            token=None,
            topic=f"barangay-{barangay_id}",
            title=title,
            body=message,
            data=data or {},
        )
        return DeliveryResult(
            recipients=len(users),
            firebase_success=firebase_result.success,
            topic=f"barangay-{barangay_id}",
        )

    async def notify_municipality(
        self,
        municipality_id: UUID,
        title: str,
        message: str,
        *,
        data: dict[str, str] | None = None,
    ) -> DeliveryResult:
        """Notify all users assigned to a municipality."""

        users, _ = await self.users.list_users_by_municipality(municipality_id, page=1, size=1000)
        for user in users:
            await self._create_user_notification(
                user.id,
                title,
                message,
                data=data,
                topic=f"municipality-{municipality_id}",
            )
        firebase_result = self.firebase.send_notification(
            token=None,
            topic=f"municipality-{municipality_id}",
            title=title,
            body=message,
            data=data or {},
        )
        return DeliveryResult(
            recipients=len(users),
            firebase_success=firebase_result.success,
            topic=f"municipality-{municipality_id}",
        )

    async def notify_school(
        self,
        school_id: UUID,
        title: str,
        message: str,
        *,
        data: dict[str, str] | None = None,
    ) -> DeliveryResult:
        """Notify school administrators for a school's municipality."""

        school = await self.schools.get_school(school_id)
        if school is None:
            return DeliveryResult(recipients=0, firebase_success=False, topic=f"school-{school_id}")
        users, _ = await self.users.list_users_by_municipality(school.municipality_id, page=1, size=1000)
        school_admins = [user for user in users if user.role == UserRole.school_admin]
        for user in school_admins:
            await self._create_user_notification(
                user.id,
                title,
                message,
                data=data,
                topic=f"school-{school_id}",
            )
        firebase_result = self.firebase.send_notification(
            token=None,
            topic=f"school-{school_id}",
            title=title,
            body=message,
            data=data or {},
        )
        return DeliveryResult(
            recipients=len(school_admins),
            firebase_success=firebase_result.success,
            topic=f"school-{school_id}",
        )

    async def broadcast_outbreak(
        self,
        *,
        title: str,
        message: str,
        municipality_id: UUID | None = None,
        barangay_id: UUID | None = None,
        data: dict[str, str] | None = None,
    ) -> DeliveryResult:
        """Broadcast an outbreak alert to the relevant scope."""

        if barangay_id is not None:
            return await self.notify_barangay(barangay_id, title, message, data=data)
        if municipality_id is not None:
            return await self.notify_municipality(municipality_id, title, message, data=data)
        return DeliveryResult(recipients=0, firebase_success=False, topic="outbreak-global")
