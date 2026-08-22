"""
CDCS Enterprise Management Platform (CDCS-EMP)

Reporting & Analytics Framework

Public interface for the reporting and analytics
framework.
"""


# ---------------------------------------------------------
# Reporting Contracts
# ---------------------------------------------------------

from app.core.reporting.contracts import (
    ReportDefinition,
    ReportDefinitionParameter,
    ReportDefinitionParameterCollection,
    ReportParameterType,
    ReportParameter,
    ReportParameterCollection,
    ReportQuery,
    ReportQueryExecutor,
    ReportDataProvider,
    ReportDataProviderRegistry,
    ReportProvider,
    ReportResultStatus,
    ReportResult,
)


# ---------------------------------------------------------
# Reporting Exceptions
# ---------------------------------------------------------

from app.core.reporting.exceptions import (
    ReportingException,
    ReportingConfigurationException,
    ReportingContractException,
    ReportDefinitionException,
    ReportExecutionException,
    ReportValidationException,
    ReportNotFoundException,
    ReportRegistrationException,
    AnalyticsException,
    AnalyticsConfigurationException,
    AnalyticsExecutionException,
)


__all__ = [

    # -----------------------------------------------------
    # Reporting Definition
    # -----------------------------------------------------

    "ReportDefinition",

    "ReportDefinitionParameter",

    "ReportDefinitionParameterCollection",


    # -----------------------------------------------------
    # Reporting Parameters
    # -----------------------------------------------------

    "ReportParameterType",

    "ReportParameter",

    "ReportParameterCollection",


    # -----------------------------------------------------
    # Reporting Query
    # -----------------------------------------------------

    "ReportQuery",


    # -----------------------------------------------------
    # Reporting Query Execution
    # -----------------------------------------------------

    "ReportQueryExecutor",


    # -----------------------------------------------------
    # Reporting Data Provider
    # -----------------------------------------------------

    "ReportDataProvider",


    # -----------------------------------------------------
    # Reporting Provider Registry
    # -----------------------------------------------------

    "ReportDataProviderRegistry",


    # -----------------------------------------------------
    # Reporting Provider
    # -----------------------------------------------------

    "ReportProvider",


    # -----------------------------------------------------
    # Reporting Results
    # -----------------------------------------------------

    "ReportResultStatus",

    "ReportResult",


    # -----------------------------------------------------
    # Reporting Exceptions
    # -----------------------------------------------------

    "ReportingException",

    "ReportingConfigurationException",

    "ReportingContractException",

    "ReportDefinitionException",

    "ReportExecutionException",

    "ReportValidationException",

    "ReportNotFoundException",

    "ReportRegistrationException",


    # -----------------------------------------------------
    # Analytics Exceptions
    # -----------------------------------------------------

    "AnalyticsException",

    "AnalyticsConfigurationException",

    "AnalyticsExecutionException",
]
