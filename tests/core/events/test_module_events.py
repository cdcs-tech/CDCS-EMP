"""
CDCS Enterprise Management Platform (CDCS-EMP)

Module Event Registration and Publication Tests

Verifies integration between the enterprise
module framework, event registry, event bus,
and event publisher.
"""

from app.core.events import (
    BaseEvent,
    BaseEventHandler,
    event_registry,
    event_bus,
    event_publisher,
)

from app.core.modules.base import (
    BaseModule,
)

from app.core.modules.metadata import (
    ModuleMetadata,
)


class TestModuleEvent(BaseEvent):
    """
    Test event used to verify event integration.
    """

    @property
    def event_name(self):
        """
        Return test event name.
        """

        return "test.module.event"


class TestModuleEventHandler(BaseEventHandler):
    """
    Test handler used to verify event processing.
    """

    def __init__(self):
        self.handled_events = []

    def handle(self, event):
        """
        Record the event handled.
        """

        self.handled_events.append(
            event
        )

        return True


class TestEventModule(BaseModule):
    """
    Test module exposing an event
    and its event handler.
    """

    def get_metadata(self) -> ModuleMetadata:
        """
        Return test module metadata.
        """

        return ModuleMetadata(
            code="test_event_module",
            name="Test Event Module",
            description="Test module for event integration.",
            version="1.0.0",
            active=True,
        )

    def get_events(self):
        """
        Return test module events.
        """

        return [
            TestModuleEvent,
        ]

    def get_event_handlers(self):
        """
        Return test module event handlers.
        """

        return [
            (
                TestModuleEvent,
                TestModuleEventHandler(),
            ),
        ]


def test_module_event_registration():
    """
    Verify module event registration.
    """

    event_registry.clear()

    module = TestEventModule()

    assert module.has_events() is True

    module.initialize(None)

    registered_event = (
        event_registry.get_event(
            "test.module.event"
        )
    )

    assert registered_event is TestModuleEvent

    event_registry.clear()


def test_module_event_handler_registration():
    """
    Verify module event handler registration.
    """

    event_registry.clear()

    module = TestEventModule()

    assert module.has_event_handlers() is True

    module.initialize(None)

    handlers = (
        event_registry.get_handlers(
            TestModuleEvent
        )
    )

    assert len(handlers) == 1

    assert isinstance(
        handlers[0],
        TestModuleEventHandler,
    )

    event_registry.clear()


def test_event_publication_end_to_end():
    """
    Verify complete event publication flow.

    Module
        ↓
    Event Registry
        ↓
    Event Publisher
        ↓
    Event Bus
        ↓
    Event Handler
    """

    event_registry.clear()

    module = TestEventModule()

    module.initialize(None)

    handlers = (
        event_registry.get_handlers(
            TestModuleEvent
        )
    )

    assert len(handlers) == 1

    handler = handlers[0]

    event = TestModuleEvent()

    results = (
        event_publisher.publish(
            event
        )
    )

    assert results == [True]

    assert len(
        handler.handled_events
    ) == 1

    assert (
        handler.handled_events[0]
        is event
    )

    event_registry.clear()

