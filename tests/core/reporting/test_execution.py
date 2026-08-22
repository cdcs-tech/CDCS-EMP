"""
CDCS Enterprise Management Platform (CDCS-EMP)

Reporting Framework Tests

Report query execution contract and integration tests.
"""

from __future__ import annotations

from typing import Any

import pytest

from app.core.data import QueryOptions

from app.core.reporting import (
    DefaultReportQueryExecutor,
    ReportDataProvider,
    ReportQuery,
    ReportQueryExecutor,
    ReportQueryResult,
    ReportQueryResultStatus,
)


class ExampleReportDataProvider(
    ReportDataProvider,
):
    """
    Concrete test implementation of the
    ReportDataProvider contract.
    """

    def __init__(
        self,
        data: Any = None,
    ) -> None:

        self.received_query = None
        self.received_options = None

        self.data = data

    @property
    def name(
        self,
    ) -> str:
        return "example"

    def supports(
        self,
        query: ReportQuery,
    ) -> bool:
        return (
            query.identifier
            == "EXAMPLE"
        )

    def execute(
        self,
        query: ReportQuery,
        options: QueryOptions | None = None,
    ) -> Any:
        self.received_query = query
        self.received_options = options

        if self.data is not None:
            return self.data

        return {
            "query": query.to_dict(),
        }


class FailingReportDataProvider(
    ExampleReportDataProvider,
):
    """
    Provider used to verify standardized execution
    failure handling.
    """

    def execute(
        self,
        query: ReportQuery,
        options: QueryOptions | None = None,
    ) -> Any:

        self.received_query = query
        self.received_options = options

        raise RuntimeError(
            "Provider execution failed."
        )


def create_query() -> ReportQuery:
    """
    Create a standard test report query.
    """

    return ReportQuery(
        report_code="EXAMPLE",
        metadata={
            "source": "test",
        },
    )


def test_report_query_executor_is_abstract():

    assert (
        ReportQueryExecutor.__abstractmethods__
    )


def test_report_query_executor_cannot_be_instantiated():

    with pytest.raises(
        TypeError
    ):
        ReportQueryExecutor()


def test_report_query_executor_requires_execute():

    class InvalidExecutor(
        ReportQueryExecutor,
    ):
        pass

    with pytest.raises(
        TypeError
    ):
        InvalidExecutor()


def test_default_report_query_executor_is_concrete():

    executor = DefaultReportQueryExecutor()

    assert isinstance(
        executor,
        ReportQueryExecutor,
    )


def test_execute_returns_report_query_result():

    executor = DefaultReportQueryExecutor()

    provider = ExampleReportDataProvider()

    query = create_query()

    result = executor.execute(
        provider,
        query,
    )

    assert isinstance(
        result,
        ReportQueryResult,
    )


def test_execute_returns_success_status():

    executor = DefaultReportQueryExecutor()

    provider = ExampleReportDataProvider()

    query = create_query()

    result = executor.execute(
        provider,
        query,
    )

    assert (
        result.status
        == ReportQueryResultStatus.SUCCESS
    )

    assert (
        result.is_success
        is True
    )


def test_execute_passes_query_to_provider():

    executor = DefaultReportQueryExecutor()

    provider = ExampleReportDataProvider()

    query = create_query()

    executor.execute(
        provider,
        query,
    )

    assert (
        provider.received_query
        is query
    )


def test_execute_passes_query_options_to_provider():

    executor = DefaultReportQueryExecutor()

    provider = ExampleReportDataProvider()

    query = create_query()

    options = QueryOptions(
        page=2,
        page_size=50,
        sort_by="name",
        sort_direction="desc",
        filters={
            "is_active": True,
        },
    )

    executor.execute(
        provider,
        query,
        options,
    )

    assert (
        provider.received_options
        is options
    )


def test_execute_preserves_provider_data():

    executor = DefaultReportQueryExecutor()

    provider = ExampleReportDataProvider(
        data={
            "rows": [
                {
                    "id": 1,
                    "name": "Example",
                }
            ],
        }
    )

    query = create_query()

    result = executor.execute(
        provider,
        query,
    )

    assert result.data == {
        "rows": [
            {
                "id": 1,
                "name": "Example",
            }
        ],
    }


