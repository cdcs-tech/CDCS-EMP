"""
CDCS Enterprise Management Platform (CDCS-EMP)

Enterprise Event Framework

Event Registry

Maintains registered events and handlers.
"""


from app.core.events.exceptions import (
    EventRegistrationException,
)



class EventRegistry:
    """
    Central registry for events and handlers.
    """



    def __init__(self):

        self._events = {}

        self._handlers = {}



    def register(self, event_class):
        """
        Register an event type.
        """

        try:

            event_name = event_class().event_name

        except Exception as exc:

            raise EventRegistrationException(
                "Invalid event definition"
            ) from exc



        self._events[event_name] = event_class



    def get_event(self, event_name):
        """
        Retrieve event class.
        """

        return self._events.get(
            event_name
        )



    def register_handler(
        self,
        event_class,
        handler,
    ):
        """
        Register handler for an event.
        """

        if event_class not in self._handlers:

            self._handlers[event_class] = []



        self._handlers[event_class].append(
            handler
        )



    def get_handlers(
        self,
        event_class,
    ):
        """
        Return handlers attached
        to an event.
        """

        return self._handlers.get(
            event_class,
            []
        )



    def all_events(self):
        """
        Return registered events.
        """

        return self._events



    def clear(self):
        """
        Clear registry.

        Used mainly for testing.
        """

        self._events.clear()

        self._handlers.clear()



    def __repr__(self):

        return (
            f"<EventRegistry "
            f"events={len(self._events)} "
            f"handlers={len(self._handlers)}>"
        )



event_registry = EventRegistry()
