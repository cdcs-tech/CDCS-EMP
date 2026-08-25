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


# ---------------------------------------------------------
# Reporting Exporters
# ---------------------------------------------------------

from app.core.reporting.exporters import (
    ReportExporter,
)


# ---------------------------------------------------------
# Reporting Exporter Registry
# ---------------------------------------------------------

from app.core.reporting.exporter_registry import (
    ReportExporterRegistry,
)


# ---------------------------------------------------------
# Reporting Export Execution
# ---------------------------------------------------------

from app.core.reporting.export_execution_service import (
    ReportExportExecutionService,
)


# ---------------------------------------------------------
# Analytics & KPI Contracts
# ---------------------------------------------------------

from app.core.reporting.analytics import (
    ReportKPIValueType,
    ReportKPI,
)


# ---------------------------------------------------------
# KPI Registry
# ---------------------------------------------------------

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


# ---------------------------------------------------------
# Analytics Metrics & Aggregation
# ---------------------------------------------------------

from app.core.reporting.analytics_metrics import (
    AnalyticsAggregationType,
    AnalyticsMetric,
)


# ---------------------------------------------------------
# Analytics Execution
# ---------------------------------------------------------

from app.core.reporting.analytics_execution_service import (
    ReportAnalyticsExecutionService,
)

# ---------------------------------------------------------
# Reporting Authorization
# ---------------------------------------------------------

from app.core.reporting.authorization import (
    ReportAuthorizationOperation,
    ReportAuthorizationResource,
    ReportAuthorizationSubject,
    ReportAuthorizationContext,
    ReportAuthorizationRequest,
    ReportAuthorizationDecisionStatus,
    ReportAuthorizationDecision,
)


# ---------------------------------------------------------
# Reporting Authorization Adapter
# ---------------------------------------------------------

from app.core.reporting.authorization_adapter import (
    ReportingAuthorizationAdapter,
)


# ---------------------------------------------------------
# Reporting Permissions
# ---------------------------------------------------------

from app.core.reporting.permissions import (
    ReportPermissionCode,
    permission_for_operation,
    permission_code_for_operation,
    all_report_permissions,
    register_report_permissions,
    report_permission_mapping,
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

    "ReportDataProviderRegistry",

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


    # -----------------------------------------------------
    # KPI Calculation
    # -----------------------------------------------------

    "ReportKPICalculationStatus",

    "ReportKPICalculationRequest",

    "ReportKPICalculationResult",


    # -----------------------------------------------------
    # Analytics Metrics & Aggregation
    # -----------------------------------------------------

    "AnalyticsAggregationType",

    "AnalyticsMetric",


    # -----------------------------------------------------
    # Analytics Execution
    # -----------------------------------------------------

    "ReportAnalyticsExecutionService",


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


    # -----------------------------------------------------
    # Reporting Authorization
    # -----------------------------------------------------

    "ReportAuthorizationOperation",

    "ReportAuthorizationResource",

    "ReportAuthorizationSubject",

    "ReportAuthorizationContext",

    "ReportAuthorizationRequest",

    "ReportAuthorizationDecisionStatus",

    "ReportAuthorizationDecision",

    "ReportingAuthorizationAdapter",


    # -----------------------------------------------------
    # Reporting Permissions
    # -----------------------------------------------------

    "ReportPermissionCode",

    "permission_for_operation",

    "permission_code_for_operation",

    "all_report_permissions",

    "register_report_permissions",

    "report_permission_mapping",

]
