"""
CDCS Enterprise Management Platform (CDCS-EMP)

Enterprise Services Framework Tests

Service container tests.
"""

import pytest
from flask import Flask

from app.core.services import (
    ServiceAlreadyRegisteredException,
    ServiceContainer,
    ServiceContainerException,
    ServiceNotRegisteredException,
)


class ExampleService:
    """
    Test service.
    """

    def execute(self):
        return "ok"


def create_container():

    return ServiceContainer()


def test_container_creation():

    container = create_container()

    assert (
        container.count()
        == 0
    )


def test_service_registration():

    container = create_container()

    service = ExampleService()

    container.register(
        "example",
        service,
    )

    assert (
        container.has("example")
        is True
    )

    assert (
        container.resolve("example")
        is service
    )


def test_service_resolution():

    container = create_container()

    service = ExampleService()

    container.register(
        "example",
        service,
    )

    resolved = container.resolve(
        "example"
    )

    assert (
        resolved.execute()
        == "ok"
    )


def test_duplicate_registration_fails():

    container = create_container()

    container.register(
        "example",
        ExampleService(),
    )

    with pytest.raises(
        ServiceAlreadyRegisteredException
    ):

        container.register(
            "example",
            ExampleService(),
        )


def test_service_replacement():

    container = create_container()

    first = ExampleService()
    second = ExampleService()

    container.register(
        "example",
        first,
    )

    container.register(
        "example",
        second,
        replace=True,
    )

    assert (
        container.resolve("example")
        is second
    )


def test_missing_service_resolution_fails():

    container = create_container()

    with pytest.raises(
        ServiceNotRegisteredException
    ):

        container.resolve(
            "missing"
        )


def test_invalid_service_name_fails():

    container = create_container()

    with pytest.raises(
        ServiceContainerException
    ):

        container.register(
            "",
            ExampleService(),
        )


def test_blank_service_name_fails():

    container = create_container()

    with pytest.raises(
        ServiceContainerException
    ):

        container.register(
            "   ",
            ExampleService(),
        )


def test_none_service_fails():

    container = create_container()

    with pytest.raises(
        ServiceContainerException
    ):

        container.register(
            "example",
            None,
        )


def test_service_name_is_normalized():

    container = create_container()

    service = ExampleService()

    container.register(
        "  example  ",
        service,
    )

    assert (
        container.has("example")
        is True
    )

    assert (
        container.resolve("example")
        is service
    )


def test_service_listing():

    container = create_container()

    container.register(
        "service_a",
        ExampleService(),
    )

    container.register(
        "service_b",
        ExampleService(),
    )

    assert container.names() == [
        "service_a",
        "service_b",
    ]

    assert (
        container.count()
        == 2
    )


def test_all_returns_copy():

    container = create_container()

    container.register(
        "example",
        ExampleService(),
    )

    services = container.all()

    services.clear()

    assert (
        container.count()
        == 1
    )


def test_service_removal():

    container = create_container()

    container.register(
        "example",
        ExampleService(),
    )

    container.remove(
        "example"
    )

    assert (
        container.has("example")
        is False
    )


def test_removing_missing_service_fails():

    container = create_container()

    with pytest.raises(
        ServiceNotRegisteredException
    ):

        container.remove(
            "missing"
        )


def test_service_clear():

    container = create_container()

    container.register(
        "service_a",
        ExampleService(),
    )

    container.register(
        "service_b",
        ExampleService(),
    )

    container.clear()

    assert (
        container.count()
        == 0
    )


def test_container_iteration():

    container = create_container()

    container.register(
        "service_a",
        ExampleService(),
    )

    container.register(
        "service_b",
        ExampleService(),
    )

    assert set(
        list(container)
    ) == {
        "service_a",
        "service_b",
    }


def test_container_membership():

    container = create_container()

    container.register(
        "example",
        ExampleService(),
    )

    assert (
        "example"
        in container
    )

    assert (
        "missing"
        not in container
    )


def test_register_with_application():

    app = Flask(
        "test_application"
    )

    container = create_container()

    container.register_with_app(
        app
    )

    assert (
        app.extensions[
            "service_container"
        ]
        is container
    )


def test_resolve_container_from_application():

    app = Flask(
        "test_application"
    )

    container = create_container()

    container.register_with_app(
        app
    )

    resolved = (
        ServiceContainer.from_app(
            app
        )
    )

    assert resolved is container


def test_missing_application_container_fails():

    app = Flask(
        "test_application"
    )

    with pytest.raises(
        ServiceContainerException
    ):

        ServiceContainer.from_app(
            app
        )


def test_container_representation():

    container = create_container()

    container.register(
        "example",
        ExampleService(),
    )

    representation = repr(
        container
    )

    assert (
        "ServiceContainer"
        in representation
    )

    assert (
        "1 services"
        in representation
    )
