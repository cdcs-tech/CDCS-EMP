"""
CDCS Enterprise Management Platform (CDCS-EMP)

Reporting Framework Tests

Report data provider registry tests.
"""

import pytest

from app.core.reporting import (
    ReportDataProvider,
    ReportDataProviderRegistry,
    ReportDefinition,
    ReportQuery,
    ReportResult,
    ReportResultStatus,
    ReportRegistrationException,
)


class ExampleReportDataProvider(
    ReportDataProvider,
):
    """
    Concrete provider used by registry tests.
    """

    def __init__(
        self,
        provider_name: str = "example",
        supported_code: str = "EXAMPLE",
    ):
        self._provider_name = provider_name
        self._supported_code = supported_code

    @property
    def name(self) -> str:
        return self._provider_name

    def supports(
        self,
        query: ReportQuery,
    ) -> bool:
        return (
            query.identifier
            == self._supported_code
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
            data=[],
            status=ReportResultStatus.SUCCESS,
        )


def create_query(
    code: str = "EXAMPLE",
) -> ReportQuery:

    return ReportQuery(
        report_code=code,
    )


def test_registry_creation():

    registry = ReportDataProviderRegistry()

    assert (
        registry.all()
        == ()
    )


def test_registry_registers_provider():

    provider = ExampleReportDataProvider()

    registry = ReportDataProviderRegistry()

    registry.register(
        provider
    )

    assert (
        registry.has("example")
        is True
    )

    assert (
        registry.get("example")
        is provider
    )


def test_registry_provider_name_is_case_insensitive():

    provider = ExampleReportDataProvider(
        provider_name="FinanceProvider",
    )

    registry = ReportDataProviderRegistry()

    registry.register(
        provider
    )

    assert (
        registry.has("financeprovider")
        is True
    )

    assert (
        registry.get("FINANCEPROVIDER")
        is provider
    )


def test_registry_rejects_duplicate_provider():

    registry = ReportDataProviderRegistry()

    registry.register(
        ExampleReportDataProvider()
    )

    with pytest.raises(
        ReportRegistrationException
    ):

        registry.register(
            ExampleReportDataProvider()
        )


def test_registry_rejects_invalid_provider():

    registry = ReportDataProviderRegistry()

    with pytest.raises(
        ReportRegistrationException
    ):

        registry.register(
            "invalid"
        )


def test_registry_initial_providers_are_registered():

    provider = ExampleReportDataProvider()

    registry = ReportDataProviderRegistry(
        providers=[
            provider,
        ]
    )

    assert (
        registry.get("example")
        is provider
    )


def test_registry_all_preserves_registration_order():

    first = ExampleReportDataProvider(
        provider_name="first",
        supported_code="FIRST",
    )

    second = ExampleReportDataProvider(
        provider_name="second",
        supported_code="SECOND",
    )

    registry = ReportDataProviderRegistry(
        providers=[
            first,
            second,
        ]
    )

    assert registry.all() == (
        first,
        second,
    )


def test_registry_resolves_supported_provider():

    provider = ExampleReportDataProvider()

    registry = ReportDataProviderRegistry(
        providers=[
            provider,
        ]
    )

    resolved = registry.resolve(
        create_query()
    )

    assert (
        resolved
        is provider
    )


def test_registry_resolves_first_matching_provider():

    first = ExampleReportDataProvider(
        provider_name="first",
        supported_code="EXAMPLE",
    )

    second = ExampleReportDataProvider(
        provider_name="second",
        supported_code="EXAMPLE",
    )

    registry = ReportDataProviderRegistry(
        providers=[
            first,
            second,
        ]
    )

    resolved = registry.resolve(
        create_query()
    )

    assert (
        resolved
        is first
    )


def test_registry_rejects_unsupported_query():

    registry = ReportDataProviderRegistry(
        providers=[
            ExampleReportDataProvider(),
        ]
    )

    with pytest.raises(
        ReportRegistrationException
    ):

        registry.resolve(
            create_query("UNKNOWN")
        )


def test_registry_rejects_invalid_query():

    registry = ReportDataProviderRegistry(
        providers=[
            ExampleReportDataProvider(),
        ]
    )

    with pytest.raises(
        ReportRegistrationException
    ):

        registry.resolve(
            "invalid"
        )


def test_registry_unregisters_provider():

    provider = ExampleReportDataProvider()

    registry = ReportDataProviderRegistry(
        providers=[
            provider,
        ]
    )

    registry.unregister(
        "example"
    )

    assert (
        registry.has("example")
        is False
    )


def test_registry_unregister_missing_provider():

    registry = ReportDataProviderRegistry()

    with pytest.raises(
        KeyError
    ):

        registry.unregister(
            "missing"
        )


def test_registry_get_missing_provider():

    registry = ReportDataProviderRegistry()

    with pytest.raises(
        KeyError
    ):

        registry.get(
            "missing"
        )


def test_public_registry_is_available():

    from app.core.reporting import (
        ReportDataProviderRegistry as PublicRegistry,
    )

    assert (
        PublicRegistry
        is ReportDataProviderRegistry
    )
