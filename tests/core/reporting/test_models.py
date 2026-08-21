"""
CDCS Enterprise Management Platform (CDCS-EMP)

Reporting Framework Tests

Tests for reporting model contracts.
"""

import pytest

from app.core.reporting.models import (
    ReportDefinition,
    ReportParameter,
    ReportParameterCollection,
)


# ---------------------------------------------------------
# Report Parameter
# ---------------------------------------------------------


def test_report_parameter_creation():

    parameter = ReportParameter(
        name="start_date",
        label="Start Date",
    )

    assert parameter.name == "start_date"

    assert parameter.label == "Start Date"

    assert parameter.data_type == "string"

    assert parameter.required is False

    assert parameter.default is None

    assert parameter.description == ""


def test_report_parameter_defaults():

    parameter = ReportParameter(
        name="department",
        label="Department",
    )

    assert parameter.data_type == "string"

    assert parameter.required is False

    assert parameter.default is None

    assert parameter.description == ""


def test_report_parameter_custom_values():

    parameter = ReportParameter(
        name="year",
        label="Reporting Year",
        data_type="integer",
        required=True,
        default=2026,
        description="Reporting year.",
    )

    assert parameter.name == "year"

    assert parameter.label == "Reporting Year"

    assert parameter.data_type == "integer"

    assert parameter.required is True

    assert parameter.default == 2026

    assert parameter.description == "Reporting year."


def test_report_parameter_name_validation():

    with pytest.raises(ValueError):

        ReportParameter(
            name="",
            label="Name",
        )


def test_report_parameter_label_validation():

    with pytest.raises(ValueError):

        ReportParameter(
            name="name",
            label="",
        )


def test_report_parameter_data_type_validation():

    with pytest.raises(ValueError):

        ReportParameter(
            name="name",
            label="Name",
            data_type="",
        )


# ---------------------------------------------------------
# Report Parameter Collection
# ---------------------------------------------------------


def test_report_parameter_collection_creation():

    collection = ReportParameterCollection()

    assert collection.count() == 0

    assert len(collection) == 0


def test_report_parameter_collection_add_and_get():

    parameter = ReportParameter(
        name="department",
        label="Department",
    )

    collection = ReportParameterCollection()

    collection.add(
        parameter
    )

    assert collection.count() == 1

    assert collection.get(
        "department"
    ) == parameter


def test_report_parameter_collection_has():

    collection = ReportParameterCollection()

    collection.add(
        ReportParameter(
            name="year",
            label="Year",
        )
    )

    assert collection.has(
        "year"
    )

    assert "year" in collection

    assert not collection.has(
        "month"
    )


def test_report_parameter_collection_duplicate_rejected():

    collection = ReportParameterCollection()

    collection.add(
        ReportParameter(
            name="year",
            label="Year",
        )
    )

    with pytest.raises(ValueError):

        collection.add(
            ReportParameter(
                name="year",
                label="Reporting Year",
            )
        )


def test_report_parameter_collection_invalid_parameter():

    collection = ReportParameterCollection()

    with pytest.raises(ValueError):

        collection.add(
            "invalid"
        )


def test_report_parameter_collection_remove():

    collection = ReportParameterCollection()

    collection.add(
        ReportParameter(
            name="year",
            label="Year",
        )
    )

    collection.remove(
        "year"
    )

    assert collection.count() == 0

    assert not collection.has(
        "year"
    )


def test_report_parameter_collection_remove_missing():

    collection = ReportParameterCollection()

    with pytest.raises(KeyError):

        collection.remove(
            "missing"
        )


def test_report_parameter_collection_clear():

    collection = ReportParameterCollection()

    collection.add(
        ReportParameter(
            name="year",
            label="Year",
        )
    )

    collection.add(
        ReportParameter(
            name="month",
            label="Month",
        )
    )

    collection.clear()

    assert collection.count() == 0

    assert len(collection) == 0


def test_report_parameter_collection_iteration():

    first = ReportParameter(
        name="year",
        label="Year",
    )

    second = ReportParameter(
        name="month",
        label="Month",
    )

    collection = ReportParameterCollection(
        parameters=[
            first,
            second,
        ]
    )

    assert list(collection) == [
        first,
        second,
    ]


def test_report_parameter_collection_to_list():

    collection = ReportParameterCollection(
        parameters=[
            ReportParameter(
                name="year",
                label="Year",
                data_type="integer",
                required=True,
                default=2026,
                description="Reporting year.",
            )
        ]
    )

    result = collection.to_list()

    assert result == [
        {
            "name": "year",
            "label": "Year",
            "data_type": "integer",
            "required": True,
            "default": 2026,
            "description": "Reporting year.",
        }
    ]


# ---------------------------------------------------------
# Report Definition
# ---------------------------------------------------------


def test_report_definition_creation():

    definition = ReportDefinition(
        code="FINANCE_MONTHLY",
        name="Monthly Finance Report",
    )

    assert definition.code == "FINANCE_MONTHLY"

    assert definition.name == "Monthly Finance Report"

    assert definition.version == "1.0.0"

    assert definition.category == "General"

    assert definition.parameters == ()


def test_report_definition_identifier():

    definition = ReportDefinition(
        code="finance_monthly",
        name="Monthly Finance Report",
    )

    assert definition.identifier == (
        "FINANCE_MONTHLY"
    )


def test_report_definition_parameters():

    parameter = ReportParameter(
        name="year",
        label="Year",
        data_type="integer",
        required=True,
    )

    definition = ReportDefinition(
        code="FINANCE_MONTHLY",
        name="Monthly Finance Report",
        parameters=(
            parameter,
        ),
    )

    assert definition.parameters == (
        parameter,
    )


def test_report_definition_code_validation():

    with pytest.raises(ValueError):

        ReportDefinition(
            code="",
            name="Monthly Finance Report",
        )


def test_report_definition_name_validation():

    with pytest.raises(ValueError):

        ReportDefinition(
            code="FINANCE_MONTHLY",
            name="",
        )


def test_report_definition_version_validation():

    with pytest.raises(ValueError):

        ReportDefinition(
            code="FINANCE_MONTHLY",
            name="Monthly Finance Report",
            version="",
        )


def test_report_definition_category_validation():

    with pytest.raises(ValueError):

        ReportDefinition(
            code="FINANCE_MONTHLY",
            name="Monthly Finance Report",
            category="",
        )


def test_report_definition_invalid_parameter():

    with pytest.raises(ValueError):

        ReportDefinition(
            code="FINANCE_MONTHLY",
            name="Monthly Finance Report",
            parameters=(
                "invalid",
            ),
        )


def test_report_definition_to_dict():

    parameter = ReportParameter(
        name="year",
        label="Year",
        data_type="integer",
        required=True,
        default=2026,
        description="Reporting year.",
    )

    definition = ReportDefinition(
        code="FINANCE_MONTHLY",
        name="Monthly Finance Report",
        description="Monthly financial reporting.",
        module="finance",
        version="1.0.0",
        category="Financial",
        parameters=(
            parameter,
        ),
        metadata={
            "owner": "Finance",
        },
    )

    result = definition.to_dict()

    assert result == {
        "code": "FINANCE_MONTHLY",
        "name": "Monthly Finance Report",
        "description": "Monthly financial reporting.",
        "module": "finance",
        "version": "1.0.0",
        "category": "Financial",
        "parameters": [
            {
                "name": "year",
                "label": "Year",
                "data_type": "integer",
                "required": True,
                "default": 2026,
                "description": "Reporting year.",
            }
        ],
        "metadata": {
            "owner": "Finance",
        },
    }
