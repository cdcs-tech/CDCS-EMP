"""
CDCS Enterprise Management Platform (CDCS-EMP)

Reporting & Analytics Framework Tests

Report KPI registry contract tests.
"""

from __future__ import annotations

import pytest

from app.core.reporting import (
    ReportKPI,
    ReportKPIRegistry,
    ReportRegistrationException,
)


def create_kpi(
    code: str = "total_staff",
    name: str = "Total Staff",
    active: bool = True,
) -> ReportKPI:

    return ReportKPI(
        code=code,
        name=name,
        active=active,
    )


def test_kpi_registry_initializes_empty():

    registry = ReportKPIRegistry()

    assert registry.count() == 0
    assert registry.all() == ()


def test_kpi_registry_registers_kpi():

    registry = ReportKPIRegistry()

    kpi = create_kpi()

    registry.register(
        kpi
    )

    assert registry.count() == 1
    assert registry.get(
        "total_staff"
    ) is kpi


def test_kpi_registry_resolves_by_canonical_identifier():

    registry = ReportKPIRegistry()

    kpi = create_kpi(
        code="total_staff"
    )

    registry.register(
        kpi
    )

    assert registry.get(
        "TOTAL_STAFF"
    ) is kpi


@pytest.mark.parametrize(
    "identifier",
    [
        "total_staff",
        "TOTAL_STAFF",
        " Total_Staff ",
        "total_staff ",
        " total_staff",
    ],
)
def test_kpi_registry_normalizes_identifier(
    identifier,
):

    registry = ReportKPIRegistry()

    kpi = create_kpi(
        code="total_staff"
    )

    registry.register(
        kpi
    )

    assert registry.get(
        identifier
    ) is kpi


def test_kpi_registry_accepts_initial_kpis():

    first = create_kpi(
        code="total_staff",
        name="Total Staff",
    )

    second = create_kpi(
        code="active_staff",
        name="Active Staff",
    )

    registry = ReportKPIRegistry(
        [
            first,
            second,
        ]
    )

    assert registry.count() == 2

    assert registry.get(
        "total_staff"
    ) is first

    assert registry.get(
        "active_staff"
    ) is second


def test_kpi_registry_rejects_invalid_kpi():

    registry = ReportKPIRegistry()

    with pytest.raises(
        ReportRegistrationException,
        match="KPI must be a ReportKPI",
    ):
        registry.register(
            object()
        )


def test_kpi_registry_rejects_duplicate_identifier():

    registry = ReportKPIRegistry()

    first = create_kpi(
        code="total_staff",
        name="Total Staff",
    )

    second = create_kpi(
        code="TOTAL_STAFF",
        name="Different Total Staff",
    )

    registry.register(
        first
    )

    with pytest.raises(
        ReportRegistrationException,
        match="already registered",
    ):
        registry.register(
            second
        )


def test_kpi_registry_has_registered_identifier():

    registry = ReportKPIRegistry()

    registry.register(
        create_kpi()
    )

    assert registry.has(
        "total_staff"
    ) is True

    assert registry.has(
        "missing_kpi"
    ) is False


def test_kpi_registry_unregisters_kpi():

    registry = ReportKPIRegistry()

    registry.register(
        create_kpi()
    )

    registry.unregister(
        "total_staff"
    )

    assert registry.count() == 0

    assert registry.has(
        "total_staff"
    ) is False


def test_kpi_registry_get_raises_for_unknown_identifier():

    registry = ReportKPIRegistry()

    with pytest.raises(
        KeyError,
        match="missing_kpi",
    ):
        registry.get(
            "missing_kpi"
        )


def test_kpi_registry_unregister_raises_for_unknown_identifier():

    registry = ReportKPIRegistry()

    with pytest.raises(
        KeyError,
        match="missing_kpi",
    ):
        registry.unregister(
            "missing_kpi"
        )


def test_kpi_registry_all_preserves_registration_order():

    first = create_kpi(
        code="first_kpi",
        name="First KPI",
    )

    second = create_kpi(
        code="second_kpi",
        name="Second KPI",
    )

    third = create_kpi(
        code="third_kpi",
        name="Third KPI",
    )

    registry = ReportKPIRegistry()

    registry.register(first)
    registry.register(second)
    registry.register(third)

    assert registry.all() == (
        first,
        second,
        third,
    )


def test_kpi_registry_count():

    registry = ReportKPIRegistry()

    assert registry.count() == 0

    registry.register(
        create_kpi(
            code="first_kpi",
            name="First KPI",
        )
    )

    assert registry.count() == 1

    registry.register(
        create_kpi(
            code="second_kpi",
            name="Second KPI",
        )
    )

    assert registry.count() == 2


def test_kpi_registry_clear():

    registry = ReportKPIRegistry()

    registry.register(
        create_kpi(
            code="first_kpi",
            name="First KPI",
        )
    )

    registry.register(
        create_kpi(
            code="second_kpi",
            name="Second KPI",
        )
    )

    registry.clear()

    assert registry.count() == 0
    assert registry.all() == ()


def test_kpi_registry_preserves_inactive_kpi_definition():

    registry = ReportKPIRegistry()

    kpi = create_kpi(
        code="inactive_kpi",
        name="Inactive KPI",
        active=False,
    )

    registry.register(
        kpi
    )

    assert registry.get(
        "inactive_kpi"
    ) is kpi

    assert registry.get(
        "inactive_kpi"
    ).active is False


@pytest.mark.parametrize(
    "identifier",
    [
        "",
        " ",
        None,
        123,
        object(),
    ],
)
def test_kpi_registry_rejects_invalid_identifier(
    identifier,
):

    registry = ReportKPIRegistry()

    with pytest.raises(
        ValueError,
        match="KPI identifier",
    ):
        registry.get(
            identifier
        )


def test_public_kpi_registry_is_available():

    from app.core.reporting import (
        ReportKPIRegistry as PublicReportKPIRegistry,
    )

    assert (
        PublicReportKPIRegistry
        is ReportKPIRegistry
    )
