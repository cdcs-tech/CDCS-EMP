"""
CDCS Enterprise Management Platform (CDCS-EMP)

Enterprise Event Framework

Base Event Definition

Provides the standard contract for
all domain events within CDCS-EMP.
"""

from abc import ABC, abstractmethod

from app.core.events.metadata import (
    EventMetadata,
)


class BaseEvent(ABC):
    """
    Abstract base class for enterprise events.
    """

    event_version = "1.0"

    event_source = "CDCS-EMP"


    def __init__(self):
        """
        Initialize event metadata.
        """

        self._metadata = EventMetadata(
            event_name=self.event_name,
            version=self.event_version,
            source=self.event_source,
        )


        # Backward compatibility
        self.event_id = (
            self._metadata.event_id
        )

        self.created_at = (
            self._metadata.timestamp
        )


    @property
    @abstractmethod
    def event_name(self) -> str:
        """
        Return unique event name.

        Every event must implement this.
        """

        raise NotImplementedError


    @property
    def version(self):
        """
        Return event version.
        """

        return self.event_version


    @property
    def source(self):
        """
        Return event source.
        """

        return self.event_source


    def metadata(self):
        """
        Return enterprise event metadata.

        Used by:
        - Event Bus
        - Audit System
        - Logging
        - Integrations
        """

        return self._metadata.to_dict()


    def __repr__(self):
        """
        Developer-friendly representation.
        """

        return (
            f"<Event "
            f"{self.event_name} "
            f"v{self.version} "
            f"{self.event_id}>"
        )

