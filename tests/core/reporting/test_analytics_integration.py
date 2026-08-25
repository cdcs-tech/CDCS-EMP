"""
CDCS Enterprise Management Platform (CDCS-EMP)

Reporting & Analytics Framework

Stage 1.16.7.6 — Analytics Integration Verification

Integration verification for the complete Analytics & KPI
Framework.
"""

from __future__ import annotations

import pytest

from app.core.reporting import (
    AnalyticsAggregationType,
    AnalyticsMetric,
    ReportAnalyticsExecutionService,
    ReportKPI,
    ReportKPIRegistry,
    ReportKPICalculationRequest,
    ReportKPICalculationResult,
    ReportKPICalculationStatus,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def kpi() -> ReportKPI:
    """Return a representative report KPI definition."""

    return ReportKPI(
        code="total_beneficiaries",
        name="Total Beneficiaries",
        description="Total number of registered beneficiaries.",
        value_type="integer",
        unit="persons",
        category="beneficiaries",
        metadata={
            "source": "beneficiary_registry",
        },
    )


@pytest.fixture
def metric() -> AnalyticsMetric:
    """Return a representative analytics metric."""

    return AnalyticsMetric(
        code="total_beneficiaries",
        name="Total Beneficiaries",
        aggregation=AnalyticsAggregationType.COUNT,
        category="beneficiaries",
        metadata={
            "purpose": "integration-test",
        },
    )


@pytest.fixture
def registry(
    kpi: ReportKPI,
) -> ReportKPIRegistry:
    """Return a KPI registry containing the test KPI."""

    return ReportKPIRegistry(
        [kpi]
    )


# ---------------------------------------------------------------------------
# KPI Definition / Registry Integration
# ---------------------------------------------------------------------------


def test_kpi_definition_can_be_registered_and_resolved(
    kpi: ReportKPI,
    registry: ReportKPIRegistry,
) -> None:
    """
    Verify that a KPI definition can flow from the KPI
    contract into the KPI registry and be resolved again.
    """

    assert registry.has(
        kpi.identifier
    )

    resolved = registry.get(
        kpi.identifier
    )

    assert resolved is kpi
    assert resolved.identifier == "TOTAL_BENEFICIARIES"


def test_kpi_registry_preserves_registered_definition(
    kpi: ReportKPI,
    registry: ReportKPIRegistry,
) -> None:
    """
    Verify that registry resolution preserves the complete
    provider-neutral KPI definition.
    """

    resolved = registry.get(
        "total_beneficiaries"
    )

    assert resolved.code == kpi.code
    assert resolved.name == kpi.name
    assert resolved.value_type is kpi.value_type
    assert resolved.unit == kpi.unit
    assert resolved.category == kpi.category
    assert resolved.metadata == kpi.metadata


# ---------------------------------------------------------------------------
# Analytics Metric / Aggregation Integration
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "aggregation",
    [
        AnalyticsAggregationType.COUNT,
        AnalyticsAggregationType.SUM,
        AnalyticsAggregationType.AVERAGE,
        AnalyticsAggregationType.MINIMUM,
        AnalyticsAggregationType.MAXIMUM,
    ],
)
def test_analytics_metric_supports_established_aggregation_types(
    aggregation: AnalyticsAggregationType,
) -> None:
    """
    Verify that every supported aggregation type can be
    represented by an AnalyticsMetric.
    """

    source = (
        None
        if aggregation is AnalyticsAggregationType.COUNT
        else "amount"
    )

    metric = AnalyticsMetric(
        code=f"metric_{aggregation.value}",
        name=f"Metric {aggregation.label}",
        aggregation=aggregation,
        source=source,
    )

    assert metric.aggregation is aggregation
    assert metric.to_dict()["aggregation"] == (
        aggregation.value
    )


def test_metric_identifier_is_provider_neutral(
    metric: AnalyticsMetric,
) -> None:
    """
    Verify that metric identity remains independent of
    execution implementation.
    """

    assert metric.identifier == "TOTAL_BENEFICIARIES"
    assert metric.code == "total_beneficiaries"


