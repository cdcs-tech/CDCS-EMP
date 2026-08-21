"""
CDCS Enterprise Management Platform (CDCS-EMP)

Reporting Framework Tests

Report parameter contract tests.
"""

import pytest

from app.core.reporting import (
    ReportParameter,
    ReportParameterCollection,
    ReportParameterType,
)


def test_report_parameter_defaults():

    parameter = ReportParameter(
        name="department",
        label="Department",
    )

    assert (
        parameter.name
        == "department"
    )

    assert (
        parameter.label
        == "Department"
    )

    assert (
        parameter.data_type
        == ReportParameterType.STRING
    )

    assert (
        parameter.description
        == ""
    )

    assert (
        parameter.default_value
        is None
    )

    assert (
        parameter.required
        is False
    )

    assert (
        parameter.allowed_values
        == []
    )

    assert (
        parameter.metadata
        == {}
    )


def test_report_parameter_normalization():

    parameter = ReportParameter(
        name="  department  ",
        label="  Department Name  ",
        description="  Department filter  ",
    )

    assert (
        parameter.name
        == "department"
    )

    assert (
        parameter.label
        == "Department Name"
    )

    assert (
        parameter.description
        == "Department filter"
    )


def test_report_parameter_type_conversion():

    parameter = ReportParameter(
        name="year",
        label="Year",
        data_type="integer",
    )

    assert (
        parameter.data_type
        == ReportParameterType.INTEGER
    )


def test_report_parameter_invalid_name():

    with pytest.raises(
        ValueError,
        match="name is required",
    ):

        ReportParameter(
            name="   ",
            label="Department",
        )


def test_report_parameter_invalid_label():

    with pytest.raises(
        ValueError,
        match="label is required",
    ):

        ReportParameter(
            name="department",
            label="   ",
        )


def test_report_parameter_invalid_type():

    with pytest.raises(
        ValueError,
        match="Invalid report parameter data type",
    ):

        ReportParameter(
            name="year",
            label="Year",
            data_type="unsupported",
        )


def test_report_parameter_to_dict():

    parameter = ReportParameter(
        name="year",
        label="Year",
        data_type=ReportParameterType.INTEGER,
        description="Reporting year.",
        default_value=2026,
        required=True,
        allowed_values=[
            2024,
            2025,
            2026,
        ],
        metadata={
            "category": "period",
        },
    )

    result = parameter.to_dict()

    assert (
        result["name"]
        == "year"
    )

    assert (
        result["label"]
        == "Year"
    )

    assert (
        result["data_type"]
        == "integer"
    )

    assert (
        result["description"]
        == "Reporting year."
    )

    assert (
        result["default_value"]
        == 2026
    )

    assert (
        result["required"]
        is True
    )

    assert (
        result["allowed_values"]
        == [
            2024,
            2025,
            2026,
        ]
    )

    assert (
        result["metadata"]["category"]
        == "period"
    )


def test_parameter_collection_add():

    collection = (
        ReportParameterCollection()
    )

    parameter = ReportParameter(
        name="year",
        label="Year",
    )

    collection.add(
        parameter
    )

    assert (
        len(collection)
        == 1
    )

    assert (
        collection.get("year")
        is parameter
    )


def test_parameter_collection_duplicate():

    collection = (
        ReportParameterCollection()
    )

    collection.add(
        ReportParameter(
            name="year",
            label="Year",
        )
    )

    with pytest.raises(
        ValueError,
        match="already defined",
    ):

        collection.add(
            ReportParameter(
                name="year",
                label="Year",
            )
        )


def test_parameter_collection_contains():

    collection = (
        ReportParameterCollection()
    )

    collection.add(
        ReportParameter(
            name="year",
            label="Year",
        )
    )

    assert (
        collection.contains("year")
        is True
    )

    assert (
        collection.contains("missing")
        is False
    )


def test_parameter_collection_remove():

    collection = (
        ReportParameterCollection()
    )

    collection.add(
        ReportParameter(
            name="year",
            label="Year",
        )
    )

    collection.remove(
        "year"
    )

    assert (
        len(collection)
        == 0
    )


def test_parameter_collection_to_list():

    collection = (
        ReportParameterCollection()
    )

    collection.add(
        ReportParameter(
            name="year",
            label="Year",
            data_type=ReportParameterType.INTEGER,
        )
    )

    collection.add(
        ReportParameter(
            name="department",
            label="Department",
        )
    )

    result = collection.to_list()

    assert (
        len(result)
        == 2
    )

    assert (
        result[0]["name"]
        == "year"
    )

    assert (
        result[0]["data_type"]
        == "integer"
    )

    assert (
        result[1]["name"]
        == "department"
    )


def test_parameter_collection_invalid_parameter():

    collection = (
        ReportParameterCollection()
    )

    with pytest.raises(
        TypeError,
        match="ReportParameter instance",
    ):

        collection.add(
            "invalid"
        )
