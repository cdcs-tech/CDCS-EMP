"""
CDCS Enterprise Management Platform (CDCS-EMP)

Enterprise Integration Framework

Integration Health.

Provides standardized health-check services
for registered integration providers.
"""

from dataclasses import (
    dataclass,
    field,
)
from datetime import (
    datetime,
    timezone,
)
from typing import Any


@dataclass(slots=True)
class IntegrationHealthResult:
    """
    Represents the health status of an
    integration provider.
    """

    provider: str

    healthy: bool

    message: str = ""

    checked_at: datetime = field(
        default_factory=lambda:
        datetime.now(timezone.utc)
    )

    metadata: dict[str, Any] = field(
        default_factory=dict
    )

    @property
    def status(self) -> str:
        """
        Return normalized health status.
        """

        return (
            "HEALTHY"
            if self.healthy
            else "UNHEALTHY"
        )


class IntegrationHealthService:
    """
    Service responsible for checking the
    health of registered integration providers.
    """

    def __init__(
        self,
        provider_registry=None,
    ):
        """
        Initialize the health service.
        """

        from app.core.integration.providers.registry import (
            integration_provider_registry,
        )

        self.provider_registry = (
            provider_registry
            or integration_provider_registry
        )


    def check(
        self,
        provider_name: str,
    ) -> IntegrationHealthResult:
        """
        Check the health of one provider.
        """

        provider = (
            self.provider_registry.get(
                provider_name
            )
        )

        if provider is None:

            return IntegrationHealthResult(
                provider=provider_name,
                healthy=False,
                message=(
                    "Integration provider "
                    "is not registered."
                ),
            )

        try:

            healthy = provider.health_check()

            return IntegrationHealthResult(
                provider=provider_name,
                healthy=bool(healthy),
                message=(
                    "Integration provider "
                    "is healthy."
                    if healthy
                    else
                    "Integration provider "
                    "is unhealthy."
                ),
            )

        except Exception as exc:

            return IntegrationHealthResult(
                provider=provider_name,
                healthy=False,
                message=(
                    "Integration provider "
                    "health check failed."
                ),
                metadata={
                    "exception": (
                        type(exc).__name__
                    )
                },
            )


    def check_all(
        self,
    ) -> list[IntegrationHealthResult]:
        """
        Check the health of all registered
        integration providers.
        """

        results = []

        for provider in (
            self.provider_registry.all()
        ):

            results.append(
                self.check(
                    provider.provider_name
                )
            )

        return results


    def healthy(
        self,
        provider_name: str,
    ) -> bool:
        """
        Return True when the specified provider
        is healthy.
        """

        return self.check(
            provider_name
        ).healthy


    def healthy_count(
        self,
    ) -> int:
        """
        Return the number of healthy providers.
        """

        return sum(
            result.healthy
            for result in self.check_all()
        )


    def unhealthy_count(
        self,
    ) -> int:
        """
        Return the number of unhealthy providers.
        """

        return sum(
            not result.healthy
            for result in self.check_all()
        )


    def __repr__(
        self,
    ) -> str:
        """
        Developer-friendly representation.
        """

        return (
            f"<IntegrationHealthService "
            f"providers="
            f"{self.provider_registry.count()}>"
        )


integration_health_service = (
    IntegrationHealthService()
)

