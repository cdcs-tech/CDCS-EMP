"""
CDCS Enterprise Management Platform (CDCS-EMP)

Enterprise Notification Framework

Base Notification Definition

Provides the standard contract for
all enterprise notifications.
"""

from abc import ABC, abstractmethod

from datetime import datetime, timezone

from uuid import uuid4


class BaseNotification(ABC):
    """
    Abstract base class for enterprise
    notifications.
    """

    def __init__(
        self,
        recipient,
        title="",
        message="",
        metadata=None,
    ):
        """
        Initialize notification.
        """

        self.notification_id = str(
            uuid4()
        )

        self.recipient = recipient

        self.title = title

        self.message = message

        self.metadata = (
            metadata
            if metadata is not None
            else {}
        )

        self.created_at = (
            datetime.now(
                timezone.utc
            )
        )


    @property
    @abstractmethod
    def notification_type(self) -> str:
        """
        Return unique notification type.

        Every notification must implement
        this property.
        """

        raise NotImplementedError


    def validate(self):
        """
        Validate notification contract.
        """

        if not self.recipient:

            raise ValueError(
                "Notification recipient "
                "is required."
            )


        if not self.title:

            raise ValueError(
                "Notification title "
                "is required."
            )


        if not self.message:

            raise ValueError(
                "Notification message "
                "is required."
            )


        return True


    def metadata_dict(self):
        """
        Return standard notification metadata.
        """

        return {
            "notification_id": (
                self.notification_id
            ),
            "notification_type": (
                self.notification_type
            ),
            "recipient": (
                self.recipient
            ),
            "created_at": (
                self.created_at
            ),
            **self.metadata,
        }


    def __repr__(self):

        return (
            f"<Notification "
            f"{self.notification_type} "
            f"{self.notification_id}>"
        )

