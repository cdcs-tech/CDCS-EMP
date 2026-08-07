"""
CDCS Enterprise Management Platform (CDCS-EMP)

Enterprise Event Framework

Event Bus

Responsible for publishing events
and dispatching them to handlers.
"""


from app.core.events.registry import (
    event_registry,
)

from app.core.events.exceptions import (
    EventPublishingException,
)



class EventBus:
    """
    Central event dispatcher.
    """



    def __init__(
        self,
        registry=None,
    ):

        self.registry = (
            registry
            or event_registry
        )



    def publish(
        self,
        event,
    ):
        """
        Publish an event.

        All registered handlers
        receive the event.
        """

        try:

            event_class = type(event)


            handlers = (
                self.registry.get_handlers(
                    event_class
                )
            )


            results = []


            for handler in handlers:

                result = (
                    handler.handle(event)
                )

                results.append(
                    result
                )


            return results



        except Exception as exc:

            raise EventPublishingException(
                "Event publishing failed"
            ) from exc



    def has_handlers(
        self,
        event_class,
    ):
        """
        Check whether handlers exist.
        """

        return bool(
            self.registry.get_handlers(
                event_class
            )
        )



    def __repr__(self):

        return (
            f"<EventBus "
            f"registry={self.registry}>"
        )



event_bus = EventBus()
