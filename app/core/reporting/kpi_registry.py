"""
CDCS Enterprise Management Platform (CDCS-EMP)

Reporting & Analytics Framework

Report KPI definition registration and resolution.
"""

from __future__ import annotations

from typing import Iterable

from app.core.reporting.analytics import (
    ReportKPI,
)
from app.core.reporting.exceptions import (
    ReportRegistrationException,
)


class ReportKPIRegistry:
    """
    Registry responsible for registering and resolving
    provider-neutral report KPI definitions.

    The registry owns KPI definition discovery and selection
    only.

    KPI calculation, aggregation, query execution,
    persistence, presentation, authorization, governance,
    auditing, telemetry, and scheduling remain outside this
    contract.
    """

    def __init__(
        self,
        kpis: Iterable[ReportKPI] | None = None,
    ) -> None:
        """
        Initialize the KPI registry.

        Args:
            kpis:
                Optional initial KPI definition collection.

        Raises:
            ReportRegistrationException:
                When an invalid or duplicate KPI is supplied.
        """

        self._kpis: dict[
            str,
            ReportKPI,
        ] = {}

        if kpis is not None:

            for kpi in kpis:

                self.register(
                    kpi
                )

    def register(
        self,
        kpi: ReportKPI,
    ) -> None:
        """
        Register a report KPI definition.

        KPI identifiers are derived from the KPI's canonical
        identifier and normalized to lowercase for registry
        lookup.

        Raises:
            ReportRegistrationException:
                When the KPI is invalid or already registered.
        """

        if not isinstance(
            kpi,
            ReportKPI,
        ):
            raise ReportRegistrationException(
                "KPI must be a ReportKPI."
            )

        identifier = self._normalize_identifier(
            kpi.identifier
        )

        if identifier in self._kpis:

            raise ReportRegistrationException(
                f"Report KPI "
                f"'{identifier}' is already registered."
            )

        self._kpis[
            identifier
        ] = kpi

    def unregister(
        self,
        identifier: str,
    ) -> None:
        """
        Remove a registered KPI definition.

        Args:
            identifier:
                KPI code or canonical KPI identifier.

        Raises:
            KeyError:
                When the KPI is not registered.
        """

        normalized_identifier = (
            self._normalize_identifier(
                identifier
            )
        )

        del self._kpis[
            normalized_identifier
        ]

    def get(
        self,
        identifier: str,
    ) -> ReportKPI:
        """
        Retrieve a registered KPI definition.

        Args:
            identifier:
                KPI code or canonical KPI identifier.

        Returns:
            ReportKPI:
                The registered KPI definition.

        Raises:
            KeyError:
                When the KPI is not registered.
        """

        normalized_identifier = (
            self._normalize_identifier(
                identifier
            )
        )

        return self._kpis[
            normalized_identifier
        ]

    def has(
        self,
        identifier: str,
    ) -> bool:
        """
        Determine whether a KPI definition is registered.
        """

        normalized_identifier = (
            self._normalize_identifier(
                identifier
            )
        )

        return (
            normalized_identifier
            in self._kpis
        )

    def all(
        self,
    ) -> tuple[ReportKPI, ...]:
        """
        Return all registered KPI definitions.

        Registration order is preserved.
        """

        return tuple(
            self._kpis.values()
        )

    def count(
        self,
    ) -> int:
        """
        Return the number of registered KPI definitions.
        """

        return len(
            self._kpis
        )

    def clear(
        self,
    ) -> None:
        """
        Remove all registered KPI definitions.
        """

        self._kpis.clear()

    def _normalize_identifier(
        self,
        identifier: str,
    ) -> str:
        """
        Normalize a KPI identifier for registry lookup.
        """

        if not isinstance(
            identifier,
            str,
        ):
            raise ValueError(
                "KPI identifier must be a string."
            )

        normalized_identifier = (
            identifier.strip().lower()
        )

        if not normalized_identifier:

            raise ValueError(
                "KPI identifier is required."
            )

        return normalized_identifier


__all__ = [
    "ReportKPIRegistry",
]
