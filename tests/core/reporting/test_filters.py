"""
CDCS Enterprise Management Platform (CDCS-EMP)

Reporting Framework Tests

Report filtering contract tests.
"""

from __future__ import annotations

import pytest

from app.core.reporting import (
    ReportFilter,
    ReportFilterCollection,
    ReportFilterOperator,
)


def test_report_filter_creation():

    report_filter = ReportFilter(
        field="department",
        operator=ReportFilterOperator.EQUALS,
        value="Finance",
    )

    assert (
        report_filter.field
        == "department"
    )

    assert (
        report_filter.operator
        == ReportFilterOperator.EQUALS
    )

    assert (
        report_filter.value
        == "Finance"
    )


def test_report_filter_normalizes_field():

    report_filter = ReportFilter(
        field="  department  ",
        operator=ReportFilterOperator.EQUALS,
        value="Finance",
    )

    assert (
        report_filter.field
        == "department"
    )


def test_report_filter_accepts_operator_string():

    report_filter = ReportFilter(
        field="department",
        operator="eq",
        value="Finance",
    )

    assert (
        report_filter.operator
        == ReportFilterOperator.EQUALS
    )


def test_report_filter_normalizes_operator_string():

    report_filter = ReportFilter(
        field="department",
        operator=" EQ ",
        value="Finance",
    )

    assert (
        report_filter.operator
        == ReportFilterOperator.EQUALS
    )


def test_report_filter_requires_field():

    with pytest.raises(
        ValueError,
        match="field is required",
    ):

        ReportFilter(
            field="   ",
            operator=ReportFilterOperator.EQUALS,
            value="Finance",
        )


def test_report_filter_requires_string_field():

    with pytest.raises(
        ValueError,
        match="field must be a string",
    ):

        ReportFilter(
            field=123,
            operator=ReportFilterOperator.EQUALS,
            value="Finance",
        )


def test_report_filter_rejects_invalid_operator():

    with pytest.raises(
        ValueError,
        match="Invalid report filter operator",
    ):

        ReportFilter(
            field="department",
            operator="unsupported",
            value="Finance",
        )


def test_report_filter_rejects_invalid_operator_type():

    with pytest.raises(
        ValueError,
        match="operator must be a ReportFilterOperator",
    ):

        ReportFilter(
            field="department",
            operator=123,
            value="Finance",
        )


@pytest.mark.parametrize(
    "operator",
    [
        ReportFilterOperator.IS_NULL,
        ReportFilterOperator.IS_NOT_NULL,
    ],
)
def test_null_operators_do_not_require_value(
    operator,
):

    report_filter = ReportFilter(
        field="department",
        operator=operator,
    )

    assert (
        report_filter.value
        is None
    )

    assert (
        report_filter.requires_value
        is False
    )


@pytest.mark.parametrize(
    "operator",
    [
        ReportFilterOperator.EQUALS,
        ReportFilterOperator.NOT_EQUALS,
        ReportFilterOperator.GREATER_THAN,
        ReportFilterOperator.GREATER_THAN_OR_EQUAL,
        ReportFilterOperator.LESS_THAN,
        ReportFilterOperator.LESS_THAN_OR_EQUAL,
        ReportFilterOperator.CONTAINS,
        ReportFilterOperator.STARTS_WITH,
        ReportFilterOperator.ENDS_WITH,
        ReportFilterOperator.IN,
        ReportFilterOperator.NOT_IN,
    ],
)
def test_value_operators_require_value(
    operator,
):

    report_filter = ReportFilter(
        field="amount",
        operator=operator,
        value=100,
    )

    assert (
        report_filter.requires_value
        is True
    )


@pytest.mark.parametrize(
    "operator",
    [
        ReportFilterOperator.IS_NULL,
        ReportFilterOperator.IS_NOT_NULL,
    ],
)
def test_null_operators_reject_values(
    operator,
):

    with pytest.raises(
        ValueError,
        match="does not accept a filter value",
    ):

        ReportFilter(
            field="department",
            operator=operator,
            value="Finance",
        )


def test_report_filter_is_immutable():

    report_filter = ReportFilter(
        field="department",
        operator=ReportFilterOperator.EQUALS,
        value="Finance",
    )

    with pytest.raises(
        AttributeError
    ):

        report_filter.field = "other"


def test_report_filter_to_dict():

    report_filter = ReportFilter(
        field="department",
        operator=ReportFilterOperator.EQUALS,
        value="Finance",
    )

    assert (
        report_filter.to_dict()
        == {
            "field": "department",
            "operator": "eq",
            "value": "Finance",
        }
    )


def test_report_filter_collection_defaults():

    collection = ReportFilterCollection()

    assert (
        len(collection)
        == 0
    )

    assert (
        collection.to_list()
        == []
    )


