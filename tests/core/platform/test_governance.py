"""
CDCS Enterprise Management Platform (CDCS-EMP)

Platform Infrastructure Tests

Platform governance tests.
"""

import pytest

from app.core.platform import (
    PlatformComponent,
    PlatformGovernance,
)


def create_component():

    return PlatformComponent(
        name="platform.services",
        component_type="SERVICE",
        version="1.0.0",
        description="Platform service container",
        owner="CDCS-EMP",
        metadata={
            "critical": True,
        },
    )


def test_component_creation():

    component = create_component()

    assert (
        component.name
        == "platform.services"
    )

    assert (
        component.component_type
        == "SERVICE"
    )

    assert (
        component.version
        == "1.0.0"
    )

    assert (
        component.owner
        == "CDCS-EMP"
    )


def test_component_metadata():

    component = create_component()

    assert (
        component.metadata["critical"]
        is True
    )


def test_component_is_immutable():

    component = create_component()

    with pytest.raises(
        Exception
    ):

        component.name = (
            "changed"
        )


def test_component_registration():

    governance = (
        PlatformGovernance()
    )

    component = create_component()

    governance.register(
        component
    )

    assert (
        governance.has(
            "platform.services"
        )
        is True
    )

    assert (
        governance.get(
            "platform.services"
        )
        is component
    )


def test_duplicate_registration_fails():

    governance = (
        PlatformGovernance()
    )

    component = create_component()

    governance.register(
        component
    )

    with pytest.raises(
        ValueError
    ):

        governance.register(
            component
        )


def test_component_replacement():

    governance = (
        PlatformGovernance()
    )

    first = create_component()

    second = PlatformComponent(
        name="platform.services",
        component_type="SERVICE",
        version="2.0.0",
    )

    governance.register(
        first
    )

    governance.register(
        second,
        replace=True,
    )

    assert (
        governance.get(
            "platform.services"
        )
        is second
    )

    assert (
        governance.get(
            "platform.services"
        ).version
        == "2.0.0"
    )


def test_governance_listing():

    governance = (
        PlatformGovernance()
    )

    governance.register(
        create_component()
    )

    governance.register(
        PlatformComponent(
            name="platform.logging",
            component_type="LOGGER",
        )
    )

    assert (
        governance.count()
        == 2
    )

    assert len(
        governance.all()
    ) == 2


def test_governance_validation():

    governance = (
        PlatformGovernance()
    )

    governance.register(
        create_component()
    )

    assert (
        governance.validate()
        is True
    )


def test_governance_clear():

    governance = (
        PlatformGovernance()
    )

    governance.register(
        create_component()
    )

    governance.clear()

    assert (
        governance.count()
        == 0
    )

    assert (
        governance.validate()
        is True
    )


def test_governance_repr():

    governance = (
        PlatformGovernance()
    )

    governance.register(
        create_component()
    )

    representation = repr(
        governance
    )

    assert (
        "PlatformGovernance"
        in representation
    )

    assert (
        "1 components"
        in representation
    )


def test_empty_component_name_fails():

    governance = (
        PlatformGovernance()
    )

    component = PlatformComponent(
        name="",
        component_type="SERVICE",
    )

    with pytest.raises(
        ValueError
    ):

        governance.register(
            component
        )


def test_empty_component_type_fails():

    governance = (
        PlatformGovernance()
    )

    component = PlatformComponent(
        name="test",
        component_type="",
    )

    with pytest.raises(
        ValueError
    ):

        governance.register(
            component
        )
