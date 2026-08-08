"""
CDCS Enterprise Management Platform (CDCS-EMP)

Enterprise Integration Framework

Integration Service.

Central orchestration service responsible for
executing standardized integration requests
through registered integration providers.
"""

from time import perf_counter

from app.core.integration.exceptions import (
    IntegrationDeliveryException,
    IntegrationRegistrationException,
    IntegrationRequestException,
)

from app.core.integration.models import (
    IntegrationRequest,
    IntegrationResponse,
    IntegrationResult,
)

from app.core.integration.providers.registry import (
    integration_provider_registry,
)


class IntegrationService:
    """
    Central enterprise integration service.
    """

    def __init__(
        self,
        provider_registry=None,
    ):
        """
        Initialize the integration service.
        """

        self.provider_registry = (
            provider_registry
            or integration_provider_registry
        )


    def execute(
        self,
        request: IntegrationRequest,
    ) -> IntegrationResult:
        """
        Execute an integration request.

        The service:

        1. validates the request;
        2. resolves the provider;
        3. validates provider compatibility;
        4. executes the provider;
        5. normalizes the response;
        6. returns an IntegrationResult.
        """

        if not isinstance(
            request,
            IntegrationRequest,
        ):
            raise IntegrationRequestException(
                "Integration request must be "
                "an IntegrationRequest instance."
            )


        provider = (
            self.provider_registry.get(
                request.provider
            )
        )


        if provider is None:

            raise IntegrationRegistrationException(
                f"Integration provider "
                f"'{request.provider}' "
                f"is not registered."
            )


        try:

            provider.validate(
                request
            )

        except Exception as exc:

            raise IntegrationRequestException(
                "Integration request validation failed."
            ) from exc


        if not provider.supports(
            request.operation
        ):

            raise IntegrationRequestException(
                f"Integration provider "
                f"'{request.provider}' "
                f"does not support operation "
                f"'{request.operation}'."
            )


        started_at = perf_counter()


        try:

            response = provider.execute(
                request
            )

        except Exception as exc:

            raise IntegrationDeliveryException(
                f"Integration provider "
                f"'{request.provider}' "
                f"execution failed."
            ) from exc


        duration_ms = (
            perf_counter()
            - started_at
        ) * 1000


        if not isinstance(
            response,
            IntegrationResponse,
        ):

            raise IntegrationDeliveryException(
                f"Integration provider "
                f"'{request.provider}' "
                f"returned an invalid response."
            )


        if response.request_id is None:

            response.request_id = (
                request.request_id
            )


        return IntegrationResult(
            request=request,
            response=response,
            duration_ms=duration_ms,
            provider=request.provider,
            operation=request.operation,
        )


    def has_provider(
        self,
        provider_name: str,
    ) -> bool:
        """
        Determine whether an integration provider
        is registered.
        """

        return self.provider_registry.has(
            provider_name
        )


    def provider_count(
        self,
    ) -> int:
        """
        Return the number of registered
        integration providers.
        """

        return self.provider_registry.count()


    def __repr__(
        self,
    ) -> str:
        """
        Developer-friendly representation.
        """

        return (
            f"<IntegrationService "
            f"providers="
            f"{self.provider_count()}>"
        )


integration_service = IntegrationService()

