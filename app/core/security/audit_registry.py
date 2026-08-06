"""
CDCS Enterprise Management Platform (CDCS-EMP)

Enterprise Security Framework

Security audit event registry.
"""


from typing import List, Optional


from app.core.security.audit import (
    SecurityAuditEvent,
)



class AuditRegistry:
    """
    Central registry for security audit events.
    """



    def __init__(self):
        """
        Initialize audit storage.
        """

        self._events: List[
            SecurityAuditEvent
        ] = []



    def record(
        self,
        event: SecurityAuditEvent,
    ):
        """
        Store security audit event.
        """

        if not isinstance(
            event,
            SecurityAuditEvent,
        ):
            raise TypeError(
                "Only SecurityAuditEvent objects can be recorded."
            )


        self._events.append(
            event
        )



    def all(self) -> List[SecurityAuditEvent]:
        """
        Return all audit events.
        """

        return list(
            self._events
        )



    def filter(
        self,
        event_type: Optional[str] = None,
        subject: Optional[str] = None,
        result: Optional[str] = None,
    ) -> List[SecurityAuditEvent]:
        """
        Filter audit events.
        """

        events = self._events


        if event_type:

            events = [
                event
                for event
                in events
                if event.event_type
                == event_type
            ]


        if subject:

            events = [
                event
                for event
                in events
                if event.subject
                == subject
            ]


        if result:

            events = [
                event
                for event
                in events
                if event.result.upper()
                == result.upper()
            ]


        return events



    def latest(
        self,
    ) -> SecurityAuditEvent | None:
        """
        Return latest audit event.
        """

        if not self._events:

            return None


        return self._events[-1]



    def count(self) -> int:
        """
        Return event count.
        """

        return len(
            self._events
        )



    def clear(self):
        """
        Remove all audit events.
        """

        self._events.clear()



    def __repr__(self):
        """
        Developer-friendly representation.
        """

        return (
            f"<AuditRegistry "
            f"{self.count()} events>"
        )



# Global audit registry instance

audit_registry = AuditRegistry()