def test_execute_preserves_query():

    executor = DefaultReportQueryExecutor()

    provider = ExampleReportDataProvider()

    query = create_query()

    result = executor.execute(
        provider,
        query,
    )

    assert result.query is query


def test_execute_records_provider_metadata():

    executor = DefaultReportQueryExecutor()

    provider = ExampleReportDataProvider()

    result = executor.execute(
        provider,
        create_query(),
    )

    assert (
        result.metadata["provider"]
        == "example"
    )


def test_execute_records_query_options_metadata():

    executor = DefaultReportQueryExecutor()

    provider = ExampleReportDataProvider()

    options = QueryOptions(
        page=3,
        page_size=10,
        sort_by="name",
        sort_direction="desc",
    )

    result = executor.execute(
        provider,
        create_query(),
        options,
    )

    assert (
        result.metadata["query_options"]
        == options.to_dict()
    )


def test_execute_detects_none_as_empty():

    executor = DefaultReportQueryExecutor()

    provider = ExampleReportDataProvider(
        data=None,
    )

    # Explicitly override provider behaviour so that
    # None is returned as provider data.
    provider.execute = (
        lambda query, options=None: None
    )

    result = executor.execute(
        provider,
        create_query(),
    )

    assert (
        result.status
        == ReportQueryResultStatus.EMPTY
    )

    assert (
        result.is_empty
        is True
    )

    assert (
        result.data is None
    )


@pytest.mark.parametrize(
    "empty_data",
    [
        [],
        (),
        set(),
        frozenset(),
    ],
)
def test_execute_detects_empty_collections(
    empty_data,
):

    executor = DefaultReportQueryExecutor()

    provider = ExampleReportDataProvider(
        data=empty_data,
    )

    result = executor.execute(
        provider,
        create_query(),
    )

    assert (
        result.status
        == ReportQueryResultStatus.EMPTY
    )

    assert (
        result.is_empty
        is True
    )


def test_execute_returns_success_for_non_empty_list():

    executor = DefaultReportQueryExecutor()

    provider = ExampleReportDataProvider(
        data=[
            {
                "id": 1,
            }
        ],
    )

    result = executor.execute(
        provider,
        create_query(),
    )

    assert (
        result.status
        == ReportQueryResultStatus.SUCCESS
    )


def test_execute_converts_provider_exception_to_failed_result():

    executor = DefaultReportQueryExecutor()

    provider = FailingReportDataProvider()

    query = create_query()

    result = executor.execute(
        provider,
        query,
    )

    assert isinstance(
        result,
        ReportQueryResult,
    )

    assert (
        result.status
        == ReportQueryResultStatus.FAILED
    )

    assert (
        result.is_failed
        is True
    )

    assert (
        result.error
        == "Provider execution failed."
    )


def test_execute_failed_result_preserves_query():

    executor = DefaultReportQueryExecutor()

    provider = FailingReportDataProvider()

    query = create_query()

    result = executor.execute(
        provider,
        query,
    )

    assert result.query is query


def test_execute_rejects_invalid_provider():

    executor = DefaultReportQueryExecutor()

    with pytest.raises(
        ValueError,
        match="Report data provider",
    ):
        executor.execute(
            object(),
            create_query(),
        )


def test_execute_rejects_invalid_query():

    executor = DefaultReportQueryExecutor()

    provider = ExampleReportDataProvider()

    with pytest.raises(
        ValueError,
        match="Report query",
    ):
        executor.execute(
            provider,
            object(),
        )


def test_execute_rejects_invalid_query_options():

    executor = DefaultReportQueryExecutor()

    provider = ExampleReportDataProvider()

    with pytest.raises(
        ValueError,
        match="Query options",
    ):
        executor.execute(
            provider,
            create_query(),
            object(),
        )


def test_execute_does_not_require_provider_resolution():

    executor = DefaultReportQueryExecutor()

    provider = ExampleReportDataProvider()

    query = create_query()

    result = executor.execute(
        provider,
        query,
    )

    assert (
        result.metadata["provider"]
        == "example"
    )


def test_public_default_executor_is_available():

    from app.core.reporting import (
        DefaultReportQueryExecutor as PublicDefaultExecutor,
    )

    assert (
        PublicDefaultExecutor
        is DefaultReportQueryExecutor
    )
