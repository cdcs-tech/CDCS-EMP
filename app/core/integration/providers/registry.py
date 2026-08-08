"""
CDCS Enterprise Management Platform (CDCS-EMP)

Enterprise Integration Framework

Integration Provider Registry.

Maintains registered integration providers
and provides centralized provider discovery.
"""

from app.core.integration.exceptions import (
    IntegrationRegistrationException,
)

from app.core.integration.providers.base import (
    BaseIntegrationProvider,
)


class IntegrationProviderRegistry:
    """
    Central registry for enterprise
    integration providers.
    """

    def __init__(self):
        """
        Initialize the provider registry.
        """

        self._providers: dict[
            str,
            BaseIntegrationProvider,
        ] = {}


    def register(
        self,
        provider: BaseIntegrationProvider,
    ) -> None:
        """
        Register an integration provider.

        Raises:
            IntegrationRegistrationException:
                When the provider is invalid or
                already registered.
        """

        if not isinstance(
            provider,
            BaseIntegrationProvider,
        ):
            raise IntegrationRegistrationException(
                "Only BaseIntegrationProvider "
                "instances can be registered."
            )


        provider_name = (
            provider.provider_name
        )


        if not provider_name:
            raise IntegrationRegistrationException(
                "Integration provider name is required."
            )


        if provider_name in self._providers:
            raise IntegrationRegistrationException(
                f"Integration provider "
                f"'{provider_name}' "
                f"is already registered."
            )


        self._providers[
            provider_name
        ] = provider


    def get(
        self,
        provider_name: str,
    ) -> BaseIntegrationProvider | None:
        """
        Return a registered provider.
        """

        return self._providers.get(
            provider_name
        )


    def has(
        self,
        provider_name: str,
    ) -> bool:
        """
        Determine whether a provider
        is registered.
        """

        return (
            provider_name
            in self._providers
        )


    def all(
        self,
    ) -> list[BaseIntegrationProvider]:
        """
        Return all registered providers.
        """

        return list(
            self._providers.values()
        )


    def names(
        self,
    ) -> list[str]:
        """
        Return names of all registered
        providers.
        """

        return list(
            self._providers.keys()
        )


    def count(
        self,
    ) -> int:
        """
        Return the number of registered
        providers.
        """

        return len(
            self._providers
        )


    def clear(
        self,
    ) -> None:
        """
        Remove all provider registrations.

        Primarily intended for testing and
        controlled application lifecycle operations.
        """

        self._providers.clear()


    def __iter__(
        self,
    ):
        """
        Iterate over registered providers.
        """

        return iter(
            self._providers.values()
        )


    def __repr__(
        self,
    ) -> str:
        """
        Developer-friendly representation.
        """

        return (
            f"<IntegrationProviderRegistry "
            f"{self.count()} providers>"
        )


integration_provider_registry = (
    IntegrationProviderRegistry()
)
