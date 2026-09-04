"""Firebase notification helpers."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from app.core.config import settings

try:  # pragma: no cover - optional dependency
    import firebase_admin
    from firebase_admin import credentials, messaging
except Exception:  # noqa: BLE001
    firebase_admin = None
    credentials = None
    messaging = None


@dataclass(slots=True)
class FirebaseMessageResult:
    """Result from a Firebase delivery attempt."""

    success: bool
    message_id: str | None = None
    error: str | None = None


class FirebaseService:
    """Lightweight Firebase Cloud Messaging wrapper."""

    def __init__(self) -> None:
        self.project_id = settings.FIREBASE_PROJECT_ID
        self._initialized = False
        if firebase_admin is not None and self.project_id:
            self._initialize_app()

    def _initialize_app(self) -> None:
        if self._initialized or firebase_admin is None:
            return
        if not firebase_admin._apps:  # type: ignore[attr-defined]
            firebase_admin.initialize_app()  # pragma: no cover - external integration
        self._initialized = True

    def send_notification(
        self,
        *,
        token: str | None,
        topic: str | None = None,
        title: str,
        body: str,
        data: dict[str, str] | None = None,
    ) -> FirebaseMessageResult:
        """Send a push notification or return a local fallback result."""

        if firebase_admin is None or messaging is None or (token is None and topic is None):
            return FirebaseMessageResult(success=False, error="Firebase not configured.")

        message_kwargs: dict[str, Any] = {
            "notification": messaging.Notification(title=title, body=body),
            "data": data or {},
        }
        if token is not None:
            message_kwargs["token"] = token
        if topic is not None:
            message_kwargs["topic"] = topic
        message = messaging.Message(**message_kwargs)
        try:
            message_id = messaging.send(message)
            return FirebaseMessageResult(success=True, message_id=message_id)
        except Exception as exc:  # noqa: BLE001
            return FirebaseMessageResult(success=False, error=str(exc))
