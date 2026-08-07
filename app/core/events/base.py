"""
CDCS Enterprise Management Platform (CDCS-EMP)

Enterprise Event Framework

Base Event Definition

Provides the standard contract for
all domain events within CDCS-EMP.
"""


from abc import ABC, abstractmethod

from datetime import datetime, timezone

from uuid import uuid4



class BaseEvent(ABC):
    """
    Abstract base class for enterprise events.
    """



    def __init__(self):
        """
        Initialize event metadata.
        """

        self.event_id = str(uuid4())

        self.created_at = datetime.now(
            timezone.utc
        )



    @property
    @abstractmethod
    def event_name(self) -> str:
        """
        Return unique event name.

        Every event must implement this.
        """

        raise NotImplementedError



    def metadata(self):
        """
        Return event metadata.

        Used by:
        - Event Bus
        - Audit System
        - Logging
        """

        return {
            "event_id": self.event_id,
            "event_name": self.event_name,
            "created_at": self.created_at,
        }



    def __repr__(self):
        """
        Developer-friendly representation.
        """

        return (
            f"<Event "
            f"{self.event_name} "
            f"{self.event_id}>"
        )
