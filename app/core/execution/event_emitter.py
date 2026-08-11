"""
CDCS Enterprise Management Platform (CDCS-EMP)

Enterprise Application Execution Framework

Execution event emission.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional

from app.core.execution.events import (
    ExecutionEvent,
    ExecutionEventType,
)

from app.core.platform.logging import (
    PlatformLogger,
    platform_logger,
)

from app.core.platform.metrics import (
    PlatformMetrics,
    platform_metrics,
)


class ExecutionEventEmitter(ABC):
    """
    Defines the event-emission contract used by
    enterprise command execution.

    The execution framework depends on this abstraction
    rather than directly depending on a concrete event
    storage or telemetry implementation.
    """

    @abstractmethod
    def emit(
        self,
        event: ExecutionEvent,
    ) -> None:
        """
        Emit an execution event.
        """

        raise NotImplementedError


class RecordingExecutionEventEmitter(
    ExecutionEventEmitter
):
    """
    In-memory event emitter used for framework testing.

    Events are retained in emission order.
    """

    def __init__(self) -> None:
        self.events: list[ExecutionEvent] = []

    def emit(
        self,
        event: ExecutionEvent,
    ) -> None:
        """
        Record an execution event.
        """

        if not isinstance(
            event,
            ExecutionEvent,
        ):
            raise TypeError(
                "event must be an ExecutionEvent."
            )

        self.events.append(event)

    def clear(self) -> None:
        """
        Remove all recorded events.
        """

        self.events.clear()

    def count(self) -> int:
        """
        Return the number of recorded events.
        """

        return len(self.events)


class ObservabilityExecutionEventEmitter(
    ExecutionEventEmitter
):
    """
    Execution event emitter integrated with the
    platform observability foundation.

    The emitter provides:

    - structured execution-event logging;
    - execution-event metrics;
    - optional forwarding to another event emitter.

    Observability failures are isolated from the
    execution framework.
    """

    def __init__(
        self,
        *,
        logger: Optional[
            PlatformLogger
        ] = None,
        metrics: Optional[
            PlatformMetrics
        ] = None,
        downstream: Optional[
            ExecutionEventEmitter
        ] = None,
    ) -> None:
        """
        Initialize the observability event emitter.
        """

        self.logger = (
            logger
            or platform_logger
        )

        self.metrics = (
            metrics
            or platform_metrics
        )

        self.downstream = downstream

    def emit(
        self,
        event: ExecutionEvent,
    ) -> None:
        """
        Emit an execution event to the
        observability infrastructure.

        A downstream emitter, when configured,
        receives the same event after observability
        processing.
        """

        if not isinstance(
            event,
            ExecutionEvent,
        ):
            raise TypeError(
                "event must be an ExecutionEvent."
            )

        self._log_event(event)
        self._record_metrics(event)

        if self.downstream is not None:
            self.downstream.emit(event)

    def _log_event(
        self,
        event: ExecutionEvent,
    ) -> None:
        """
        Write the execution event to the
        platform logging infrastructure.

        Logging failures are intentionally isolated.
        """

        try:
            context = event.context

            self.logger.info(
                "Execution event emitted.",
                event_type=event.event_type.value,
                command_name=event.command_name,
                outcome=event.outcome,
                request_id=getattr(
                    context,
                    "request_id",
                    None,
                ),
                user_id=getattr(
                    context,
                    "user_id",
                    None,
                ),
                module_name=getattr(
                    context,
                    "module_name",
                    None,
                ),
                operation=getattr(
                    context,
                    "operation",
                    None,
                ),
                correlation_id=getattr(
                    context,
                    "correlation_id",
                    None,
                ),
                trace_id=getattr(
                    context,
                    "trace_id",
                    None,
                ),
                parent_trace_id=getattr(
                    context,
                    "parent_trace_id",
                    None,
                ),
                span_id=getattr(
                    context,
                    "span_id",
                    None,
                ),
                event_timestamp=event.timestamp.isoformat(),
                metadata=dict(
                    event.metadata
                ),
            )

        except Exception:
            # Observability must never alter
            # execution semantics.
            return

    def _record_metrics(
        self,
        event: ExecutionEvent,
    ) -> None:
        """
        Record execution-event metrics.

        Metric labels are deliberately limited to
        bounded execution dimensions and do not
        contain request, trace, or user identifiers.
        """

        try:
            event_type = event.event_type.value

            self.metrics.increment(
                "execution.events",
                event_type=event_type,
                outcome=event.outcome,
            )

            metric_name = (
                f"execution.events."
                f"{self._metric_suffix(event.event_type)}"
            )

            self.metrics.increment(
                metric_name,
                outcome=event.outcome,
            )

        except Exception:
            # Metrics must never alter execution
            # semantics.
            return

    @staticmethod
    def _metric_suffix(
        event_type: ExecutionEventType,
    ) -> str:
        """
        Return the stable metric suffix associated
        with an execution event type.
        """

        mapping = {
            ExecutionEventType.STARTED: "started",
            ExecutionEventType.COMPLETED: "completed",
            ExecutionEventType.FAILED: "failed",
            ExecutionEventType.DENIED: "denied",
        }

        return mapping[event_type]
