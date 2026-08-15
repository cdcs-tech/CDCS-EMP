"""
CDCS Enterprise Management Platform (CDCS-EMP)

Enterprise Configuration Framework

Public interface for enterprise configuration
services.
"""


from app.core.configuration.module import (
    ModuleConfiguration,
)

from app.core.configuration.validator import (
    ModuleConfigurationValidator,
    ConfigurationValidationError,
    ConfigurationValidator,
)

from app.core.configuration.loader import (
    ModuleConfigurationLoader,
)

from app.core.configuration.domain import (
    ConfigurationScope,
    ConfigurationKey,
    ConfigurationValue,
    ConfigurationDefinition,
)

from app.core.configuration.contracts import (
    ConfigurationProvider,
    ConfigurationRegistry,
    ConfigurationResolver,
)

from app.core.configuration.exceptions import (
    ConfigurationException,
    ConfigurationContractException,
    ConfigurationNotFoundException,
    ConfigurationValidationException,
    ConfigurationScopeException,
)

from app.core.configuration.registry import (
    DefaultConfigurationRegistry,
)

from app.core.configuration.resolution import (
    ConfigurationResolutionContext,
    DefaultConfigurationResolver,
)

from app.core.configuration.validation import (
    ConfigurationValidationException,
    ConfigurationTypeException,
    ConfigurationRequiredException,
    ConfigurationDefaultException,
    ConfigurationValidationResult,
)

from app.core.configuration.providers import (
    MemoryConfigurationProvider,
)

from app.core.configuration.service import (
    ConfigurationService,
)

from app.core.configuration.definition_registry import (
    DefaultConfigurationDefinitionRegistry,
)

from app.core.configuration.service_impl import (
    DefaultConfigurationService,
)

from app.core.configuration.composition import (
    CONFIGURATION_SERVICE_NAME,
    CONFIGURATION_SERVICE_EXTENSION,
    ConfigurationServiceComponents,
    compose_configuration_service,
    compose_default_configuration_service,
    create_application_configuration_service,
    register_configuration_service,
    get_configuration_service,
    replace_configuration_provider,
    unregister_configuration_service,
)


__all__ = [

    "ModuleConfiguration",
    "ModuleConfigurationValidator",
    "ModuleConfigurationLoader",

    "ConfigurationValidationError",

    "ConfigurationScope",
    "ConfigurationKey",
    "ConfigurationValue",
    "ConfigurationDefinition",

    "ConfigurationProvider",
    "ConfigurationRegistry",
    "ConfigurationResolver",
    "ConfigurationService",

    "DefaultConfigurationRegistry",
    "DefaultConfigurationDefinitionRegistry",
    "DefaultConfigurationResolver",
    "DefaultConfigurationService",

    "ConfigurationException",
    "ConfigurationContractException",
    "ConfigurationNotFoundException",
    "ConfigurationValidationException",
    "ConfigurationTypeException",
    "ConfigurationRequiredException",
    "ConfigurationDefaultException",
    "ConfigurationScopeException",

    "ConfigurationValidationResult",

    "ConfigurationResolutionContext",

    "ConfigurationValidator",
    "MemoryConfigurationProvider",

    "CONFIGURATION_SERVICE_NAME",
    "CONFIGURATION_SERVICE_EXTENSION",

    "ConfigurationServiceComponents",
    "compose_configuration_service",
    "compose_default_configuration_service",
    "create_application_configuration_service",
    "register_configuration_service",
    "get_configuration_service",
    "replace_configuration_provider",
    "unregister_configuration_service",

]
