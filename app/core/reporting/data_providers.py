"""
CDCS Enterprise Management Platform (CDCS-EMP)

Reporting Framework

Report data provider contracts.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from app.core.data import QueryOptions

from app.core.reporting.queries import (
    ReportQuery,
)


class ReportDataProvider(
    ABC,
):
    """
    Abstract contract for report data providers.

    A report data provider is responsible for determining
    whether it can handle a report query and for retrieving
    the corresponding report data.

    Provider implementations must remain independent
    of report presentation, authorization, governance,
    auditing, telemetry, transaction management, and
    persistence implementation details.

    Query execution options are expressed through the
    reusable Enterprise Data Framework QueryOptions
    contract rather than through a reporting-specific
    query-options abstraction.
    """

    @property
    @abstractmethod
    def name(
        self,
    ) -> str:
        """
        Return the canonical provider name.

        Returns:
            Provider identifier.
        """

        raise NotImplementedError

    @abstractmethod
    def supports(
        self,
        query: ReportQuery,
    ) -> bool:
        """
        Determine whether this provider supports
        the supplied report query.

        Args:
            query:
                Provider-neutral report query.

        Returns:
            True when the provider supports the
            supplied query.
        """

        raise NotImplementedError

    @abstractmethod
    def execute(
        self,
        query: ReportQuery,
        options: QueryOptions | None = None,
    ) -> Any:
        """
        Execute the report data query.

        Args:
            query:
                Provider-neutral report query.

            options:
                Optional reusable Enterprise Data Framework
                query options.

        Returns:
            Provider-neutral report data.

        Notes:
            The provider returns data rather than a
            ReportResult. ReportResult belongs to the
            report-generation boundary and remains outside
            the data-provider contract.
        """

        raise NotImplementedError


__all__ = [
    "ReportDataProvider",
]
