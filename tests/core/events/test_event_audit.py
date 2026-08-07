"""
CDCS-EMP Event Audit Integration Test
"""

from app.core.events import (
    BaseEvent,
    EventAuditHandler,
)

from app.core.security.audit_registry import (
    audit_registry,
)


class AuditTestEvent(BaseEvent):

    @property
    def event_name(self):

        return "test.audit.event"



def test_event_creates_audit_record():

    audit_registry.clear()

    handler = EventAuditHandler()

    event = AuditTestEvent()

    result = handler.handle(
        event
    )

    assert result is True

    assert (
        audit_registry.count()
        == 1
    )

    audit = (
        audit_registry.latest()
    )

    assert (
        audit.event_type
        == "test.audit.event"
    )

    assert (
        audit.action
        == "EVENT_PUBLISHED"
    )

    assert (
        audit.metadata["event_id"]
        == event.event_id
    )

    audit_registry.clear()

