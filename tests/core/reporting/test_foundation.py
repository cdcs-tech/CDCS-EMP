"""
CDCS Enterprise Management Platform (CDCS-EMP)

Reporting Framework Tests

Public reporting package API and contract integration tests.
"""

from app.core.reporting import (
    AnalyticsConfigurationException,
    AnalyticsException,
    AnalyticsExecutionException,
    ReportDefinition,
    ReportDefinitionParameter,
    ReportDefinitionParameterCollection,
    ReportExecutionException,
    ReportNotFoundException,
    ReportParameter,
    ReportParameterCollection,
    ReportParameterType,
    ReportProvider,
    ReportRegistrationException,
    ReportResult,
    ReportResultStatus,
    ReportValidationException,
    ReportingConfigurationException,
    ReportingContractException,
    ReportingException,
)


def test_public_report_definition_is_available():

    definition = ReportDefinition(
        code="FINANCE.REVENUE",
        name="Revenue Report",
    )

    assert definition.code == "FINANCE.REVENUE"

    assert definition.name == "Revenue Report"

    assert definition.identifier == "FINANCE.REVENUE"


def test_public_report_definition_parameter_alias_is_available():

    parameter = ReportDefinitionParameter(
        name="period",
        label="Reporting Period",
    )

    assert parameter.name == "period"

    assert parameter.label == "Reporting Period"


def test_public_report_definition_parameter_collection_alias_is_available():

    collection = ReportDefinitionParameterCollection()

    parameter = ReportDefinitionParameter(
        name="period",
        label="Reporting Period",
    )

    collection.add(
        parameter
    )

    assert collection.count() == 1

    assert collection.get(
        "period"
    ) is parameter


def test_public_report_parameter_contract_is_available():

    parameter = ReportParameter(
        name="department",
        label="Department",
        data_type=ReportParameterType.STRING,
    )

    assert parameter.name == "department"

    assert parameter.label == "Department"

    assert (
        parameter.data_type
        == ReportParameterType.STRING
    )


def test_public_report_parameter_collection_is_available():

    collection = ReportParameterCollection()

    parameter = ReportParameter(
        name="department",
        label="Department",
    )

    collection.add(
        parameter
    )

    assert len(collection) == 1

    assert collection.get(
        "department"
    ) is parameter


def test_public_report_parameter_types_are_available():

    assert (
        ReportParameterType.STRING.value
        == "string"
    )

    assert (
        ReportParameterType.INTEGER.value
        == "integer"
    )

    assert (
        ReportParameterType.FLOAT.value
        == "float"
    )

    assert (
        ReportParameterType.BOOLEAN.value
        == "boolean"
    )

    assert (
        ReportParameterType.DATE.value
        == "date"
    )

    assert (
        ReportParameterType.DATETIME.value
        == "datetime"
    )

    assert (
        ReportParameterType.DECIMAL.value
        == "decimal"
    )


def test_public_report_provider_is_available():

    assert ReportProvider is not None

    assert hasattr(
        ReportProvider,
        "supports",
    )

    assert hasattr(
        ReportProvider,
        "generate",
    )


def test_public_report_result_contract_is_available():

    definition = ReportDefinition(
        code="FINANCE.REVENUE",
        name="Revenue Report",
    )

    result = ReportResult(
        definition=definition,
        data=[],
        status=ReportResultStatus.EMPTY,
    )

    assert result.definition is definition

    assert (
        result.status
        == ReportResultStatus.EMPTY
    )

    assert result.is_empty is True


def test_public_report_result_status_is_available():

    assert (
        ReportResultStatus.SUCCESS.value
        == "success"
    )

    assert (
        ReportResultStatus.EMPTY.value
        == "empty"
    )

    assert (
        ReportResultStatus.FAILED.value
        == "failed"
    )


def test_public_reporting_exceptions_are_available():

    exceptions = (
        ReportingException,
        ReportingConfigurationException,
        ReportingContractException,
        ReportExecutionException,
        ReportValidationException,
        ReportNotFoundException,
        ReportRegistrationException,
    )

    for exception_type in exceptions:

        assert issubclass(
            exception_type,
            Exception,
        )


def test_public_analytics_exceptions_are_available():

    exceptions = (
        AnalyticsException,
        AnalyticsConfigurationException,
        AnalyticsExecutionException,
    )

    for exception_type in exceptions:

        assert issubclass(
            exception_type,
            Exception,
        )


def test_public_contract_surface_has_no_ambiguous_parameter_exports():

    assert (
        ReportParameter
        is not ReportDefinitionParameter
    )

    assert (
        ReportParameterCollection
        is not ReportDefinitionParameterCollection
    )
