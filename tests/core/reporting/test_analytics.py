"""
CDCS Enterprise Management Platform (CDCS-EMP)

Reporting & Analytics Framework Tests

Analytics and KPI contract tests.
"""

from __future__ import annotations

import pytest

from app.core.reporting import (
    ReportKPI,
    ReportKPIValueType,
)


def test_report_kpi_value_type_is_string_enum():

    assert issubclass(
        ReportKPIValueType,
        str,
    )


@pytest.mark.parametrize(
    "member, expected",
    [
        (
            ReportKPIValueType.INTEGER,
            "integer",
        ),
        (
            ReportKPIValueType.DECIMAL,
            "decimal",
        ),
        (
            ReportKPIValueType.PERCENTAGE,
            "percentage",
        ),
        (
            ReportKPIValueType.CURRENCY,
            "currency",
        ),
        (
            ReportKPIValueType.RATIO,
            "ratio",
        ),
        (
            ReportKPIValueType.BOOLEAN,
            "boolean",
        ),
        (
            ReportKPIValueType.TEXT,
            "text",
        ),
    ],
)
def test_report_kpi_value_type_values(
    member,
    expected,
):

    assert member.value == expected


@pytest.mark.parametrize(
    "value, expected",
    [
        (
            "integer",
            ReportKPIValueType.INTEGER,
        ),
        (
            "INTEGER",
            ReportKPIValueType.INTEGER,
        ),
        (
            " integer ",
            ReportKPIValueType.INTEGER,
        ),
        (
            "decimal",
            ReportKPIValueType.DECIMAL,
        ),
        (
            "percentage",
            ReportKPIValueType.PERCENTAGE,
        ),
        (
            "currency",
            ReportKPIValueType.CURRENCY,
        ),
        (
            "ratio",
            ReportKPIValueType.RATIO,
        ),
        (
            "boolean",
            ReportKPIValueType.BOOLEAN,
        ),
        (
            "text",
            ReportKPIValueType.TEXT,
        ),
    ],
)
def test_report_kpi_normalizes_value_type(
    value,
    expected,
):

    kpi = ReportKPI(
        code="test.kpi",
        name="Test KPI",
        value_type=value,
    )

    assert kpi.value_type is expected


@pytest.mark.parametrize(
    "value",
    [
        "",
        " ",
        "unsupported",
        "date",
        "list",
        None,
        123,
        object(),
    ],
)
def test_report_kpi_rejects_invalid_value_type(
    value,
):

    with pytest.raises(
        ValueError,
        match="Report KPI value_type",
    ):
        ReportKPI(
            code="test.kpi",
            name="Test KPI",
            value_type=value,
        )


def test_report_kpi_creates_minimal_definition():

    kpi = ReportKPI(
        code="sales.total",
        name="Total Sales",
    )

    assert kpi.code == "sales.total"
    assert kpi.name == "Total Sales"
    assert kpi.description is None
    assert (
        kpi.value_type
        is ReportKPIValueType.DECIMAL
    )
    assert kpi.unit is None
    assert kpi.category is None
    assert kpi.metadata == {}
    assert kpi.active is True


def test_report_kpi_normalizes_string_fields():

    kpi = ReportKPI(
        code="  sales.total  ",
        name="  Total Sales  ",
        description="  Total value of sales.  ",
        unit="  USD  ",
        category="  Finance  ",
    )

    assert kpi.code == "sales.total"
    assert kpi.name == "Total Sales"
    assert kpi.description == "Total value of sales."
    assert kpi.unit == "USD"
    assert kpi.category == "Finance"


def test_report_kpi_converts_blank_optional_strings_to_none():

    kpi = ReportKPI(
        code="sales.total",
        name="Total Sales",
        description=" ",
        unit=" ",
        category=" ",
    )

    assert kpi.description is None
    assert kpi.unit is None
    assert kpi.category is None


