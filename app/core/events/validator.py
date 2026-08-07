"""
CDCS Enterprise Management Platform (CDCS-EMP)

Enterprise Event Framework

Event Validation Framework

Validates enterprise events before
they enter the event bus.
"""

from app.core.events.base import (
    BaseEvent,
)


class EventValidator:
    """
    Validates enterprise event contracts.
    """

    REQUIRED_METADATA_FIELDS = [
        "event_id",
        "event_name",
        "version",
        "source",
        "timestamp",
        "correlation_id",
    ]


    def validate(self, event):
        """
        Validate an enterprise event.

        Raises:
            ValueError:
                When event contract is invalid.
        """

        self.validate_type(
            event
        )

        self.validate_identity(
            event
        )

        self.validate_metadata(
            event
        )

        return True


    def validate_type(self, event):
        """
        Validate event type.
        """

        if not isinstance(
            event,
            BaseEvent,
        ):
            raise ValueError(
                "Invalid event type."
            )


    def validate_identity(self, event):
        """
        Validate event identity.
        """

        if not event.event_name:

            raise ValueError(
                "Event name is required."
            )


        if not event.version:

            raise ValueError(
                "Event version is required."
            )


        if not event.source:

            raise ValueError(
                "Event source is required."
            )


    def validate_metadata(self, event):
        """
        Validate metadata structure.
        """

        metadata = (
            event.metadata()
        )


        for field in (
            self.REQUIRED_METADATA_FIELDS
        ):

            if field not in metadata:

                raise ValueError(
                    f"Missing event metadata: {field}"
                )


        return True


    def __repr__(self):

        return (
            "<EventValidator>"
        )


event_validator = EventValidator()

