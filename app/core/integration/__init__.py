"""
CDCS Enterprise Management Platform (CDCS-EMP)

Enterprise Integration Framework

Public package interface.
"""

from app.core.integration.exceptions import (
    IntegrationException,
    IntegrationConfigurationException,
    IntegrationRegistrationException,
    IntegrationConnectionException,
    IntegrationAuthenticationException,
    IntegrationTimeoutException,
    IntegrationRequestException,
    IntegrationResponseException,
    IntegrationDeliveryException,
    IntegrationHealthException,
    IntegrationGovernanceException,
)


from app.core.integration.models import (
    IntegrationRequest,
    IntegrationResponse,
    IntegrationResult,
)


from app.core.integration.providers import (
    BaseIntegrationProvider,
    IntegrationProviderRegistry,
    integration_provider_registry,
)


from app.core.integration.service import (
    IntegrationService,
    integration_service,
)


from app.core.integration.health import (
    IntegrationHealthResult,
    IntegrationHealthService,
    integration_health_service,
)


from app.core.integration.audit import (
    IntegrationAuditHook,
    integration_audit_hook,
)


from app.core.integration.events import (
    IntegrationRequestEvent,
    IntegrationResultEvent,
    IntegrationFailureEvent,
)

from app.core.integration.event_hook import (
    IntegrationEventHook,
    integration_event_hook,
)


from app.core.integration.lifecycle import (
    IntegrationLifecycle,
    integration_lifecycle,
)


__all__ = [
    "IntegrationException",
    "IntegrationConfigurationException",
    "IntegrationRegistrationException",
    "IntegrationConnectionException",
    "IntegrationAuthenticationException",
    "IntegrationTimeoutException",
    "IntegrationRequestException",
    "IntegrationResponseException",
    "IntegrationDeliveryException",
    "IntegrationHealthException",
    "IntegrationGovernanceException",
    "IntegrationRequest",
    "IntegrationResponse",
    "IntegrationResult",
    "BaseIntegrationProvider",
    "IntegrationProviderRegistry",
    "integration_provider_registry",
    "IntegrationService",
    "integration_service",
    "IntegrationHealthResult",
    "IntegrationHealthService",
    "integration_health_service",
    "IntegrationAuditHook",
    "integration_audit_hook",
    "IntegrationRequestEvent",
    "IntegrationResultEvent",
    "IntegrationFailureEvent",
    "IntegrationEventHook",
    "integration_event_hook",
    "IntegrationLifecycle",
    "integration_lifecycle",
]

