"""
CDCS Enterprise Management Platform (CDCS-EMP)

Platform Infrastructure Tests

Platform service container tests.
"""

import pytest

from app.core.platform import (
    PlatformServiceContainer,
    ServiceRegistrationException,
    ServiceResolutionException,
)


class ExampleService:
    """
    Test service.
    """

    def execute(self):
        return "ok"


def test_service_registration():

    container = (
        PlatformServiceContainer()
    )

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
        container.get("example")
        is service
    )


def test_service_resolution():

    container = (
        PlatformServiceContainer()
    )

    service = ExampleService()

    container.register(
        "example",
        service,
    )

    resolved = container.get(
        "example"
    )

    assert (
        resolved.execute()
        == "ok"
    )


def test_duplicate_registration_fails():

    container = (
        PlatformServiceContainer()
    )

    container.register(
        "example",
        ExampleService(),
    )

    with pytest.raises(
        ServiceRegistrationException
    ):

        container.register(
            "example",
            ExampleService(),
        )


def test_service_replacement():

    container = (
        PlatformServiceContainer()
    )

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
        container.get("example")
        is second
    )


def test_missing_service_resolution_fails():

    container = (
        PlatformServiceContainer()
    )

    with pytest.raises(
        ServiceResolutionException
    ):

        container.get(
            "missing"
        )


def test_invalid_registration_name():

    container = (
        PlatformServiceContainer()
    )

    with pytest.raises(
        ServiceRegistrationException
    ):

        container.register(
            "",
            ExampleService(),
        )


def test_none_service_registration_fails():

    container = (
        PlatformServiceContainer()
    )

    with pytest.raises(
        ServiceRegistrationException
    ):

        container.register(
            "example",
            None,
        )


def test_service_listing():

    container = (
        PlatformServiceContainer()
    )

    container.register(
        "service_a",
        ExampleService(),
    )

    container.register(
        "service_b",
        ExampleService(),
    )

    assert (
        container.count()
        == 2
    )

    assert set(
        container.names()
    ) == {
        "service_a",
        "service_b",
    }


def test_all_returns_copy():

    container = (
        PlatformServiceContainer()
    )

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

    container = (
        PlatformServiceContainer()
    )

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

    with pytest.raises(
        ServiceResolutionException
    ):

        container.remove(
            "example"
        )


def test_service_clear():

    container = (
        PlatformServiceContainer()
    )

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

    container = (
        PlatformServiceContainer()
    )

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


def test_container_representation():

    container = (
        PlatformServiceContainer()
    )

    container.register(
        "example",
        ExampleService(),
    )

    representation = repr(
        container
    )

    assert (
        "PlatformServiceContainer"
        in representation
    )

    assert (
        "1 services"
        in representation
    )

