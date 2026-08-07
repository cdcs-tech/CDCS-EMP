"""
CDCS Enterprise Management Platform (CDCS-EMP)

Enterprise Event Framework

Event Audit Handler

Bridges enterprise events with
the Security Audit Framework.
"""

from app.core.events.handlers import (
    BaseEventHandler,
)

from app.core.security.audit import (
    SecurityAuditEvent,
)

from app.core.security.audit_registry import (
    audit_registry,
)


class EventAuditHandler(BaseEventHandler):
    """
    Converts enterprise events into
    security audit records.
    """


    def handle(self, event):
        """
        Create and store audit event.
        """

        audit_event = SecurityAuditEvent(
            event_type=event.event_name,

            action="EVENT_PUBLISHED",

            result="SUCCESS",

            message=(
                f"Enterprise event published: "
                f"{event.event_name}"
            ),

            metadata=(
                event.metadata()
            ),
        )


        audit_registry.record(
            audit_event
        )


        return True


    def __repr__(self):

        return (
            "<EventAuditHandler>"
        )

