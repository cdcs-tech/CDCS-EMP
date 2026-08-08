"""
CDCS Enterprise Management Platform (CDCS-EMP)

Platform Infrastructure

Request Context Foundation.

Provides a standardized execution context
for enterprise platform operations.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Optional
from uuid import uuid4

from app.core.platform.runtime import (
    RuntimeContext,
    runtime_context,
)

from app.core.platform.trace import (
    TraceContext,
)


@dataclass(slots=True)
class RequestContext:
    """
    Represents the context of a platform operation.

    The request context provides a common execution
    identity for enterprise platform components,
    including:

    - User identity
    - Module identity
    - Operation identity
    - Resource identity
    - Runtime identity
    - Correlation identity
    - Trace identity
    - Request metadata
    """

    runtime: RuntimeContext = field(
        default_factory=lambda:
            runtime_context
    )

    request_id: str = field(
        default_factory=lambda:
            str(uuid4())
    )

    trace: TraceContext = field(
        default_factory=TraceContext
    )

    user_id: Optional[str] = None

    username: Optional[str] = None

    module_name: Optional[str] = None

    operation: Optional[str] = None

    resource: Optional[str] = None

    source: Optional[str] = None

    metadata: dict[str, Any] = field(
        default_factory=dict
    )

    created_at: datetime = field(
        default_factory=lambda:
            datetime.now(timezone.utc)
    )

    @property
    def environment(self) -> str:
        """
        Return the active runtime environment.
        """

        return self.runtime.environment

    @property
    def application_name(self) -> str:
        """
        Return the application name.
        """

        return self.runtime.application_name

    @property
    def application_version(self) -> str:
        """
        Return the application version.
        """

        return self.runtime.application_version

    @property
    def correlation_id(self) -> str:
        """
        Return the correlation ID associated
        with this request.
        """

        return self.trace.correlation_id

    @property
    def trace_id(self) -> str:
        """
        Return the trace ID associated
        with this request.
        """

        return self.trace.trace_id

    @property
    def parent_trace_id(
        self,
    ) -> Optional[str]:
        """
        Return the parent trace ID.
        """

        return self.trace.parent_trace_id

    @property
    def span_id(self) -> str:
        """
        Return the current span ID.
        """

        return self.trace.span_id

    def identity(self) -> dict[str, Any]:
        """
        Return request identity information.

        Includes both request-level identity
        and distributed tracing identifiers.
        """

        return {
            "request_id": self.request_id,
            "user_id": self.user_id,
            "username": self.username,
            "module_name": self.module_name,
            "operation": self.operation,
            "resource": self.resource,
            "source": self.source,
            "correlation_id": (
                self.trace.correlation_id
            ),
            "trace_id": (
                self.trace.trace_id
            ),
            "parent_trace_id": (
                self.trace.parent_trace_id
            ),
            "span_id": (
                self.trace.span_id
            ),
        }

    def runtime_identity(
        self,
    ) -> dict[str, Any]:
        """
        Return runtime identity information.
        """

        return self.runtime.identity()

    def trace_identity(
        self,
    ) -> dict[str, Optional[str]]:
        """
        Return distributed tracing identity.
        """

        return self.trace.identity()

    def as_dict(self) -> dict[str, Any]:
        """
        Return the complete request context
        as a dictionary.
        """

        return {
            "request_id": self.request_id,
            "user_id": self.user_id,
            "username": self.username,
            "module_name": self.module_name,
            "operation": self.operation,
            "resource": self.resource,
            "source": self.source,
            "environment": self.environment,
            "application_name": (
                self.application_name
            ),
            "application_version": (
                self.application_version
            ),
            "correlation_id": (
                self.trace.correlation_id
            ),
            "trace_id": (
                self.trace.trace_id
            ),
            "parent_trace_id": (
                self.trace.parent_trace_id
            ),
            "span_id": (
                self.trace.span_id
            ),
            "created_at": self.created_at,
            "metadata": dict(
                self.metadata
            ),
        }

    def child_context(
        self,
    ) -> "RequestContext":
        """
        Create a child request context.

        The child context preserves the current
        correlation ID while creating a new trace
        with the current trace as its parent.
        """

        return RequestContext(
            runtime=self.runtime,
            trace=self.trace.child(),
            user_id=self.user_id,
            username=self.username,
            module_name=self.module_name,
            operation=self.operation,
            resource=self.resource,
            source=self.source,
            metadata=dict(
                self.metadata
            ),
        )

    def add_metadata(
        self,
        key: str,
        value: Any,
    ) -> None:
        """
        Add metadata to the request context.
        """

        if not key:
            raise ValueError(
                "Metadata key is required."
            )

        self.metadata[key] = value

    def validate(self) -> bool:
        """
        Validate request context and its
        associated runtime and trace contexts.
        """

        if not self.request_id:
            raise ValueError(
                "Request ID is required."
            )

        if not self.environment:
            raise ValueError(
                "Runtime environment is required."
            )

        if not self.application_name:
            raise ValueError(
                "Application name is required."
            )

        if not self.application_version:
            raise ValueError(
                "Application version is required."
            )

        self.runtime.validate()

        self.trace.validate()

        return True

    def __repr__(self) -> str:
        """
        Developer-friendly representation.
        """

        return (
            f"<RequestContext "
            f"request_id="
            f"{self.request_id!r} "
            f"correlation_id="
            f"{self.correlation_id!r} "
            f"trace_id="
            f"{self.trace_id!r} "
            f"module="
            f"{self.module_name!r} "
            f"operation="
            f"{self.operation!r}>"
        )


__all__ = [
    "RequestContext",
]