# ---------------------------------------------------------------------------
# KPI Calculation Request Integration
# ---------------------------------------------------------------------------


def test_kpi_can_be_transformed_into_calculation_request(
    kpi: ReportKPI,
) -> None:
    """
    Verify that the KPI definition participates correctly
    in the KPI calculation request contract.
    """

    request = ReportKPICalculationRequest(
        kpi=kpi,
        data=[
            {"id": 1},
            {"id": 2},
            {"id": 3},
        ],
        parameters={
            "include_inactive": False,
        },
        metadata={
            "execution_source": "integration-test",
        },
    )

    assert request.kpi is kpi
    assert request.kpi_code == "total_beneficiaries"
    assert request.identifier == "TOTAL_BENEFICIARIES"
    assert request.data == [
        {"id": 1},
        {"id": 2},
        {"id": 3},
    ]
    assert request.parameters == {
        "include_inactive": False,
    }
    assert request.metadata == {
        "execution_source": "integration-test",
    }


# ---------------------------------------------------------------------------
# Analytics Execution Service Integration
# ---------------------------------------------------------------------------


def test_analytics_execution_service_integrates_kpi_and_calculation(
    kpi: ReportKPI,
) -> None:
    """
    Verify the complete KPI-to-calculation execution path.
    """

    captured: dict[str, object] = {}

    def calculator(
        request: ReportKPICalculationRequest,
    ) -> ReportKPICalculationResult:
        captured["request"] = request

        return ReportKPICalculationResult(
            kpi=request.kpi,
            value=3,
            status=ReportKPICalculationStatus.SUCCESS,
            metadata=dict(
                request.metadata
            ),
        )

    service = ReportAnalyticsExecutionService(
        calculator
    )

    result = service.execute(
        kpi,
        data=[
            {"id": 1},
            {"id": 2},
            {"id": 3},
        ],
        parameters={
            "include_inactive": False,
        },
        metadata={
            "execution_source": "integration-test",
        },
    )

    request = captured["request"]

    assert isinstance(
        request,
        ReportKPICalculationRequest,
    )

    assert request.kpi is kpi
    assert request.data == [
        {"id": 1},
        {"id": 2},
        {"id": 3},
    ]
    assert request.parameters == {
        "include_inactive": False,
    }
    assert request.metadata == {
        "execution_source": "integration-test",
    }

    assert isinstance(
        result,
        ReportKPICalculationResult,
    )

    assert result.kpi is kpi
    assert result.identifier == "TOTAL_BENEFICIARIES"
    assert result.value == 3
    assert result.status is (
        ReportKPICalculationStatus.SUCCESS
    )
    assert result.is_success is True


def test_analytics_execution_service_preserves_result_metadata(
    kpi: ReportKPI,
) -> None:
    """
    Verify that calculation-result metadata survives the
    analytics execution boundary.
    """

    expected_metadata = {
        "source": "beneficiary_registry",
        "execution_id": "integration-test-001",
    }

    def calculator(
        request: ReportKPICalculationRequest,
    ) -> ReportKPICalculationResult:
        return ReportKPICalculationResult(
            kpi=request.kpi,
            value=42,
            status=ReportKPICalculationStatus.SUCCESS,
            metadata=expected_metadata,
        )

    service = ReportAnalyticsExecutionService(
        calculator
    )

    result = service.execute(
        kpi
    )

    assert result.metadata == expected_metadata
    assert result.value == 42


def test_analytics_execution_service_supports_empty_result(
    kpi: ReportKPI,
) -> None:
    """
    Verify that the analytics execution service preserves
    the EMPTY calculation-result state.
    """

    def calculator(
        request: ReportKPICalculationRequest,
    ) -> ReportKPICalculationResult:
        return ReportKPICalculationResult(
            kpi=request.kpi,
            value=None,
            status=ReportKPICalculationStatus.EMPTY,
            message="No qualifying records.",
        )

    service = ReportAnalyticsExecutionService(
        calculator
    )

    result = service.execute(
        kpi
    )

    assert result.kpi is kpi
    assert result.value is None
    assert result.status is (
        ReportKPICalculationStatus.EMPTY
    )
    assert result.is_empty is True
    assert result.is_success is False
    assert result.message == "No qualifying records."


