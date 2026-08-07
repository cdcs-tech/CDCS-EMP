"""
CDCS Enterprise Management Platform (CDCS-EMP)

Enterprise Event Framework

Event Publisher Foundation

Provides a standard interface for
publishing enterprise events.
"""


from app.core.events.bus import (
    event_bus,
)


from app.core.events.validator import (
    event_validator,
)


class EventPublisher:
    """
    Standard event publishing service.
    """



    def __init__(
        self,
        bus=None,
        validator=None,
):

        self.bus = (
          bus
          or event_bus
    )

        self.validator = (
        validator
        or event_validator
    )

        self.bus = (
            bus
            or event_bus
        )



    def publish(
        self,
        event,
    ):
        """
        Publish an event through
        the enterprise event bus.
        """

        self.validator.validate(
            event
)

        return self.bus.publish(
            event
)



    def publish_many(
        self,
        events,
    ):
        """
        Publish multiple events.
        """

        results = []


        for event in events:

            results.append(
                self.publish(event)
            )


        return results



    def __repr__(self):

        return (
            f"<EventPublisher "
            f"bus={self.bus}>"
        )



event_publisher = EventPublisher()
