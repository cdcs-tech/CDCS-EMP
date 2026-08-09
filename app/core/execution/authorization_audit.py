"""
CDCS Enterprise Management Platform (CDCS-EMP)

Enterprise Application Execution Framework

Authorization audit integration.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from app.core.execution.authorization import (
    AuthorizationDecision,
)

from app.core.execution.commands.base import (
    BaseCommand,
)

from app.core.execution.context import (
    ExecutionContext,
)

from app.core.security.audit import (
    SecurityAuditEvent,
)


AUTHORIZATION_AUDIT_EVENT_TYPE = (
    "EXECUTION_AUTHORIZATION"
)


@dataclass(frozen=True)
class AuthorizationAuditContract:
    """
    Defines the audit contract for execution
    authorization decisions.

    The contract converts an authorization decision
    together with its command and execution context
    into a SecurityAuditEvent.
    """

    event_type: str = (
        AUTHORIZATION_AUDIT_EVENT_TYPE
    )

    def build_event(
        self,
        command: BaseCommand,
        context: ExecutionContext,
        decision: AuthorizationDecision,
    ) -> SecurityAuditEvent:
        """
        Build a security audit event from an
        authorization decision.
        """

        if not isinstance(command, BaseCommand):
            raise TypeError("command must be a BaseCommand.")

        if not isinstance(context, ExecutionContext):
            raise TypeError("context must be an ExecutionContext.")

        if not isinstance(decision, AuthorizationDecision):
            raise TypeError(
                "decision must be an AuthorizationDecision."
            )

        allowed = decision.is_allowed()

        # Permission resolution is handled by the
        # authorization layer. The audit contract
        # intentionally leaves this field empty when
        # the decision does not explicitly provide it.
        permission_code = ""

        metadata: dict[str, Any] = dict(context.metadata)

        metadata.update(
            {
                "authorization_allowed": allowed,
                "authorization_reason": decision.reason,
                "permission_code": permission_code,
                "authorization_metadata": dict(decision.metadata),
            }
        )

        if context.request_id:
            metadata.setdefault("request_id", context.request_id)

        if context.correlation_id:
            metadata.setdefault("correlation_id", context.correlation_id)

        if context.trace_id:
            metadata.setdefault("trace_id", context.trace_id)

        if context.environment:
            metadata.setdefault("environment", context.environment)

        if context.module_name:
            metadata.setdefault("module_name", context.module_name)

        if context.user_id:
            metadata.setdefault("user_id", context.user_id)

        return SecurityAuditEvent(
            event_type=self.event_type,
            subject=context.user_id or "",
            resource=command.command_name,
            action=context.operation or "",
            result=("SUCCESS" if allowed else "FAILED"),
            message=(
                decision.reason
                or (
                    "Command execution authorization granted."
                    if allowed
                    else "Command execution authorization denied."
                )
            ),
            metadata=metadata,
        )



    def to_event(
        self,
        command: BaseCommand,
        context: ExecutionContext,
        decision: AuthorizationDecision,
    ) -> SecurityAuditEvent:
        """
        Compatibility alias for build_event().
        """

        return self.build_event(
            command,
            context,
            decision,
        )


def build_authorization_audit_event(
    command: BaseCommand,
    context: ExecutionContext,
    decision: AuthorizationDecision,
) -> SecurityAuditEvent:
    """
    Build an authorization audit event using
    the standard authorization audit contract.
    """

    contract = AuthorizationAuditContract()

    return contract.build_event(
        command,
        context,
        decision,
    )


def record_authorization_audit_event(
    command: BaseCommand,
    context: ExecutionContext,
    decision: AuthorizationDecision,
    audit_registry: Any,
) -> SecurityAuditEvent:
    """
    Build and record an authorization audit event.
    """

    event = build_authorization_audit_event(
        command,
        context,
        decision,
    )

    record = getattr(
        audit_registry,
        "record",
        None,
    )

    if not callable(record):
        raise TypeError(
            "audit_registry must provide "
            "a callable 'record' method."
        )

    record(event)

    return event


__all__ = [
    "AUTHORIZATION_AUDIT_EVENT_TYPE",
    "AuthorizationAuditContract",
    "build_authorization_audit_event",
    "record_authorization_audit_event",
]
