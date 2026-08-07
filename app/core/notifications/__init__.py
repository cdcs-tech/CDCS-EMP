"""
CDCS Enterprise Management Platform (CDCS-EMP)

Enterprise Notification Framework

Public package interface.
"""

from app.core.notifications.base import (
    BaseNotification,
)

from app.core.notifications.exceptions import (
    NotificationException,
    NotificationRegistrationException,
    NotificationDeliveryException,
)

from app.core.notifications.registry import (
    NotificationRegistry,
    notification_registry,
)

from app.core.notifications.service import (
    NotificationService,
    notification_service,
)


__all__ = [
    "BaseNotification",
    "NotificationException",
    "NotificationRegistrationException",
    "NotificationDeliveryException",
    "NotificationRegistry",
    "notification_registry",
    "NotificationService",
    "notification_service",
]