def test_analytics_execution_service_supports_failed_result(
    kpi: ReportKPI,
) -> None:
    """
    Verify that the analytics execution service preserves
    the FAILED calculation-result state.
    """

    def calculator(
        request: ReportKPICalculationRequest,
    ) -> ReportKPICalculationResult:
        return ReportKPICalculationResult(
            kpi=request.kpi,
            value=None,
            status=ReportKPICalculationStatus.FAILED,
            error="Calculation provider failure.",
        )

    service = ReportAnalyticsExecutionService(
        calculator
    )

    result = service.execute(
        kpi
    )

    assert result.kpi is kpi
    assert result.value is None
    assert result.status is (
        ReportKPICalculationStatus.FAILED
    )
    assert result.is_failed is True
    assert result.is_success is False
    assert result.error == (
        "Calculation provider failure."
    )


def test_analytics_execution_service_preserves_kpi_identity(
    kpi: ReportKPI,
) -> None:
    """
    Verify that the calculation result remains associated
    with the exact KPI supplied to the execution service.
    """

    def calculator(
        request: ReportKPICalculationRequest,
    ) -> ReportKPICalculationResult:
        return ReportKPICalculationResult(
            kpi=request.kpi,
            value=100,
        )

    service = ReportAnalyticsExecutionService(
        calculator
    )

    result = service.execute(
        kpi
    )

    assert result.kpi is kpi
    assert result.kpi_code == kpi.code
    assert result.identifier == kpi.identifier


def test_analytics_execution_service_does_not_mutate_input_dictionaries(
    kpi: ReportKPI,
) -> None:
    """
    Verify that execution does not mutate caller-owned
    parameters or metadata dictionaries.
    """

    parameters = {
        "period": "monthly",
    }

    metadata = {
        "source": "integration-test",
    }

    original_parameters = dict(
        parameters
    )
    original_metadata = dict(
        metadata
    )

    captured: dict[str, object] = {}

    def calculator(
        request: ReportKPICalculationRequest,
    ) -> ReportKPICalculationResult:
        captured["request"] = request

        return ReportKPICalculationResult(
            kpi=request.kpi,
            value=12,
        )

    service = ReportAnalyticsExecutionService(
        calculator
    )

    service.execute(
        kpi,
        parameters=parameters,
        metadata=metadata,
    )

    assert parameters == original_parameters
    assert metadata == original_metadata

    request = captured["request"]

    assert isinstance(
        request,
        ReportKPICalculationRequest,
    )

    assert request.parameters == original_parameters
    assert request.metadata == original_metadata


# ---------------------------------------------------------------------------
# Error Boundary Integration
# ---------------------------------------------------------------------------


def test_analytics_execution_service_translates_calculator_failure(
    kpi: ReportKPI,
) -> None:
    """
    Verify that an implementation-level calculator failure
    is translated into the reporting execution boundary.
    """

    def calculator(
        request: ReportKPICalculationRequest,
    ) -> ReportKPICalculationResult:
        raise RuntimeError(
            "Simulated calculator failure."
        )

    service = ReportAnalyticsExecutionService(
        calculator
    )

    with pytest.raises(
        Exception,
        match="Analytics KPI execution failed",
    ):
        service.execute(
            kpi
        )


def test_analytics_execution_service_rejects_invalid_calculation_result(
    kpi: ReportKPI,
) -> None:
    """
    Verify that the execution boundary rejects a calculator
    returning a non-contract result.
    """

    def calculator(
        request: ReportKPICalculationRequest,
    ):
        return {
            "kpi": request.kpi.code,
            "value": 10,
        }

    service = ReportAnalyticsExecutionService(
        calculator
    )

    with pytest.raises(
        Exception,
        match="invalid calculation result",
    ):
        service.execute(
            kpi
        )


