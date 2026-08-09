"""
CDCS Enterprise Management Platform (CDCS-EMP)

Enterprise Application Execution Framework

Execution context.
"""

from dataclasses import dataclass, field
from typing import Any, Optional

from app.core.execution.exceptions import (
    ExecutionContextException,
)


@dataclass(slots=True)
class ExecutionContext:
    """
    Represents the execution context for
    an enterprise operation.
    """

    user_id: Optional[str] = None

    module_name: Optional[str] = None

    operation: Optional[str] = None

    request_id: Optional[str] = None

    correlation_id: Optional[str] = None

    trace_id: Optional[str] = None

    environment: Optional[str] = None

    metadata: dict[str, Any] = field(
        default_factory=dict
    )

    def validate(self) -> None:
        """
        Validate the execution context.
        """

        if not self.module_name:
            raise ExecutionContextException(
                "Execution context requires "
                "a module name."
            )

        if not self.operation:
            raise ExecutionContextException(
                "Execution context requires "
                "an operation."
            )

    def with_metadata(
        self,
        **metadata: Any,
    ) -> "ExecutionContext":
        """
        Return a copy of the context with
        additional metadata.
        """

        combined = dict(
            self.metadata
        )

        combined.update(
            metadata
        )

        return ExecutionContext(
            user_id=self.user_id,
            module_name=self.module_name,
            operation=self.operation,
            request_id=self.request_id,
            correlation_id=self.correlation_id,
            trace_id=self.trace_id,
            environment=self.environment,
            metadata=combined,
        )


__all__ = [
    "ExecutionContext",
]
