"""
CDCS Enterprise Management Platform (CDCS-EMP)

Enterprise Services Framework Tests

Service registry tests.
"""

import pytest

from app.core.services import (
    ServiceDefinition,
    ServiceDefinitionException,
    ServiceRegistry,
    ServiceRegistrationException,
    ServiceResolutionException,
)


class ExampleService:
    """
    Test service.
    """

    def execute(self):
        return "ok"


def create_definition(
    module_name="finance",
    service_name="invoice",
):
    return ServiceDefinition(
        module_name=module_name,
        service_name=service_name,
        service_class=ExampleService,
    )


def test_service_definition_creation():

    definition = create_definition()

    assert (
        definition.module_name
        == "finance"
    )

    assert (
        definition.service_name
        == "invoice"
    )

    assert (
        definition.service_class
        is ExampleService
    )


def test_service_definition_normalizes_names():

    definition = ServiceDefinition(
        module_name="  finance  ",
        service_name="  invoice  ",
    )

    assert (
        definition.module_name
        == "finance"
    )

    assert (
        definition.service_name
        == "invoice"
    )


@pytest.mark.parametrize(
    "module_name",
    [
        "",
        "   ",
    ],
)
def test_blank_module_name_is_rejected(
    module_name,
):

    with pytest.raises(
        ServiceDefinitionException
    ):

        ServiceDefinition(
            module_name=module_name,
            service_name="invoice",
        )


@pytest.mark.parametrize(
    "service_name",
    [
        "",
        "   ",
    ],
)
def test_blank_service_name_is_rejected(
    service_name,
):

    with pytest.raises(
        ServiceDefinitionException
    ):

        ServiceDefinition(
            module_name="finance",
            service_name=service_name,
        )


def test_invalid_definition_type_is_rejected():

    registry = ServiceRegistry()

    with pytest.raises(
        ServiceDefinitionException
    ):

        registry.register(
            "invalid"
        )


def test_service_definition_key():

    definition = create_definition()

    assert (
        definition.key
        == "finance.invoice"
    )


def test_service_definition_to_dict():

    definition = create_definition()

    data = definition.to_dict()

    assert (
        data["module_name"]
        == "finance"
    )

    assert (
        data["service_name"]
        == "invoice"
    )

    assert (
        data["key"]
        == "finance.invoice"
    )

    assert (
        data["service_class"]
        == "ExampleService"
    )


def test_service_registration():

    registry = ServiceRegistry()

    definition = create_definition()

    registry.register(
        definition
    )

    assert (
        registry.count()
        == 1
    )

    assert registry.has(
        "finance",
        "invoice",
    )


def test_service_resolution():

    registry = ServiceRegistry()

    definition = create_definition()

    registry.register(
        definition
    )

    resolved = registry.get(
        "finance",
        "invoice",
    )

    assert (
        resolved
        is definition
    )


def test_duplicate_registration_fails():

    registry = ServiceRegistry()

    registry.register(
        create_definition()
    )

    with pytest.raises(
        ServiceRegistrationException
    ):

        registry.register(
            create_definition()
        )


def test_service_replacement():

    registry = ServiceRegistry()

    first = create_definition()

    second = create_definition()

    registry.register(
        first
    )

    registry.register(
        second,
        replace=True,
    )

    assert (
        registry.get(
            "finance",
            "invoice",
        )
        is second
    )


def test_missing_service_resolution_fails():

    registry = ServiceRegistry()

    with pytest.raises(
        ServiceResolutionException
    ):

        registry.get(
            "finance",
            "missing",
        )


def test_missing_service_removal_fails():

    registry = ServiceRegistry()

    with pytest.raises(
        ServiceResolutionException
    ):

        registry.remove(
            "finance",
            "missing",
        )


def test_service_removal():

    registry = ServiceRegistry()

    registry.register(
        create_definition()
    )

    registry.remove(
        "finance",
        "invoice",
    )

    assert (
        registry.count()
        == 0
    )

    assert not registry.has(
        "finance",
        "invoice",
    )


def test_service_listing():

    registry = ServiceRegistry()

    registry.register(
        create_definition(
            "finance",
            "invoice",
        )
    )

    registry.register(
        create_definition(
            "hr",
            "employee",
        )
    )

    assert set(
        registry.names()
    ) == {
        "finance.invoice",
        "hr.employee",
    }


def test_all_returns_copy():

    registry = ServiceRegistry()

    registry.register(
        create_definition()
    )

    services = registry.all()

    services.clear()

    assert (
        registry.count()
        == 1
    )


def test_service_clear():

    registry = ServiceRegistry()

    registry.register(
        create_definition(
            "finance",
            "invoice",
        )
    )

    registry.register(
        create_definition(
            "hr",
            "employee",
        )
    )

    registry.clear()

    assert (
        registry.count()
        == 0
    )


def test_container_iteration():

    registry = ServiceRegistry()

    registry.register(
        create_definition(
            "finance",
            "invoice",
        )
    )

    registry.register(
        create_definition(
            "hr",
            "employee",
        )
    )

    assert set(
        list(registry)
    ) == {
        "finance.invoice",
        "hr.employee",
    }


def test_registry_representation():

    registry = ServiceRegistry()

    registry.register(
        create_definition()
    )

    representation = repr(
        registry
    )

    assert (
        "ServiceRegistry"
        in representation
    )

    assert (
        "1 services"
        in representation
    )


def test_service_instance_is_preserved():

    service = ExampleService()

    definition = ServiceDefinition(
        module_name="finance",
        service_name="invoice",
        service_class=ExampleService,
        instance=service,
    )

    assert (
        definition.instance
        is service
    )
