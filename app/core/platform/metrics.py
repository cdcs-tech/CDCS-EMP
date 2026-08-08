"""
CDCS Enterprise Management Platform (CDCS-EMP)

Platform Infrastructure

Platform Metrics & Telemetry Foundation.

Provides lightweight internal metrics
and telemetry primitives for enterprise
platform components.
"""

from dataclasses import dataclass, field
from time import perf_counter
from typing import Any, Optional

from app.core.platform.context import (
    RequestContext,
)


@dataclass
class Metric:
    """
    Represents a platform metric.
    """

    name: str

    value: float = 0.0

    labels: dict[str, Any] = field(
        default_factory=dict
    )

    description: str = ""


class MetricsRegistry:
    """
    Central registry for platform metrics.
    """

    def __init__(self):
        """
        Initialize metrics storage.
        """

        self._metrics: dict[
            tuple[str, tuple],
            Metric,
        ] = {}

    def _key(
        self,
        name: str,
        labels: Optional[
            dict[str, Any]
        ] = None,
    ) -> tuple[str, tuple]:
        """
        Build a deterministic metric key.
        """

        labels = labels or {}

        return (
            name,
            tuple(
                sorted(
                    labels.items()
                )
            ),
        )

    def register(
        self,
        name: str,
        *,
        description: str = "",
        labels: Optional[
            dict[str, Any]
        ] = None,
    ) -> Metric:
        """
        Register a metric if it does not exist.
        """

        if not name:
            raise ValueError(
                "Metric name is required."
            )

        labels = dict(
            labels or {}
        )

        key = self._key(
            name,
            labels,
        )

        if key not in self._metrics:

            self._metrics[key] = Metric(
                name=name,
                labels=labels,
                description=description,
            )

        return self._metrics[key]

    def get(
        self,
        name: str,
        *,
        labels: Optional[
            dict[str, Any]
        ] = None,
    ) -> Metric:
        """
        Return a registered metric.
        """

        key = self._key(
            name,
            labels,
        )

        if key not in self._metrics:
            raise KeyError(
                f"Metric '{name}' is not registered."
            )

        return self._metrics[key]

    def increment(
        self,
        name: str,
        amount: float = 1.0,
        *,
        labels: Optional[
            dict[str, Any]
        ] = None,
        description: str = "",
    ) -> Metric:
        """
        Increment a metric.
        """

        metric = self.register(
            name,
            description=description,
            labels=labels,
        )

        metric.value += amount

        return metric

    def set(
        self,
        name: str,
        value: float,
        *,
        labels: Optional[
            dict[str, Any]
        ] = None,
        description: str = "",
    ) -> Metric:
        """
        Set a metric value.
        """

        metric = self.register(
            name,
            description=description,
            labels=labels,
        )

        metric.value = value

        return metric

    def value(
        self,
        name: str,
        *,
        labels: Optional[
            dict[str, Any]
        ] = None,
    ) -> float:
        """
        Return a metric value.
        """

        return self.get(
            name,
            labels=labels,
        ).value

    def all(self) -> list[Metric]:
        """
        Return all registered metrics.
        """

        return list(
            self._metrics.values()
        )

    def count(self) -> int:
        """
        Return the number of registered metrics.
        """

        return len(
            self._metrics
        )

    def clear(self) -> None:
        """
        Remove all registered metrics.
        """

        self._metrics.clear()

    def __repr__(self) -> str:
        """
        Developer-friendly representation.
        """

        return (
            f"<MetricsRegistry "
            f"{self.count()} metrics>"
        )


class MetricTimer:
    """
    Context manager for measuring operation duration.
    """

    def __init__(
        self,
        registry: MetricsRegistry,
        metric_name: str,
        *,
        labels: Optional[
            dict[str, Any]
        ] = None,
    ):
        self.registry = registry
        self.metric_name = metric_name
        self.labels = dict(
            labels or {}
        )
        self.elapsed: Optional[
            float
        ] = None
        self._started: Optional[
            float
        ] = None

    def __enter__(self):
        self._started = perf_counter()

        return self

    def __exit__(
        self,
        exc_type,
        exc_value,
        traceback,
    ):
        if self._started is not None:

            self.elapsed = (
                perf_counter()
                - self._started
            )

            self.registry.set(
                self.metric_name,
                self.elapsed,
                labels=self.labels,
            )

        return False


class PlatformMetrics:
    """
    High-level metrics interface for CDCS-EMP.
    """

    def __init__(
        self,
        registry: Optional[
            MetricsRegistry
        ] = None,
    ):
        self.registry = (
            registry
            or MetricsRegistry()
        )

    def increment(
        self,
        name: str,
        amount: float = 1.0,
        *,
        context: Optional[
            RequestContext
        ] = None,
        **labels: Any,
    ) -> Metric:
        """
        Increment a metric with optional
        request context information.
        """

        metric_labels = dict(
            labels
        )

        if context is not None:

            metric_labels.setdefault(
                "module_name",
                context.module_name,
            )

        return self.registry.increment(
            name,
            amount,
            labels=metric_labels,
        )

    def set(
        self,
        name: str,
        value: float,
        *,
        context: Optional[
            RequestContext
        ] = None,
        **labels: Any,
    ) -> Metric:
        """
        Set a metric value.
        """

        metric_labels = dict(
            labels
        )

        if context is not None:

            metric_labels.setdefault(
                "module_name",
                context.module_name,
            )

        return self.registry.set(
            name,
            value,
            labels=metric_labels,
        )

    def timer(
        self,
        name: str,
        *,
        context: Optional[
            RequestContext
        ] = None,
        **labels: Any,
    ) -> MetricTimer:
        """
        Create a metric timer.
        """

        metric_labels = dict(
            labels
        )

        if context is not None:

            metric_labels.setdefault(
                "module_name",
                context.module_name,
            )

        return MetricTimer(
            self.registry,
            name,
            labels=metric_labels,
        )

    def all(self) -> list[Metric]:
        """
        Return all metrics.
        """

        return self.registry.all()

    def clear(self) -> None:
        """
        Clear all metrics.
        """

        self.registry.clear()

    def __repr__(self) -> str:
        """
        Developer-friendly representation.
        """

        return (
            f"<PlatformMetrics "
            f"metrics="
            f"{self.registry.count()}>"
        )


metrics_registry = MetricsRegistry()

platform_metrics = PlatformMetrics(
    registry=metrics_registry
)


__all__ = [
    "Metric",
    "MetricsRegistry",
    "MetricTimer",
    "PlatformMetrics",
    "metrics_registry",
    "platform_metrics",
]
