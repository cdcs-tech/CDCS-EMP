"""
CDCS Enterprise Management Platform (CDCS-EMP)

Reporting Framework Tests

Report parameter binding and validation tests.
"""

from datetime import date, datetime
from decimal import Decimal

import pytest

from app.core.reporting import (
    ReportParameter,
    ReportParameterBinder,
    ReportParameterCollection,
    ReportParameterType,
    ReportValidationException,
)


def create_definitions():

    collection = ReportParameterCollection()

    collection.add(
        ReportParameter(
            name="year",
            label="Year",
            data_type=ReportParameterType.INTEGER,
            required=True,
        )
    )

    collection.add(
        ReportParameter(
            name="department",
            label="Department",
            required=False,
            default_value="Finance",
        )
    )

    collection.add(
        ReportParameter(
            name="active",
            label="Active",
            data_type=ReportParameterType.BOOLEAN,
            default_value=True,
        )
    )

    return collection


def test_binder_accepts_valid_parameters():

    binder = ReportParameterBinder()

    result = binder.bind(
        create_definitions(),
        {
            "year": 2026,
            "department": "HR",
            "active": False,
        },
    )

    assert len(result) == 3

    assert result.get(
        "year"
    ).value == 2026

    assert result.get(
        "department"
    ).value == "HR"

    assert result.get(
        "active"
    ).value is False


def test_binder_applies_default_values():

    binder = ReportParameterBinder()

    result = binder.bind(
        create_definitions(),
        {
            "year": 2026,
        },
    )

    department = result.get(
        "department"
    )

    active = result.get(
        "active"
    )

    assert department.value == "Finance"

    assert department.defaulted is True

    assert active.value is True

    assert active.defaulted is True


def test_binder_rejects_missing_required_parameter():

    binder = ReportParameterBinder()

    with pytest.raises(
        ReportValidationException,
        match="Required report parameter 'year'",
    ):

        binder.bind(
            create_definitions(),
            {},
        )


def test_binder_rejects_unknown_parameter():

    binder = ReportParameterBinder()

    with pytest.raises(
        ReportValidationException,
        match="Unknown report parameter 'unknown'",
    ):

        binder.bind(
            create_definitions(),
            {
                "year": 2026,
                "unknown": "value",
            },
        )


def test_binder_converts_integer():

    definitions = ReportParameterCollection()

    definitions.add(
        ReportParameter(
            name="year",
            label="Year",
            data_type=ReportParameterType.INTEGER,
        )
    )

    result = ReportParameterBinder().bind(
        definitions,
        {
            "year": "2026",
        },
    )

    assert result.get(
        "year"
    ).value == 2026

    assert isinstance(
        result.get(
            "year"
        ).value,
        int,
    )


def test_binder_converts_float():

    definitions = ReportParameterCollection()

    definitions.add(
        ReportParameter(
            name="rate",
            label="Rate",
            data_type=ReportParameterType.FLOAT,
        )
    )

    result = ReportParameterBinder().bind(
        definitions,
        {
            "rate": "12.5",
        },
    )

    assert result.get(
        "rate"
    ).value == 12.5


def test_binder_converts_boolean():

    definitions = ReportParameterCollection()

    definitions.add(
        ReportParameter(
            name="active",
            label="Active",
            data_type=ReportParameterType.BOOLEAN,
        )
    )

    result = ReportParameterBinder().bind(
        definitions,
        {
            "active": "true",
        },
    )

    assert result.get(
        "active"
    ).value is True


def test_binder_converts_date():

    definitions = ReportParameterCollection()

    definitions.add(
        ReportParameter(
            name="start_date",
            label="Start Date",
            data_type=ReportParameterType.DATE,
        )
    )

    result = ReportParameterBinder().bind(
        definitions,
        {
            "start_date": "2026-01-15",
        },
    )

    assert result.get(
        "start_date"
    ).value == date(
        2026,
        1,
        15,
    )


def test_binder_converts_datetime():

    definitions = ReportParameterCollection()

    definitions.add(
        ReportParameter(
            name="run_at",
            label="Run At",
            data_type=ReportParameterType.DATETIME,
        )
    )

    result = ReportParameterBinder().bind(
        definitions,
        {
            "run_at": "2026-01-15T10:30:00",
        },
    )

    assert result.get(
        "run_at"
    ).value == datetime(
        2026,
        1,
        15,
        10,
        30,
    )


