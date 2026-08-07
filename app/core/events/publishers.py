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



class EventPublisher:
    """
    Standard event publishing service.
    """



    def __init__(
        self,
        bus=None,
    ):

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
