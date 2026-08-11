"""
CDCS Enterprise Management Platform (CDCS-EMP)

Enterprise Application Execution Framework

Execution event integration with platform observability.
"""

from __future__ import annotations

from typing import Optional

from app.core.execution.event_emitter import (
    ExecutionEventEmitter,
)

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


class ObservabilityExecutionEventEmitter(
    ExecutionEventEmitter
):
    """
    Execution event emitter that integrates
    execution lifecycle events with the
    platform observability foundation.

    The emitter translates execution events into:

    - structured platform log entries
    - platform execution metrics

    Observability failures are isolated from
    command execution semantics.
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
    ) -> None:
        """
        Initialize the observability emitter.
        """

        self.logger = (
            logger
            or platform_logger
        )

        self.metrics = (
            metrics
            or platform_metrics
        )

    def emit(
        self,
        event: ExecutionEvent,
    ) -> None:
        """
        Emit an execution event to the
        platform observability infrastructure.

        Logging and metrics failures are isolated
        so that observability cannot alter
        execution behavior.
        """

        if not isinstance(
            event,
            ExecutionEvent,
        ):
            raise TypeError(
                "event must be an ExecutionEvent."
            )

        try:
            self._record_metric(
                event
            )

            self._record_log(
                event
            )

        except Exception:
            # Observability infrastructure must
            # never alter execution semantics.
            return

    def _record_metric(
        self,
        event: ExecutionEvent,
    ) -> None:
        """
        Record the metric associated with
        an execution lifecycle event.
        """

        metric_name = (
            self._metric_name(event)
        )

        labels = {
            "command_name": (
                event.command_name
            ),
            "event_type": (
                event.event_type.value
            ),
            "outcome": event.outcome,
        }

        if event.context.module_name:
            labels["module_name"] = (
                event.context.module_name
            )

        self.metrics.increment(
            metric_name,
            context=None,
            **labels,
        )

    def _record_log(
        self,
        event: ExecutionEvent,
    ) -> None:
        """
        Record a structured log entry for
        an execution lifecycle event.
        """

        context = event.context

        extra = {
            "event_type": (
                event.event_type.value
            ),
            "command_name": (
                event.command_name
            ),
            "outcome": event.outcome,
            "source": event.metadata.get(
                "source",
                "execution",
            ),
        }

        error_code = event.metadata.get(
            "error_code"
        )

        if error_code is not None:
            extra["error_code"] = (
                error_code
            )

        message = (
            f"Execution event: "
            f"{event.event_type.value} "
            f"for command "
            f"{event.command_name}"
        )

        if (
            event.event_type
            == ExecutionEventType.FAILED
        ):
            self.logger.error(
                message,
                context=None,
                **self._context_metadata(
                    context,
                    **extra,
                ),
            )

        elif (
            event.event_type
            == ExecutionEventType.DENIED
        ):
            self.logger.warning(
                message,
                context=None,
                **self._context_metadata(
                    context,
                    **extra,
                ),
            )

        else:
            self.logger.info(
                message,
                context=None,
                **self._context_metadata(
                    context,
                    **extra,
                ),
            )

    @staticmethod
    def _context_metadata(
        context,
        **extra,
    ) -> dict:
        """
        Convert execution context identity
        into structured logging metadata.
        """

        metadata = dict(extra)

        metadata.setdefault(
            "request_id",
            context.request_id,
        )

        metadata.setdefault(
            "correlation_id",
            context.correlation_id,
        )

        metadata.setdefault(
            "trace_id",
            context.trace_id,
        )

        metadata.setdefault(
            "user_id",
            context.user_id,
        )

        metadata.setdefault(
            "module_name",
            context.module_name,
        )

        metadata.setdefault(
            "operation",
            context.operation,
        )

        return metadata

    @staticmethod
    def _metric_name(
        event: ExecutionEvent,
    ) -> str:
        """
        Resolve the metric name for an
        execution lifecycle event.
        """

        mapping = {
            ExecutionEventType.STARTED:
                "execution.started",

            ExecutionEventType.COMPLETED:
                "execution.completed",

            ExecutionEventType.FAILED:
                "execution.failed",

            ExecutionEventType.DENIED:
                "execution.denied",
        }

        return mapping.get(
            event.event_type,
            "execution.events",
        )

    def __repr__(self) -> str:
        """
        Developer-friendly representation.
        """

        return (
            "<ObservabilityExecutionEventEmitter>"
        )


__all__ = [
    "ObservabilityExecutionEventEmitter",
]
