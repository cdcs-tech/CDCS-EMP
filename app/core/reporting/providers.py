"""
CDCS Enterprise Management Platform (CDCS-EMP)

Reporting Framework

Report provider contracts.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from app.core.reporting.models import (
    ReportDefinition,
)

from app.core.reporting.results import (
    ReportResult,
)


class ReportProvider(ABC):
    """
    Abstract contract for report providers.

    A report provider is responsible for determining
    whether it can handle a report definition and for
    producing the corresponding report result.

    Provider implementations must remain independent
    of authorization, governance, auditing, telemetry,
    persistence, and presentation concerns.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """
        Return the canonical provider name.

        Returns:
            Provider identifier.
        """

        raise NotImplementedError

    @abstractmethod
    def supports(
        self,
        definition: ReportDefinition,
    ) -> bool:
        """
        Determine whether this provider supports
        the supplied report definition.

        Args:
            definition:
                Report definition to evaluate.

        Returns:
            True when the provider supports the
            supplied definition.
        """

        raise NotImplementedError

    @abstractmethod
    def generate(
    self,
    definition: ReportDefinition,
    request: Any,
    ) -> ReportResult:
        """
        Generate a report from a definition and request.

        Args:
            definition:
                Report definition describing the report.

            request:
                Provider-neutral reporting request.

        Returns:
            Standardized report result.

        Notes:
            The contract deliberately uses framework-neutral
            request and result boundaries. Concrete request
            and result models may be introduced by later
            reporting stages.
        """

        raise NotImplementedError


__all__ = [
    "ReportProvider",
]
