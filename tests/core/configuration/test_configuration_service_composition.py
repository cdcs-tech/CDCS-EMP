"""
CDCS Enterprise Management Platform (CDCS-EMP)

Enterprise Configuration Framework

Configuration service integration and composition tests.
"""

from typing import Any, Optional

from app.core.configuration import (
    ConfigurationDefinition,
    ConfigurationKey,
    ConfigurationProvider,
    ConfigurationRegistry,
    ConfigurationResolutionContext,
    ConfigurationResolver,
    ConfigurationScope,
    ConfigurationValidator,
    ConfigurationValue,
    DefaultConfigurationDefinitionRegistry,
    DefaultConfigurationResolver,
    DefaultConfigurationService,
    MemoryConfigurationProvider,
)


class RecordingProvider(
    ConfigurationProvider
):
    """
    Test provider used to verify service composition.
    """

    def __init__(self) -> None:

        self.values: dict[
            ConfigurationKey,
            ConfigurationValue,
        ] = {}

        self.get_calls = []

        self.set_calls = []

        self.delete_calls = []

        self.exists_calls = []

    def get(
        self,
        key: ConfigurationKey,
    ) -> Optional[ConfigurationValue]:

        self.get_calls.append(
            key
        )

        return self.values.get(
            key
        )

    def set(
        self,
        key: ConfigurationKey,
        value: Any,
    ) -> ConfigurationValue:

        self.set_calls.append(
            (
                key,
                value,
            )
        )

        configuration_value = ConfigurationValue(
            key=key,
            value=value,
            source="recording",
        )

        self.values[
            key
        ] = configuration_value

        return configuration_value

    def delete(
        self,
        key: ConfigurationKey,
    ) -> bool:

        self.delete_calls.append(
            key
        )

        return (
            self.values.pop(
                key,
                None,
            )
            is not None
        )

    def exists(
        self,
        key: ConfigurationKey,
    ) -> bool:

        self.exists_calls.append(
            key
        )

        return key in self.values


class RecordingRegistry(
    ConfigurationRegistry
):
    """
    Test registry used to verify service composition.
    """

    def __init__(self) -> None:

        self.definitions = {}

        self.register_calls = []

        self.get_calls = []

    def register(
        self,
        definition: ConfigurationDefinition,
    ) -> None:

        self.register_calls.append(
            definition
        )

        self.definitions[
            definition.name
        ] = definition

    def get_definition(
        self,
        name: str,
    ) -> Optional[ConfigurationDefinition]:

        self.get_calls.append(
            name
        )

        return self.definitions.get(
            name
        )

    def definitions(
        self,
    ):

        return tuple(
            self.definitions.values()
        )


class RecordingResolver(
    ConfigurationResolver
):
    """
    Test resolver used to verify service composition.
    """

    def __init__(
        self,
        result: Any = "resolved",
    ) -> None:

        self.result = result

        self.calls = []

    def resolve(
        self,
        key: ConfigurationKey,
    ) -> Optional[ConfigurationValue]:

        self.calls.append(
            key
        )

        return self.result


class RecordingValidator(
    ConfigurationValidator
):
    """
    Test validator used to verify dependency injection.
    """

    def __init__(self) -> None:

        super().__init__()

        self.validate_calls = []

        self.validate_default_calls = []

    def validate(
        self,
        key: ConfigurationKey,
        definition: ConfigurationDefinition,
        value: Any,
    ):

        self.validate_calls.append(
            (
                key,
                definition,
                value,
            )
        )

        return super().validate(
            key,
            definition,
            value,
        )

    def validate_default(
        self,
        key: ConfigurationKey,
        definition: ConfigurationDefinition,
    ):

        self.validate_default_calls.append(
            (
                key,
                definition,
            )
        )

        return super().validate_default(
            key,
            definition,
        )


def test_service_preserves_injected_provider():

    provider = RecordingProvider()

    registry = RecordingRegistry()

    service = DefaultConfigurationService(
        provider=provider,
        definition_registry=registry,
    )

    assert service.provider is provider


def test_service_preserves_injected_registry():

    provider = RecordingProvider()

    registry = RecordingRegistry()

    service = DefaultConfigurationService(
        provider=provider,
        definition_registry=registry,
    )

    assert (
        service.definition_registry
        is registry
    )


def test_service_preserves_injected_resolver():

    provider = RecordingProvider()

    registry = RecordingRegistry()

    resolver = DefaultConfigurationResolver()

    service = DefaultConfigurationService(
        provider=provider,
        definition_registry=registry,
        resolver=resolver,
    )

    assert service.resolver is resolver


def test_service_preserves_injected_validator():

    provider = RecordingProvider()

    registry = RecordingRegistry()

    validator = RecordingValidator()

    service = DefaultConfigurationService(
        provider=provider,
        definition_registry=registry,
        validator=validator,
    )

    assert service.validator is validator


def test_default_resolver_uses_injected_validator():

    provider = RecordingProvider()

    registry = RecordingRegistry()

    validator = RecordingValidator()

    service = DefaultConfigurationService(
        provider=provider,
        definition_registry=registry,
        validator=validator,
    )

    assert (
        service.resolver.validator
        is validator
    )


def test_explicit_resolver_is_not_replaced():

    provider = RecordingProvider()

    registry = RecordingRegistry()

    resolver = DefaultConfigurationResolver()

    validator = RecordingValidator()

    service = DefaultConfigurationService(
        provider=provider,
        definition_registry=registry,
        resolver=resolver,
        validator=validator,
    )

    assert service.resolver is resolver

    assert (
        service.resolver.validator
        is not validator
    )