def test_report_filter_collection_add():

    collection = ReportFilterCollection()

    report_filter = ReportFilter(
        field="department",
        operator=ReportFilterOperator.EQUALS,
        value="Finance",
    )

    collection.add(
        report_filter
    )

    assert (
        len(collection)
        == 1
    )

    assert (
        collection.get("department")
        is report_filter
    )


def test_report_filter_collection_rejects_invalid_filter():

    collection = ReportFilterCollection()

    with pytest.raises(
        ValueError,
        match="ReportFilter instance",
    ):

        collection.add(
            "invalid"
        )


def test_report_filter_collection_rejects_duplicate_field():

    collection = ReportFilterCollection()

    collection.add(
        ReportFilter(
            field="department",
            operator=ReportFilterOperator.EQUALS,
            value="Finance",
        )
    )

    with pytest.raises(
        ValueError,
        match="already defined",
    ):

        collection.add(
            ReportFilter(
                field="department",
                operator=ReportFilterOperator.EQUALS,
                value="HR",
            )
        )


def test_report_filter_collection_contains():

    collection = ReportFilterCollection()

    collection.add(
        ReportFilter(
            field="department",
            operator=ReportFilterOperator.EQUALS,
            value="Finance",
        )
    )

    assert (
        collection.contains("department")
        is True
    )

    assert (
        collection.contains("missing")
        is False
    )


def test_report_filter_collection_contains_normalizes_field():

    collection = ReportFilterCollection()

    collection.add(
        ReportFilter(
            field="department",
            operator=ReportFilterOperator.EQUALS,
            value="Finance",
        )
    )

    assert (
        collection.contains("  department  ")
        is True
    )


def test_report_filter_collection_get_missing():

    collection = ReportFilterCollection()

    with pytest.raises(
        KeyError,
        match="not defined",
    ):

        collection.get("missing")


def test_report_filter_collection_remove():

    collection = ReportFilterCollection()

    collection.add(
        ReportFilter(
            field="department",
            operator=ReportFilterOperator.EQUALS,
            value="Finance",
        )
    )

    collection.remove(
        "department"
    )

    assert (
        len(collection)
        == 0
    )


def test_report_filter_collection_remove_missing():

    collection = ReportFilterCollection()

    with pytest.raises(
        KeyError,
        match="not defined",
    ):

        collection.remove(
            "missing"
        )


def test_report_filter_collection_clear():

    collection = ReportFilterCollection()

    collection.add(
        ReportFilter(
            field="department",
            operator=ReportFilterOperator.EQUALS,
            value="Finance",
        )
    )

    collection.add(
        ReportFilter(
            field="year",
            operator=ReportFilterOperator.EQUALS,
            value=2026,
        )
    )

    collection.clear()

    assert (
        len(collection)
        == 0
    )


def test_report_filter_collection_iteration():

    collection = ReportFilterCollection()

    first = ReportFilter(
        field="department",
        operator=ReportFilterOperator.EQUALS,
        value="Finance",
    )

    second = ReportFilter(
        field="year",
        operator=ReportFilterOperator.EQUALS,
        value=2026,
    )

    collection.add(first)
    collection.add(second)

    assert list(collection) == [
        first,
        second,
    ]


def test_report_filter_collection_contains_operator():

    collection = ReportFilterCollection()

    report_filter = ReportFilter(
        field="department",
        operator=ReportFilterOperator.EQUALS,
        value="Finance",
    )

    collection.add(
        report_filter
    )

    assert (
        "department"
        in collection
    )


def test_report_filter_collection_to_list():

    collection = ReportFilterCollection()

    collection.add(
        ReportFilter(
            field="department",
            operator=ReportFilterOperator.EQUALS,
            value="Finance",
        )
    )

    collection.add(
        ReportFilter(
            field="year",
            operator=ReportFilterOperator.GREATER_THAN,
            value=2020,
        )
    )

    assert (
        collection.to_list()
        == [
            {
                "field": "department",
                "operator": "eq",
                "value": "Finance",
            },
            {
                "field": "year",
                "operator": "gt",
                "value": 2020,
            },
        ]
    )


def test_report_filter_collection_initial_values():

    first = ReportFilter(
        field="department",
        operator=ReportFilterOperator.EQUALS,
        value="Finance",
    )

    second = ReportFilter(
        field="year",
        operator=ReportFilterOperator.EQUALS,
        value=2026,
    )

    collection = ReportFilterCollection(
        filters=[
            first,
            second,
        ]
    )

    assert (
        collection.to_list()
        == [
            first.to_dict(),
            second.to_dict(),
        ]
    )


def test_report_filter_collection_rejects_invalid_initial_value():

    with pytest.raises(
        ValueError,
        match="must contain ReportFilter instances",
    ):

        ReportFilterCollection(
            filters=[
                "invalid",
            ]
        )
