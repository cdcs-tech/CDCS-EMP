"""
CDCS Enterprise Management Platform (CDCS-EMP)

Reporting Framework

Report data provider registration and resolution.
"""

from __future__ import annotations

from typing import Iterable

from app.core.reporting.exceptions import (
    ReportRegistrationException,
)
from app.core.reporting.data_providers import (
    ReportDataProvider,
)
from app.core.reporting.queries import (
    ReportQuery,
)


class ReportDataProviderRegistry:
    """
    Registry responsible for registering and resolving
    report data providers.

    The registry owns provider discovery and selection only.

    Query execution, authorization, governance, auditing,
    telemetry, persistence, and presentation remain outside
    this contract.
    """

    def __init__(
        self,
        providers: Iterable[
            ReportDataProvider
        ] | None = None,
    ) -> None:
        """
        Initialize the provider registry.

        Args:
            providers:
                Optional initial provider collection.

        Raises:
            ReportRegistrationException:
                When an invalid provider is supplied.
        """

        self._providers: dict[
            str,
            ReportDataProvider,
        ] = {}

        if providers is not None:

            for provider in providers:

                self.register(
                    provider
                )

    def register(
        self,
        provider: ReportDataProvider,
    ) -> None:
        """
        Register a report data provider.

        Provider names are canonicalized to lowercase.

        Raises:
            ReportRegistrationException:
                When the provider is invalid or already
                registered.
        """

        if not isinstance(
            provider,
            ReportDataProvider,
        ):
            raise ReportRegistrationException(
                "Provider must implement "
                "ReportDataProvider."
            )

        name = provider.name

        if not isinstance(
            name,
            str,
        ):
            raise ReportRegistrationException(
                "Provider name must be a string."
            )

        normalized_name = name.strip().lower()

        if not normalized_name:
            raise ReportRegistrationException(
                "Provider name is required."
            )

        if normalized_name in self._providers:
            raise ReportRegistrationException(
                f"Report data provider "
                f"'{normalized_name}' is already registered."
            )

        self._providers[
            normalized_name
        ] = provider

    def unregister(
        self,
        name: str,
    ) -> None:
        """
        Remove a registered provider.

        Raises:
            KeyError:
                When no provider with the supplied name
                is registered.
        """

        normalized_name = (
            self._normalize_name(name)
        )

        del self._providers[
            normalized_name
        ]

    def get(
        self,
        name: str,
    ) -> ReportDataProvider:
        """
        Retrieve a registered provider by name.

        Raises:
            KeyError:
                When the provider is not registered.
        """

        normalized_name = (
            self._normalize_name(name)
        )

        return self._providers[
            normalized_name
        ]

    def has(
        self,
        name: str,
    ) -> bool:
        """
        Determine whether a provider is registered.
        """

        normalized_name = (
            self._normalize_name(name)
        )

        return (
            normalized_name
            in self._providers
        )

    def all(
        self,
    ) -> tuple[
        ReportDataProvider,
        ...,
    ]:
        """
        Return all registered providers.

        Registration order is preserved.
        """

        return tuple(
            self._providers.values()
        )

    def resolve(
        self,
        query: ReportQuery,
    ) -> ReportDataProvider:
        """
        Resolve the first provider that supports
        the supplied query.

        Provider registration order determines
        precedence.

        Raises:
            ReportRegistrationException:
                When no registered provider supports
                the query.
        """

        if not isinstance(
            query,
            ReportQuery,
        ):
            raise ReportRegistrationException(
                "Query must be a ReportQuery."
            )

        for provider in self._providers.values():

            if provider.supports(
                query
            ):
                return provider

        raise ReportRegistrationException(
            "No registered report data provider "
            f"supports report query "
            f"'{query.identifier}'."
        )

    def _normalize_name(
        self,
        name: str,
    ) -> str:
        """
        Normalize a provider name.
        """

        if not isinstance(
            name,
            str,
        ):
            raise ValueError(
                "Provider name must be a string."
            )

        normalized_name = (
            name.strip().lower()
        )

        if not normalized_name:
            raise ValueError(
                "Provider name is required."
            )

        return normalized_name


__all__ = [
    "ReportDataProviderRegistry",
]
