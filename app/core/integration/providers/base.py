"""
CDCS Enterprise Management Platform (CDCS-EMP)

Enterprise Integration Framework

Base Integration Provider.

Defines the standard contract that all
enterprise integration providers must implement.
"""

from abc import (
    ABC,
    abstractmethod,
)

from app.core.integration.models import (
    IntegrationRequest,
    IntegrationResponse,
)


class BaseIntegrationProvider(
    ABC
):
    """
    Abstract base class for all
    CDCS-EMP integration providers.
    """

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """
        Return the unique provider name.
        """

        raise NotImplementedError


    @property
    def provider_version(self) -> str:
        """
        Return provider implementation version.
        """

        return "1.0.0"


    @abstractmethod
    def execute(
        self,
        request: IntegrationRequest,
    ) -> IntegrationResponse:
        """
        Execute an integration request.

        Every provider must implement this method.
        """

        raise NotImplementedError


    def validate(
        self,
        request: IntegrationRequest,
    ) -> None:
        """
        Validate an integration request.

        Providers may override this method
        when additional provider-specific
        validation is required.
        """

        if not isinstance(
            request,
            IntegrationRequest,
        ):
            raise TypeError(
                "Integration request must be "
                "an IntegrationRequest instance."
            )


    def supports(
        self,
        operation: str,
    ) -> bool:
        """
        Determine whether the provider supports
        a specific integration operation.

        Providers should override this method
        when they expose a defined operation set.
        """

        return True


    def health_check(self) -> bool:
        """
        Perform a basic provider health check.

        Providers may override this method to
        perform actual connectivity verification.
        """

        return True


    def close(self) -> None:
        """
        Release provider resources.

        Providers may override this method when
        they maintain connections or other resources.
        """

        return None


    def __repr__(self) -> str:
        """
        Developer-friendly representation.
        """

        return (
            f"<IntegrationProvider "
            f"{self.provider_name} "
            f"v{self.provider_version}>"
        )