@pytest.mark.parametrize(
    "field, value, message",
    [
        (
            "code",
            None,
            "Report KPI code",
        ),
        (
            "code",
            123,
            "Report KPI code",
        ),
        (
            "name",
            None,
            "Report KPI name",
        ),
        (
            "name",
            123,
            "Report KPI name",
        ),
        (
            "description",
            123,
            "Report KPI description",
        ),
        (
            "unit",
            123,
            "Report KPI unit",
        ),
        (
            "category",
            123,
            "Report KPI category",
        ),
        (
            "metadata",
            [],
            "Report KPI metadata",
        ),
        (
            "active",
            "true",
            "Report KPI active",
        ),
    ],
)
def test_report_kpi_rejects_invalid_fields(
    field,
    value,
    message,
):

    kwargs = {
        "code": "test.kpi",
        "name": "Test KPI",
        field: value,
    }

    with pytest.raises(
        ValueError,
        match=message,
    ):
        ReportKPI(
            **kwargs
        )


@pytest.mark.parametrize(
    "code, name, message",
    [
        (
            "",
            "Test KPI",
            "Report KPI code",
        ),
        (
            " ",
            "Test KPI",
            "Report KPI code",
        ),
        (
            "test.kpi",
            "",
            "Report KPI name",
        ),
        (
            "test.kpi",
            " ",
            "Report KPI name",
        ),
    ],
)
def test_report_kpi_rejects_missing_required_strings(
    code,
    name,
    message,
):

    with pytest.raises(
        ValueError,
        match=message,
    ):
        ReportKPI(
            code=code,
            name=name,
        )


def test_report_kpi_identifier_is_canonical():

    kpi = ReportKPI(
        code="sales.total",
        name="Total Sales",
    )

    assert kpi.identifier == "SALES.TOTAL"


def test_report_kpi_metadata_is_copied():

    metadata = {
        "domain": "finance",
        "owner": "reporting",
    }

    kpi = ReportKPI(
        code="sales.total",
        name="Total Sales",
        metadata=metadata,
    )

    metadata["domain"] = "changed"

    assert kpi.metadata == {
        "domain": "finance",
        "owner": "reporting",
    }


def test_report_kpi_metadata_is_copied_by_to_dict():

    kpi = ReportKPI(
        code="sales.total",
        name="Total Sales",
        metadata={
            "domain": "finance",
        },
    )

    result = kpi.to_dict()

    result["metadata"]["domain"] = "changed"

    assert kpi.metadata == {
        "domain": "finance",
    }


def test_report_kpi_to_dict():

    kpi = ReportKPI(
        code="sales.total",
        name="Total Sales",
        description="Total value of sales.",
        value_type=ReportKPIValueType.CURRENCY,
        unit="USD",
        category="Finance",
        metadata={
            "owner": "reporting",
        },
        active=True,
    )

    assert kpi.to_dict() == {
        "code": "sales.total",
        "name": "Total Sales",
        "description": "Total value of sales.",
        "value_type": "currency",
        "unit": "USD",
        "category": "Finance",
        "metadata": {
            "owner": "reporting",
        },
        "active": True,
    }


def test_report_kpi_supports_inactive_definition():

    kpi = ReportKPI(
        code="legacy.sales",
        name="Legacy Sales",
        active=False,
    )

    assert kpi.active is False


def test_report_kpi_accepts_enum_value_type():

    kpi = ReportKPI(
        code="sales.count",
        name="Sales Count",
        value_type=ReportKPIValueType.INTEGER,
    )

    assert (
        kpi.value_type
        is ReportKPIValueType.INTEGER
    )


def test_report_kpi_is_immutable():

    kpi = ReportKPI(
        code="sales.total",
        name="Total Sales",
    )

    with pytest.raises(
        AttributeError,
    ):
        kpi.code = "changed"


def test_report_kpi_members_are_unique():

    values = [
        value_type.value
        for value_type in ReportKPIValueType
    ]

    assert len(values) == len(
        set(values)
    )


def test_public_report_kpi_is_available():

    from app.core.reporting import (
        ReportKPI as PublicReportKPI,
    )

    assert (
        PublicReportKPI
        is ReportKPI
    )


def test_public_report_kpi_value_type_is_available():

    from app.core.reporting import (
        ReportKPIValueType as PublicReportKPIValueType,
    )

    assert (
        PublicReportKPIValueType
        is ReportKPIValueType
    )
