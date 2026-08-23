"""
CDCS Enterprise Management Platform (CDCS-EMP)

Reporting Framework Tests

Report sorting contract tests.
"""

from __future__ import annotations

import pytest

from app.core.reporting import (
    ReportSort,
    ReportSortCollection,
    ReportSortDirection,
)


def test_report_sort_creation():

    report_sort = ReportSort(
        field="department",
        direction=ReportSortDirection.ASCENDING,
    )

    assert (
        report_sort.field
        == "department"
    )

    assert (
        report_sort.direction
        == ReportSortDirection.ASCENDING
    )


def test_report_sort_defaults_to_ascending():

    report_sort = ReportSort(
        field="department",
    )

    assert (
        report_sort.direction
        == ReportSortDirection.ASCENDING
    )


def test_report_sort_normalizes_field():

    report_sort = ReportSort(
        field="  department  ",
    )

    assert (
        report_sort.field
        == "department"
    )


@pytest.mark.parametrize(
    "direction",
    [
        ReportSortDirection.ASCENDING,
        ReportSortDirection.DESCENDING,
    ],
)
def test_report_sort_accepts_enum_direction(
    direction,
):

    report_sort = ReportSort(
        field="department",
        direction=direction,
    )

    assert (
        report_sort.direction
        == direction
    )


@pytest.mark.parametrize(
    "direction,expected",
    [
        ("asc", ReportSortDirection.ASCENDING),
        ("desc", ReportSortDirection.DESCENDING),
        (" ASC ", ReportSortDirection.ASCENDING),
        (" DESC ", ReportSortDirection.DESCENDING),
    ],
)
def test_report_sort_accepts_direction_string(
    direction,
    expected,
):

    report_sort = ReportSort(
        field="department",
        direction=direction,
    )

    assert (
        report_sort.direction
        == expected
    )


def test_report_sort_requires_field():

    with pytest.raises(
        ValueError,
        match="field is required",
    ):

        ReportSort(
            field="   ",
        )


def test_report_sort_requires_string_field():

    with pytest.raises(
        ValueError,
        match="field must be a string",
    ):

        ReportSort(
            field=123,
        )


def test_report_sort_rejects_invalid_direction():

    with pytest.raises(
        ValueError,
        match="Invalid report sort direction",
    ):

        ReportSort(
            field="department",
            direction="unsupported",
        )


def test_report_sort_rejects_invalid_direction_type():

    with pytest.raises(
        ValueError,
        match="direction must be a ReportSortDirection",
    ):

        ReportSort(
            field="department",
            direction=123,
        )


def test_report_sort_is_immutable():

    report_sort = ReportSort(
        field="department",
    )

    with pytest.raises(
        AttributeError
    ):

        report_sort.field = "other"


def test_report_sort_to_dict():

    report_sort = ReportSort(
        field="department",
        direction=ReportSortDirection.DESCENDING,
    )

    assert (
        report_sort.to_dict()
        == {
            "field": "department",
            "direction": "desc",
        }
    )


def test_report_sort_collection_defaults():

    collection = ReportSortCollection()

    assert (
        len(collection)
        == 0
    )

    assert (
        collection.to_list()
        == []
    )


def test_report_sort_collection_add():

    collection = ReportSortCollection()

    report_sort = ReportSort(
        field="department",
    )

    collection.add(
        report_sort
    )

    assert (
        len(collection)
        == 1
    )

    assert (
        collection.get("department")
        is report_sort
    )


def test_report_sort_collection_rejects_invalid_sort():

    collection = ReportSortCollection()

    with pytest.raises(
        ValueError,
        match="ReportSort instance",
    ):

        collection.add(
            "invalid"
        )


def test_report_sort_collection_rejects_duplicate_field():

    collection = ReportSortCollection()

    collection.add(
        ReportSort(
            field="department",
        )
    )

    with pytest.raises(
        ValueError,
        match="already defined",
    ):

        collection.add(
            ReportSort(
                field="department",
                direction=ReportSortDirection.DESCENDING,
            )
        )


def test_report_sort_collection_contains():

    collection = ReportSortCollection()

    collection.add(
        ReportSort(
            field="department",
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


def test_report_sort_collection_contains_normalizes_field():

    collection = ReportSortCollection()

    collection.add(
        ReportSort(
            field="department",
        )
    )

    assert (
        collection.contains("  department  ")
        is True
    )


def test_report_sort_collection_get_missing():

    collection = ReportSortCollection()

    with pytest.raises(
        KeyError,
        match="not defined",
    ):

        collection.get("missing")


def test_report_sort_collection_remove():

    collection = ReportSortCollection()

    collection.add(
        ReportSort(
            field="department",
        )
    )

    collection.remove(
        "department"
    )

    assert (
        len(collection)
        == 0
    )


def test_report_sort_collection_remove_missing():

    collection = ReportSortCollection()

    with pytest.raises(
        KeyError,
        match="not defined",
    ):

        collection.remove(
            "missing"
        )


def test_report_sort_collection_clear():

    collection = ReportSortCollection()

    collection.add(
        ReportSort(
            field="department",
        )
    )

    collection.add(
        ReportSort(
            field="year",
            direction=ReportSortDirection.DESCENDING,
        )
    )

    collection.clear()

    assert (
        len(collection)
        == 0
    )


def test_report_sort_collection_iteration_preserves_order():

    collection = ReportSortCollection()

    first = ReportSort(
        field="department",
    )

    second = ReportSort(
        field="year",
        direction=ReportSortDirection.DESCENDING,
    )

    collection.add(first)
    collection.add(second)

    assert list(collection) == [
        first,
        second,
    ]


def test_report_sort_collection_contains_operator():

    collection = ReportSortCollection()

    collection.add(
        ReportSort(
            field="department",
        )
    )

    assert (
        "department"
        in collection
    )


def test_report_sort_collection_to_list_preserves_order():

    collection = ReportSortCollection()

    collection.add(
        ReportSort(
            field="department",
            direction=ReportSortDirection.ASCENDING,
        )
    )

    collection.add(
        ReportSort(
            field="year",
            direction=ReportSortDirection.DESCENDING,
        )
    )

    assert (
        collection.to_list()
        == [
            {
                "field": "department",
                "direction": "asc",
            },
            {
                "field": "year",
                "direction": "desc",
            },
        ]
    )


def test_report_sort_collection_initial_values():

    first = ReportSort(
        field="department",
    )

    second = ReportSort(
        field="year",
        direction=ReportSortDirection.DESCENDING,
    )

    collection = ReportSortCollection(
        sorts=[
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


def test_report_sort_collection_rejects_invalid_initial_value():

    with pytest.raises(
        ValueError,
        match="must contain ReportSort instances",
    ):

        ReportSortCollection(
            sorts=[
                "invalid",
            ]
        )
