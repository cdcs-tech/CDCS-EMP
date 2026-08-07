"""
CDCS Enterprise Management Platform (CDCS-EMP)

Enterprise Event Framework

Event Metadata Definition

Provides the standard metadata contract
for all enterprise events.
"""

from dataclasses import dataclass, field

from datetime import datetime, timezone

from uuid import uuid4


@dataclass
class EventMetadata:
    """
    Standard metadata attached to enterprise events.
    """

    event_name: str

    version: str = "1.0"

    source: str = "CDCS-EMP"

    event_id: str = field(
        default_factory=lambda: str(uuid4())
    )

    timestamp: datetime = field(
        default_factory=lambda: datetime.now(
            timezone.utc
        )
    )

    correlation_id: str = field(
        default_factory=lambda: str(uuid4())
    )

    user_id: str | None = None

    tenant_id: str | None = None


    def validate(self):
        """
        Validate event metadata.
        """

        if not self.event_name:
            raise ValueError(
                "Event name is required."
            )

        if not self.version:
            raise ValueError(
                "Event version is required."
            )

        if not self.source:
            raise ValueError(
                "Event source is required."
            )

        return True


    def to_dict(self):
        """
        Convert metadata into dictionary form.
        """

        return {
            "event_id": self.event_id,
            "event_name": self.event_name,
            "version": self.version,
            "source": self.source,
            "timestamp": self.timestamp,
            "correlation_id": self.correlation_id,
            "user_id": self.user_id,
            "tenant_id": self.tenant_id,
        }