def test_service_set_uses_injected_provider():

    provider = RecordingProvider()

    registry = RecordingRegistry()

    service = DefaultConfigurationService(
        provider=provider,
        definition_registry=registry,
    )

    key = ConfigurationKey(
        name="currency",
        scope=ConfigurationScope.PLATFORM,
    )

    result = service.set(
        key,
        "SSP",
    )

    assert result.value == "SSP"

    assert len(
        provider.set_calls
    ) == 1

    assert (
        provider.set_calls[0]
        == (
            key,
            "SSP",
        )
    )


def test_service_get_uses_injected_provider():

    provider = RecordingProvider()

    registry = RecordingRegistry()

    key = ConfigurationKey(
        name="currency",
        scope=ConfigurationScope.PLATFORM,
    )

    provider.set(
        key,
        "SSP",
    )

    service = DefaultConfigurationService(
        provider=provider,
        definition_registry=registry,
    )

    result = service.get(
        key
    )

    assert result is not None

    assert result.value == "SSP"

    assert (
        provider.get_calls[-1]
        == key
    )


def test_service_delete_uses_injected_provider():

    provider = RecordingProvider()

    registry = RecordingRegistry()

    service = DefaultConfigurationService(
        provider=provider,
        definition_registry=registry,
    )

    key = ConfigurationKey(
        name="currency",
        scope=ConfigurationScope.PLATFORM,
    )

    service.set(
        key,
        "SSP",
    )

    assert service.delete(
        key
    ) is True

    assert (
        provider.delete_calls[-1]
        == key
    )


def test_service_exists_uses_injected_provider():

    provider = RecordingProvider()

    registry = RecordingRegistry()

    service = DefaultConfigurationService(
        provider=provider,
        definition_registry=registry,
    )

    key = ConfigurationKey(
        name="currency",
        scope=ConfigurationScope.PLATFORM,
    )

    assert (
        service.exists(key)
        is False
    )

    service.set(
        key,
        "SSP",
    )

    assert (
        service.exists(key)
        is True
    )

    assert (
        provider.exists_calls[-1]
        == key
    )


def test_service_register_definition_uses_injected_registry():

    provider = RecordingProvider()

    registry = RecordingRegistry()

    service = DefaultConfigurationService(
        provider=provider,
        definition_registry=registry,
    )

    definition = ConfigurationDefinition(
        name="currency",
        value_type=str,
        default="SSP",
    )

    service.register_definition(
        definition
    )

    assert len(
        registry.register_calls
    ) == 1

    assert (
        registry.register_calls[0]
        == definition
    )


def test_service_get_definition_uses_injected_registry():

    provider = RecordingProvider()

    registry = RecordingRegistry()

    definition = ConfigurationDefinition(
        name="currency",
        value_type=str,
    )

    registry.register(
        definition
    )

    service = DefaultConfigurationService(
        provider=provider,
        definition_registry=registry,
    )

    result = service.get_definition(
        "currency"
    )

    assert result == definition

    assert (
        registry.get_calls[-1]
        == "currency"
    )


def test_service_resolution_uses_injected_resolver():

    provider = RecordingProvider()

    registry = RecordingRegistry()

    resolver = RecordingResolver(
        result="custom-resolution"
    )

    service = DefaultConfigurationService(
        provider=provider,
        definition_registry=registry,
        resolver=resolver,
    )

    key = ConfigurationKey(
        name="currency",
        scope=ConfigurationScope.PLATFORM,
    )

    provider.set(
        key,
        "SSP",
    )

    context = ConfigurationResolutionContext()

    result = service.resolve(
        "currency",
        context,
    )

    assert result == "custom-resolution"

    assert len(
        resolver.calls
    ) == 1

    assert (
        resolver.calls[0]
        == key
    )


def test_service_resolution_passes_registered_definition_to_resolver():

    provider = RecordingProvider()

    registry = RecordingRegistry()

    definition = ConfigurationDefinition(
        name="currency",
        value_type=str,
    )

    registry.register(
        definition
    )

    resolver = RecordingResolver(
        result="SSP"
    )

    service = DefaultConfigurationService(
        provider=provider,
        definition_registry=registry,
        resolver=resolver,
    )

    service.set(
        ConfigurationKey(
            name="currency",
            scope=ConfigurationScope.PLATFORM,
        ),
        "SSP",
    )

    context = ConfigurationResolutionContext()

    result = service.resolve(
        "currency",
        context,
    )

    assert result == "SSP"

    assert len(
        resolver.calls
    ) == 1


def test_service_can_use_non_memory_provider():

    provider = RecordingProvider()

    registry = DefaultConfigurationDefinitionRegistry()

    service = DefaultConfigurationService(
        provider=provider,
        definition_registry=registry,
    )

    assert not isinstance(
        service.provider,
        MemoryConfigurationProvider,
    )

    key = ConfigurationKey(
        name="currency",
        scope=ConfigurationScope.PLATFORM,
    )

    result = service.set(
        key,
        "SSP",
    )

    assert result.value == "SSP"


def test_service_composes_all_explicit_dependencies():

    provider = RecordingProvider()

    registry = RecordingRegistry()

    resolver = DefaultConfigurationResolver()

    validator = RecordingValidator()

    service = DefaultConfigurationService(
        provider=provider,
        definition_registry=registry,
        resolver=resolver,
        validator=validator,
    )

    assert service.provider is provider

    assert (
        service.definition_registry
        is registry
    )

    assert service.resolver is resolver

    assert service.validator is validator
