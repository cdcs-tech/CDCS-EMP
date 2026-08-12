"""
CDCS Enterprise Management Platform (CDCS-EMP)

Platform Infrastructure

Execution Observability Integration.

Translates execution lifecycle events into
platform logging and metrics signals.
"""

from typing import Optional

from app.core.execution.events import (
    ExecutionEvent,
    ExecutionEventType,
)
from app.core.platform.context import (
    RequestContext,
)
from app.core.platform.logging import (
    PlatformLogger,
    platform_logger,
)
from app.core.platform.metrics import (
    PlatformMetrics,
    platform_metrics,
)

from app.core.platform.trace import (
    TraceContext,
)


class PlatformExecutionObserver:
    """
    Integrates execution lifecycle events with
    platform observability infrastructure.

    Execution events remain owned by the execution
    framework. This component provides the platform
    observability boundary for those events.
    """

    STARTED_METRIC = (
        "execution.events.started"
    )

    COMPLETED_METRIC = (
        "execution.events.completed"
    )

    FAILED_METRIC = (
        "execution.events.failed"
    )

    DENIED_METRIC = (
        "execution.events.denied"
    )

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
        Initialize the execution observer.
        """

        self.logger = (
            logger
            or platform_logger
        )

        self.metrics = (
            metrics
            or platform_metrics
        )

    def _request_context(
        self,
        event: ExecutionEvent,
    ) -> RequestContext:
        """
        Translate an execution context into
        the platform request context used by
        logging infrastructure.
        """

        context = event.context

        return RequestContext(
           user_id=context.user_id,
           module_name=context.module_name,
           operation=context.operation,
           request_id=context.request_id,
           trace=TraceContext(
               correlation_id=context.correlation_id,
               trace_id=context.trace_id,
            ),
        )

    def _metric_labels(
        self,
        event: ExecutionEvent,
    ) -> dict[str, str]:
        """
        Build low-cardinality metric labels.
        """

        context = event.context

        return {
            "command_name": (
                event.command_name
            ),
            "event_type": (
                event.event_type.value
            ),
            "outcome": event.outcome,
            "module_name": (
                context.module_name
            ),
        }

    def _increment_metric(
        self,
        event: ExecutionEvent,
    ) -> None:
        """
        Increment the metric associated with
        the execution lifecycle event.
        """

        metric_names = {
            ExecutionEventType.STARTED:
                self.STARTED_METRIC,
            ExecutionEventType.COMPLETED:
                self.COMPLETED_METRIC,
            ExecutionEventType.FAILED:
                self.FAILED_METRIC,
            ExecutionEventType.DENIED:
                self.DENIED_METRIC,
        }

        metric_name = metric_names.get(
            event.event_type
        )

        if metric_name is None:
            return

        self.metrics.increment(
            metric_name,
            context=None,
            **self._metric_labels(event),
        )

    def _log_event(
        self,
        event: ExecutionEvent,
        context: RequestContext,
    ) -> None:
        """
        Log the execution lifecycle event.
        """

        metadata = {
            "command_name": (
                event.command_name
            ),
            "event_type": (
                event.event_type.value
            ),
            "outcome": event.outcome,
        }

        metadata.update(
            event.metadata
        )

        if (
            event.event_type
            == ExecutionEventType.STARTED
        ):
            self.logger.info(
                "Execution started.",
                context=context,
                **metadata,
            )

        elif (
            event.event_type
            == ExecutionEventType.COMPLETED
        ):
            self.logger.info(
                "Execution completed.",
                context=context,
                **metadata,
            )

        elif (
            event.event_type
            == ExecutionEventType.FAILED
        ):
            self.logger.error(
                "Execution failed.",
                context=context,
                **metadata,
            )

        elif (
            event.event_type
            == ExecutionEventType.DENIED
        ):
            self.logger.warning(
                "Execution denied.",
                context=context,
                **metadata,
            )

    def emit(
        self,
        event: ExecutionEvent,
    ) -> None:
        """
        Translate an execution event into
        platform observability signals.

        Observability failures are intentionally
        isolated from execution semantics.
        """

        if not isinstance(
            event,
            ExecutionEvent,
        ):
            raise TypeError(
                "event must be an ExecutionEvent."
            )

        context = self._request_context(
            event
        )

        try:
            self._log_event(
                event,
                context,
            )
        except Exception:
            pass

        try:
            self._increment_metric(
                event
            )
        except Exception:
            pass

    def __repr__(self) -> str:
        """
        Developer-friendly representation.
        """

        return (
            "<PlatformExecutionObserver>"
        )


platform_execution_observer = (
    PlatformExecutionObserver()
)


__all__ = [
    "PlatformExecutionObserver",
    "platform_execution_observer",
]
