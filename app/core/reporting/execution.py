"""
CDCS Enterprise Management Platform (CDCS-EMP)

Reporting Framework

Report query execution contracts.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from app.core.reporting.providers import (
    ReportProvider,
)
from app.core.reporting.queries import (
    ReportQuery,
)
from app.core.reporting.results import (
    ReportResult,
)


class ReportQueryExecutor(ABC):
    """
    Abstract contract for executing report queries.

    A query executor is responsible for executing a
    provider-neutral report query through a supplied
    data provider and returning a standardized report
    result.

    Provider resolution, authorization, governance,
    auditing, telemetry, persistence, and presentation
    remain outside this contract.
    """

    @abstractmethod
    def execute(
        self,
        provider: ReportProvider,
        query: ReportQuery,
    ) -> ReportResult:
        """
        Execute a report query through a data provider.

        Args:
            provider:
                Data provider responsible for obtaining
                the report data.

            query:
                Provider-neutral report query.

        Returns:
            Standardized report result.
        """

        raise NotImplementedError


__all__ = [
    "ReportQueryExecutor",
]
