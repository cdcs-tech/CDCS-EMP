"""
CDCS Enterprise Management Platform (CDCS-EMP)

Reporting & Analytics Framework

Reporting audit integration boundary.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from app.core.security.audit import (
    SecurityAuditEvent,
)
from app.core.security.audit_registry import (
    AuditRegistry,
)


@dataclass
class ReportAuditEvent:
    """
    Provider-neutral reporting audit event.

    This contract represents an auditable reporting activity
    without coupling reporting callers to the enterprise
    security audit implementation.
    """

    event_type: str

    subject: str = ""

    resource: str = ""

    action: str = ""

    result: str = "SUCCESS"

    message: str = ""

    metadata: dict[str, Any] = field(
        default_factory=dict
    )

    def __post_init__(self) -> None:
        """
        Validate the reporting audit event.
        """

        if not self.event_type:
            raise ValueError(
                "Reporting audit event type is required."
            )

        if not isinstance(
            self.metadata,
            dict,
        ):
            raise ValueError(
                "Reporting audit event metadata must be "
                "a dictionary."
            )

class ReportingGovernanceAdapter:
    """
    Reporting-side governance integration boundary.

    Enriches reporting audit events with governance metadata
    without performing authorization, persistence, or audit
    storage itself.
    """

    def enrich(
        self,
        event: ReportAuditEvent,
        *,
        governance_state: str | None = None,
        governance_decision: str | None = None,
        governance_reason: str | None = None,
    ) -> ReportAuditEvent:
        """
        Enrich a reporting audit event with governance metadata.

        The existing event instance is updated in place and
        returned for fluent integration with the reporting
        audit boundary.
        """

        if not isinstance(
            event,
            ReportAuditEvent,
        ):
            raise ValueError(
                "A ReportAuditEvent is required."
            )

        if governance_state is not None:
            event.metadata["governance_state"] = (
                governance_state
            )

        if governance_decision is not None:
            event.metadata["governance_decision"] = (
                governance_decision
            )

        if governance_reason is not None:
            event.metadata["governance_reason"] = (
                governance_reason
            )

        return event


class ReportingAuditAdapter:
    """
    Adapter between the reporting audit boundary and the
    enterprise security audit registry.

    Reporting remains provider-neutral while the enterprise
    security audit infrastructure remains responsible for
    audit event storage and retrieval.
    """

    def __init__(
        self,
        audit_registry: AuditRegistry,
    ) -> None:
        """
        Initialize the reporting audit adapter.

        Args:
            audit_registry:
                Enterprise audit registry responsible for
                recording security audit events.

        Raises:
            ValueError:
                When an invalid audit registry is supplied.
        """

        if not isinstance(
            audit_registry,
            AuditRegistry,
        ):
            raise ValueError(
                "An AuditRegistry is required."
            )

        self.audit_registry = (
            audit_registry
        )

    def record(
        self,
        event: ReportAuditEvent,
    ) -> SecurityAuditEvent:
        """
        Translate and record a reporting audit event.

        Returns:
            SecurityAuditEvent:
                The enterprise audit event recorded in the
                audit registry.
        """

        if not isinstance(
            event,
            ReportAuditEvent,
        ):
            raise ValueError(
                "Reporting audit event must be a "
                "ReportAuditEvent instance."
            )

        security_event = SecurityAuditEvent(
            event_type=event.event_type,
            subject=event.subject,
            resource=event.resource,
            action=event.action,
            result=event.result,
            message=event.message,
            metadata=dict(
                event.metadata
            ),
        )

        self.audit_registry.record(
            security_event
        )

        return security_event


__all__ = [
    "ReportAuditEvent",
    "ReportingGovernanceAdapter",
    "ReportingAuditAdapter",
]
