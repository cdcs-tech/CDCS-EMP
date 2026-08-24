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
    ReportExecutionContext,
    ReportExecutionRequest,
    ReportQueryResultStatus,
    ReportQueryResult,
    ReportQueryExecutor,
    ReportExecutionService,
    DefaultReportQueryExecutor,
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


# ---------------------------------------------------------
# Reporting Filters
# ---------------------------------------------------------

from app.core.reporting.filters import (
    ReportFilter,
    ReportFilterCollection,
    ReportFilterOperator,
)


# ---------------------------------------------------------
# Reporting Sorting
# ---------------------------------------------------------

from app.core.reporting.sorting import (
    ReportSort,
    ReportSortCollection,
    ReportSortDirection,
)


# ---------------------------------------------------------
# Reporting Parameter Binding
# ---------------------------------------------------------

from app.core.reporting.parameter_binding import (
    ReportParameterBinding,
    ReportParameterBindingCollection,
    ReportParameterBinder,
)


# ---------------------------------------------------------
# Reporting Output
# ---------------------------------------------------------

from app.core.reporting.output import (
    ReportOutputFormat,
    ReportOutputRequest,
)


# ---------------------------------------------------------
# Reporting Export Formats
# ---------------------------------------------------------

from app.core.reporting.export_formats import (
    ReportExportFormat,
)

from app.core.reporting.exporters import (
    ReportExporter,
)

from app.core.reporting.exporter_registry import (
    ReportExporterRegistry,
)

from app.core.reporting.export_execution_service import (
    ReportExportExecutionService,
)


# ---------------------------------------------------------
# Analytics & KPI
# ---------------------------------------------------------

from app.core.reporting.analytics import (
    ReportKPIValueType,
    ReportKPI,
)

from app.core.reporting.kpi_registry import (
    ReportKPIRegistry,
)

# ---------------------------------------------------------
# KPI Calculation
# ---------------------------------------------------------

from app.core.reporting.kpi_calculation import (
    ReportKPICalculationStatus,
    ReportKPICalculationRequest,
    ReportKPICalculationResult,
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
    # Reporting Execution Request / Context
    # -----------------------------------------------------

    "ReportExecutionContext",

    "ReportExecutionRequest",


    # -----------------------------------------------------
    # Reporting Query Results
    # -----------------------------------------------------

    "ReportQueryResultStatus",

    "ReportQueryResult",


    # -----------------------------------------------------
    # Reporting Query Execution
    # -----------------------------------------------------

    "ReportQueryExecutor",

    "DefaultReportQueryExecutor",

    "ReportExecutionService",


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
    # Reporting Filters
    # -----------------------------------------------------

    "ReportFilter",

    "ReportFilterCollection",

    "ReportFilterOperator",


    # -----------------------------------------------------
    # Reporting Sorting
    # -----------------------------------------------------

    "ReportSort",

    "ReportSortCollection",

    "ReportSortDirection",


    # -----------------------------------------------------
    # Reporting Parameter Binding
    # -----------------------------------------------------

    "ReportParameterBinding",

    "ReportParameterBindingCollection",

    "ReportParameterBinder",


    # -----------------------------------------------------
    # Reporting Output
    # -----------------------------------------------------

    "ReportOutputFormat",

    "ReportOutputRequest",


    # -----------------------------------------------------
    # Reporting Export Formats
    # -----------------------------------------------------

    "ReportExportFormat",

    "ReportExporter",

    "ReportExporterRegistry",

    "ReportExportExecutionService",


    # -----------------------------------------------------
    # Analytics & KPI
    # -----------------------------------------------------

    "ReportKPIValueType",

    "ReportKPI",

    "ReportKPIRegistry",

    "ReportKPICalculationStatus",

    "ReportKPICalculationRequest",

    "ReportKPICalculationResult",


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
