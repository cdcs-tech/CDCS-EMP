"""
CDCS Enterprise Management Platform (CDCS-EMP)

Reporting Framework Tests

Report provider contract tests.
"""

import pytest

from app.core.reporting import (
    ReportDefinition,
    ReportProvider,
    ReportResult,
    ReportResultStatus,
)


class ExampleReportProvider(
    ReportProvider,
):
    """
    Concrete test implementation of the
    ReportProvider contract.
    """

    @property
    def name(self) -> str:
        return "example"

    def supports(
        self,
        definition: ReportDefinition,
    ) -> bool:
        return (
            definition.code
            == "EXAMPLE"
        )

    def generate(
        self,
        definition: ReportDefinition,
        request,
    ):
        return ReportResult(
            definition=definition,
            data={
                "request": request,
            },
            status=ReportResultStatus.SUCCESS,
            metadata={
                "provider": self.name,
            },
        )


def create_definition():
    return ReportDefinition(
        code="EXAMPLE",
        name="Example Report",
        description="Example reporting definition.",
    )


def test_report_provider_is_abstract():

    assert (
        ReportProvider.__abstractmethods__
    )


def test_report_provider_cannot_be_instantiated():

    with pytest.raises(
        TypeError
    ):
        ReportProvider()


def test_provider_name_contract():

    provider = ExampleReportProvider()

    assert (
        provider.name
        == "example"
    )


def test_provider_supports_contract():

    provider = ExampleReportProvider()

    definition = create_definition()

    assert (
        provider.supports(
            definition
        )
        is True
    )


def test_provider_supports_unsupported_definition():

    provider = ExampleReportProvider()

    definition = ReportDefinition(
        code="OTHER",
        name="Other Report",
        description="Other reporting definition.",
    )

    assert (
        provider.supports(
            definition
        )
        is False
    )


def test_provider_generate_contract():

    provider = ExampleReportProvider()

    definition = create_definition()

    result = provider.generate(
        definition,
        {
            "page": 1,
        },
    )

    assert isinstance(
        result,
        ReportResult,
    )

    assert (
        result.definition
        is definition
    )

    assert (
        result.status
        == ReportResultStatus.SUCCESS
    )

    assert (
        result.is_success
        is True
    )

    assert (
        result.data["request"]["page"]
        == 1
    )

    assert (
        result.metadata["provider"]
        == "example"
    )


def test_provider_contract_requires_name():

    class InvalidProvider(
        ReportProvider,
    ):

        def supports(
            self,
            definition,
        ):
            return True

        def generate(
            self,
            definition,
            request,
        ):
            return None

    with pytest.raises(
        TypeError
    ):
        InvalidProvider()


def test_provider_contract_requires_supports():

    class InvalidProvider(
        ReportProvider,
    ):

        @property
        def name(self):
            return "invalid"

        def generate(
            self,
            definition,
            request,
        ):
            return None

    with pytest.raises(
        TypeError
    ):
        InvalidProvider()


def test_provider_contract_requires_generate():

    class InvalidProvider(
        ReportProvider,
    ):

        @property
        def name(self):
            return "invalid"

        def supports(
            self,
            definition,
        ):
            return True

    with pytest.raises(
        TypeError
    ):
        InvalidProvider()
