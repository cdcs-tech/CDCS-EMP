"""
CDCS Enterprise Management Platform (CDCS-EMP)

Reporting Framework Tests

Report data provider contract tests.
"""

import pytest

from app.core.data import (
    QueryOptions,
)

from app.core.reporting import (
    ReportDataProvider,
    ReportQuery,
)


class ExampleReportDataProvider(
    ReportDataProvider,
):
    """
    Concrete test implementation of the
    ReportDataProvider contract.
    """

    @property
    def name(
        self,
    ) -> str:
        return "example-data"

    def supports(
        self,
        query: ReportQuery,
    ) -> bool:
        return (
            query.report_code
            == "EXAMPLE"
        )

    def execute(
        self,
        query: ReportQuery,
        options: QueryOptions | None = None,
    ):
        return {
            "report_code": query.report_code,
            "options": (
                options.to_dict()
                if options is not None
                else None
            ),
        }


def create_query():
    return ReportQuery(
        report_code="EXAMPLE",
    )


def test_report_data_provider_is_abstract():

    assert (
        ReportDataProvider.__abstractmethods__
    )


def test_report_data_provider_cannot_be_instantiated():

    with pytest.raises(
        TypeError
    ):
        ReportDataProvider()


def test_report_data_provider_requires_name():

    class InvalidProvider(
        ReportDataProvider,
    ):

        def supports(
            self,
            query,
        ):
            return True

        def execute(
            self,
            query,
            options=None,
        ):
            return {}

    with pytest.raises(
        TypeError
    ):
        InvalidProvider()


def test_report_data_provider_requires_supports():

    class InvalidProvider(
        ReportDataProvider,
    ):

        @property
        def name(
            self,
        ):
            return "invalid"

        def execute(
            self,
            query,
            options=None,
        ):
            return {}

    with pytest.raises(
        TypeError
    ):
        InvalidProvider()


def test_report_data_provider_requires_execute():

    class InvalidProvider(
        ReportDataProvider,
    ):

        @property
        def name(
            self,
        ):
            return "invalid"

        def supports(
            self,
            query,
        ):
            return True

    with pytest.raises(
        TypeError
    ):
        InvalidProvider()


def test_report_data_provider_name_contract():

    provider = ExampleReportDataProvider()

    assert (
        provider.name
        == "example-data"
    )


def test_report_data_provider_supports_contract():

    provider = ExampleReportDataProvider()

    query = create_query()

    assert (
        provider.supports(
            query
        )
        is True
    )


def test_report_data_provider_supports_unsupported_query():

    provider = ExampleReportDataProvider()

    query = ReportQuery(
        report_code="OTHER",
    )

    assert (
        provider.supports(
            query
        )
        is False
    )


def test_report_data_provider_execute_without_options():

    provider = ExampleReportDataProvider()

    query = create_query()

    result = provider.execute(
        query
    )

    assert (
        result["report_code"]
        == "EXAMPLE"
    )

    assert (
        result["options"]
        is None
    )


def test_report_data_provider_execute_with_query_options():

    provider = ExampleReportDataProvider()

    query = create_query()

    options = QueryOptions(
        page=2,
        page_size=50,
        sort_by="transaction_date",
        sort_direction="desc",
        filters={
            "department": "Finance",
        },
        search="monthly",
        fields=[
            "id",
            "amount",
        ],
        include_inactive=True,
    )

    result = provider.execute(
        query,
        options,
    )

    assert (
        result["report_code"]
        == "EXAMPLE"
    )

    assert (
        result["options"]["page"]
        == 2
    )

    assert (
        result["options"]["page_size"]
        == 50
    )

    assert (
        result["options"]["sort_by"]
        == "transaction_date"
    )

    assert (
        result["options"]["sort_direction"]
        == "desc"
    )

    assert (
        result["options"]["filters"]
        == {
            "department": "Finance",
        }
    )

    assert (
        result["options"]["search"]
        == "monthly"
    )

    assert (
        result["options"]["fields"]
        == [
            "id",
            "amount",
        ]
    )

    assert (
        result["options"]["include_inactive"]
        is True
    )


def test_report_data_provider_accepts_report_query():

    provider = ExampleReportDataProvider()

    query = ReportQuery(
        report_code="EXAMPLE",
        metadata={
            "source": "finance",
        },
    )

    assert (
        provider.supports(
            query
        )
        is True
    )


def test_report_data_provider_returns_data_not_report_result():

    provider = ExampleReportDataProvider()

    query = create_query()

    result = provider.execute(
        query
    )

    assert isinstance(
        result,
        dict,
    )

    assert not hasattr(
        result,
        "definition",
    )


def test_public_report_data_provider_is_available():

    from app.core.reporting import (
        ReportDataProvider as PublicReportDataProvider,
    )

    assert (
        PublicReportDataProvider
        is ReportDataProvider
    )