def test_binder_converts_decimal():

    definitions = ReportParameterCollection()

    definitions.add(
        ReportParameter(
            name="amount",
            label="Amount",
            data_type=ReportParameterType.DECIMAL,
        )
    )

    result = ReportParameterBinder().bind(
        definitions,
        {
            "amount": "1250.75",
        },
    )

    assert result.get(
        "amount"
    ).value == Decimal(
        "1250.75"
    )


def test_binder_rejects_invalid_type():

    definitions = ReportParameterCollection()

    definitions.add(
        ReportParameter(
            name="year",
            label="Year",
            data_type=ReportParameterType.INTEGER,
        )
    )

    with pytest.raises(
        ReportValidationException,
        match="Invalid value",
    ):

        ReportParameterBinder().bind(
            definitions,
            {
                "year": "not-a-number",
            },
        )


def test_binder_rejects_invalid_allowed_value():

    definitions = ReportParameterCollection()

    definitions.add(
        ReportParameter(
            name="department",
            label="Department",
            allowed_values=[
                "Finance",
                "HR",
                "Logistics",
            ],
        )
    )

    with pytest.raises(
        ReportValidationException,
        match="not allowed",
    ):

        ReportParameterBinder().bind(
            definitions,
            {
                "department": "Unknown",
            },
        )


def test_binder_accepts_allowed_value():

    definitions = ReportParameterCollection()

    definitions.add(
        ReportParameter(
            name="department",
            label="Department",
            allowed_values=[
                "Finance",
                "HR",
                "Logistics",
            ],
        )
    )

    result = ReportParameterBinder().bind(
        definitions,
        {
            "department": "HR",
        },
    )

    assert result.get(
        "department"
    ).value == "HR"


def test_binder_normalizes_parameter_names():

    definitions = ReportParameterCollection()

    definitions.add(
        ReportParameter(
            name="year",
            label="Year",
            data_type=ReportParameterType.INTEGER,
        )
    )

    result = ReportParameterBinder().bind(
        definitions,
        {
            "  year  ": "2026",
        },
    )

    assert result.get(
        "year"
    ).value == 2026


def test_binder_rejects_non_mapping_values():

    with pytest.raises(
        ReportValidationException,
        match="must be a mapping",
    ):

        ReportParameterBinder().bind(
            create_definitions(),
            [
                "invalid",
            ],
        )


def test_binding_values_returns_runtime_values():

    result = ReportParameterBinder().bind(
        create_definitions(),
        {
            "year": 2026,
            "department": "HR",
        },
    )

    values = result.values()

    assert values["year"] == 2026

    assert values["department"] == "HR"

    assert values["active"] is True


def test_binding_collection_to_dict():

    result = ReportParameterBinder().bind(
        create_definitions(),
        {
            "year": 2026,
        },
    )

    serialized = result.to_dict()

    assert serialized["year"]["value"] == 2026

    assert serialized["year"]["data_type"] == "integer"

    assert serialized["department"]["defaulted"] is True


def test_binding_collection_contains():

    result = ReportParameterBinder().bind(
        create_definitions(),
        {
            "year": 2026,
        },
    )

    assert "year" in result

    assert "department" in result

    assert "unknown" not in result


def test_optional_parameter_without_default_is_none():

    definitions = ReportParameterCollection()

    definitions.add(
        ReportParameter(
            name="description",
            label="Description",
        )
    )

    result = ReportParameterBinder().bind(
        definitions,
        {},
    )

    binding = result.get(
        "description"
    )

    assert binding.value is None

    assert binding.supplied is False

    assert binding.defaulted is False


def test_required_parameter_cannot_be_none():

    definitions = ReportParameterCollection()

    definitions.add(
        ReportParameter(
            name="year",
            label="Year",
            data_type=ReportParameterType.INTEGER,
            required=True,
        )
    )

    with pytest.raises(
        ReportValidationException,
        match="cannot be None",
    ):

        ReportParameterBinder().bind(
            definitions,
            {
                "year": None,
            },
        )
