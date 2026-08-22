"""
CDCS Enterprise Management Platform (CDCS-EMP)

Reporting Framework Tests

Report query execution contract tests.
"""

import pytest

from app.core.reporting import (
    ReportDataProvider,
    ReportDefinition,
    ReportQuery,
    ReportQueryExecutor,
    ReportResult,
    ReportResultStatus,
)


class ExampleReportDataProvider(
    ReportDataProvider,
):
    """
    Concrete test implementation of the
    ReportDataProvider contract.
    """

    @property
    def name(self) -> str:
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
    ) -> ReportResult:
        definition = ReportDefinition(
            code=query.report_code,
            name="Example Report",
        )

        return ReportResult(
            definition=definition,
            data={
                "query": query.to_dict(),
            },
            status=ReportResultStatus.SUCCESS,
            metadata={
                "provider": self.name,
            },
        )


class ExampleReportQueryExecutor(
    ReportQueryExecutor,
):
    """
    Concrete test implementation of the
    ReportQueryExecutor contract.
    """

    def execute(
        self,
        provider: ReportDataProvider,
        query: ReportQuery,
    ) -> ReportResult:

        return provider.execute(
            query
        )


def create_query() -> ReportQuery:
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


def test_report_query_executor_concrete_implementation():

    executor = ExampleReportQueryExecutor()

    assert isinstance(
        executor,
        ReportQueryExecutor,
    )


def test_report_query_executor_execute_contract():

    executor = ExampleReportQueryExecutor()

    provider = ExampleReportDataProvider()

    query = create_query()

    result = executor.execute(
        provider,
        query,
    )

    assert isinstance(
        result,
        ReportResult,
    )

    assert (
        result.definition.identifier
        == "EXAMPLE"
    )

    assert (
        result.status
        == ReportResultStatus.SUCCESS
    )

    assert (
        result.is_success
        is True
    )


def test_report_query_executor_passes_query_to_provider():

    executor = ExampleReportQueryExecutor()

    provider = ExampleReportDataProvider()

    query = create_query()

    result = executor.execute(
        provider,
        query,
    )

    assert (
        result.data["query"]["report_code"]
        == "EXAMPLE"
    )

    assert (
        result.data["query"]["metadata"]["source"]
        == "test"
    )


def test_report_query_executor_uses_supplied_provider():

    class AlternateProvider(
        ExampleReportDataProvider,
    ):

        @property
        def name(self) -> str:
            return "alternate"

    executor = ExampleReportQueryExecutor()

    provider = AlternateProvider()

    result = executor.execute(
        provider,
        create_query(),
    )

    assert (
        result.metadata["provider"]
        == "alternate"
    )


def test_public_report_query_executor_is_available():

    from app.core.reporting import (
        ReportQueryExecutor as PublicReportQueryExecutor,
    )

    assert (
        PublicReportQueryExecutor
        is ReportQueryExecutor
    )