def test_analytics_execution_service_rejects_result_for_different_kpi(
    kpi: ReportKPI,
) -> None:
    """
    Verify that the execution service rejects a calculation
    result associated with a different KPI.
    """

    different_kpi = ReportKPI(
        code="different_kpi",
        name="Different KPI",
        value_type="integer",
    )

    def calculator(
        request: ReportKPICalculationRequest,
    ) -> ReportKPICalculationResult:
        return ReportKPICalculationResult(
            kpi=different_kpi,
            value=10,
        )

    service = ReportAnalyticsExecutionService(
        calculator
    )

    with pytest.raises(
        Exception,
        match="different KPI",
    ):
        service.execute(
            kpi
        )


# ---------------------------------------------------------------------------
# Public API Integration
# ---------------------------------------------------------------------------


def test_analytics_framework_components_are_publicly_available() -> None:
    """
    Verify that the complete Stage 1.16.7 public analytics
    surface is available through app.core.reporting.
    """

    from app.core.reporting import (
        AnalyticsAggregationType as PublicAggregationType,
        AnalyticsMetric as PublicAnalyticsMetric,
        ReportAnalyticsExecutionService as PublicExecutionService,
        ReportKPI as PublicKPI,
        ReportKPIRegistry as PublicKPIRegistry,
        ReportKPICalculationRequest as PublicCalculationRequest,
        ReportKPICalculationResult as PublicCalculationResult,
        ReportKPICalculationStatus as PublicCalculationStatus,
    )

    assert PublicAggregationType is AnalyticsAggregationType
    assert PublicAnalyticsMetric is AnalyticsMetric
    assert PublicExecutionService is (
        ReportAnalyticsExecutionService
    )
    assert PublicKPI is ReportKPI
    assert PublicKPIRegistry is ReportKPIRegistry
    assert PublicCalculationRequest is (
        ReportKPICalculationRequest
    )
    assert PublicCalculationResult is (
        ReportKPICalculationResult
    )
    assert PublicCalculationStatus is (
        ReportKPICalculationStatus
    )


# ---------------------------------------------------------------------------
# Complete Analytics Flow
# ---------------------------------------------------------------------------


def test_complete_analytics_kpi_flow(
    kpi: ReportKPI,
    metric: AnalyticsMetric,
) -> None:
    """
    Verify the complete Stage 1.16.7 analytics flow from KPI
    registration through metric definition and execution to
    the final calculation result.
    """

    registry = ReportKPIRegistry(
        [kpi]
    )

    resolved_kpi = registry.get(
        metric.identifier
    )

    captured: dict[str, object] = {}

    def calculator(
        request: ReportKPICalculationRequest,
    ) -> ReportKPICalculationResult:
        captured["request"] = request

        data = request.data

        assert isinstance(
            data,
            list,
        )

        return ReportKPICalculationResult(
            kpi=request.kpi,
            value=len(data),
            status=ReportKPICalculationStatus.SUCCESS,
            metadata={
                "aggregation": metric.aggregation.value,
                "metric": metric.identifier,
            },
        )

    service = ReportAnalyticsExecutionService(
        calculator
    )

    result = service.execute(
        resolved_kpi,
        data=[
            {"id": 1},
            {"id": 2},
            {"id": 3},
            {"id": 4},
        ],
        metadata={
            "integration": "stage-1.16.7.6",
        },
    )

    request = captured["request"]

    assert isinstance(
        request,
        ReportKPICalculationRequest,
    )

    assert request.kpi is kpi
    assert request.identifier == metric.identifier

    assert result.kpi is kpi
    assert result.identifier == "TOTAL_BENEFICIARIES"
    assert result.value == 4
    assert result.is_success is True

    assert result.metadata == {
        "aggregation": "count",
        "metric": "TOTAL_BENEFICIARIES",
    }
