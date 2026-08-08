"""
CDCS Enterprise Management Platform (CDCS-EMP)

Platform Infrastructure

Correlation and Trace IDs.

Provides standardized identifiers for
tracking enterprise operations across
platform components.
"""

from dataclasses import dataclass, field
from typing import Optional
from uuid import uuid4


def generate_id(prefix: str) -> str:
    """
    Generate a platform trace identifier.
    """

    return f"{prefix}-{uuid4()}"


@dataclass(slots=True)
class TraceContext:
    """
    Represents correlation and trace information
    for an enterprise operation.
    """

    correlation_id: str = field(
        default_factory=lambda:
            generate_id("CORR")
    )

    trace_id: str = field(
        default_factory=lambda:
            generate_id("TRACE")
    )

    parent_trace_id: Optional[str] = None

    span_id: str = field(
        default_factory=lambda:
            generate_id("SPAN")
    )


    def child(
        self,
    ) -> "TraceContext":
        """
        Create a child trace context.

        The current trace becomes the parent
        of the newly created trace.
        """

        return TraceContext(
            correlation_id=self.correlation_id,
            trace_id=generate_id("TRACE"),
            parent_trace_id=self.trace_id,
        )


    def identity(self) -> dict[str, Optional[str]]:
        """
        Return trace identity information.
        """

        return {
            "correlation_id": (
                self.correlation_id
            ),
            "trace_id": self.trace_id,
            "parent_trace_id": (
                self.parent_trace_id
            ),
            "span_id": self.span_id,
        }


    def validate(self) -> bool:
        """
        Validate the trace context.
        """

        if not self.correlation_id:
            raise ValueError(
                "Correlation ID is required."
            )

        if not self.trace_id:
            raise ValueError(
                "Trace ID is required."
            )

        if not self.span_id:
            raise ValueError(
                "Span ID is required."
            )

        return True


    def __repr__(self) -> str:
        """
        Developer-friendly representation.
        """

        return (
            f"<TraceContext "
            f"correlation_id="
            f"{self.correlation_id!r} "
            f"trace_id="
            f"{self.trace_id!r} "
            f"parent_trace_id="
            f"{self.parent_trace_id!r}>"
        )


__all__ = [
    "TraceContext",
    "generate_id",
]

