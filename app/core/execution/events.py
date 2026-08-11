"""
CDCS Enterprise Management Platform (CDCS-EMP)

Enterprise Application Execution Framework

Execution event contract.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any

from app.core.execution.context import (
    ExecutionContext,
)


class ExecutionEventType(str, Enum):
    """
    Standard execution event types.
    """

    STARTED = "execution.started"

    COMPLETED = "execution.completed"

    FAILED = "execution.failed"

    DENIED = "execution.denied"


@dataclass(slots=True)
class ExecutionEvent:
    """
    Represents a standardized execution event.
    """

    event_type: ExecutionEventType

    command_name: str

    context: ExecutionContext

    outcome: str

    timestamp: datetime = field(
        default_factory=lambda: datetime.now(
            timezone.utc
        )
    )

    metadata: dict[str, Any] = field(
        default_factory=dict
    )

    def __post_init__(self) -> None:
        """
        Validate the execution event contract.
        """

        if not isinstance(
            self.event_type,
            ExecutionEventType,
        ):
            raise TypeError(
                "event_type must be an "
                "ExecutionEventType."
            )

        if not isinstance(
            self.command_name,
            str,
        ):
            raise TypeError(
                "command_name must be a string."
            )

        if not self.command_name.strip():
            raise ValueError(
                "command_name cannot be empty."
            )

        if not isinstance(
            self.context,
            ExecutionContext,
        ):
            raise TypeError(
                "context must be an "
                "ExecutionContext."
            )

        if not isinstance(
            self.outcome,
            str,
        ):
            raise TypeError(
                "outcome must be a string."
            )

        if not self.outcome.strip():
            raise ValueError(
                "outcome cannot be empty."
            )

        if self.outcome not in {
            "success",
            "failure",
            "denied",
        }:
            raise ValueError(
                "outcome must be one of "
                "'success', 'failure', or "
                "'denied'."
            )

        if not isinstance(
            self.timestamp,
            datetime,
        ):
            raise TypeError(
                "timestamp must be a datetime."
            )

        if (
            self.timestamp.tzinfo is None
            or self.timestamp.utcoffset() is None
        ):
            raise ValueError(
                "timestamp must be timezone-aware."
            )

        if not isinstance(
            self.metadata,
            dict,
        ):
            raise TypeError(
                "metadata must be a dictionary."
            )

        # Isolate event metadata from the
        # caller's source dictionary.
        self.metadata = dict(
            self.metadata
        )

    def validate(self) -> None:
        """
        Explicitly validate the execution event.
        """

        self.__post_init__()

    def is_success(self) -> bool:
        """
        Determine whether the event represents
        successful execution.
        """

        return self.outcome == "success"

    def is_failure(self) -> bool:
        """
        Determine whether the event represents
        failed execution.
        """

        return self.outcome == "failure"

    def is_denied(self) -> bool:
        """
        Determine whether the event represents
        denied execution.
        """

        return self.outcome == "denied"

    def with_metadata(
        self,
        **metadata: Any,
    ) -> "ExecutionEvent":
        """
        Return an enriched copy of the event.

        Existing metadata is preserved and the
        supplied metadata is merged into the copy.
        """

        combined = dict(
            self.metadata
        )

        combined.update(
            metadata
        )

        return ExecutionEvent(
            event_type=self.event_type,
            command_name=self.command_name,
            context=self.context,
            outcome=self.outcome,
            timestamp=self.timestamp,
            metadata=combined,
        )


__all__ = [
    "ExecutionEventType",
    "ExecutionEvent",
]
