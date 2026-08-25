"""
CDCS Enterprise Management Platform (CDCS-EMP)

Reporting & Analytics Framework Tests

Analytics execution service contract tests.
"""

from __future__ import annotations

import pytest

from app.core.reporting import (
    ReportKPI,
    ReportKPIValueType,
    ReportKPICalculationRequest,
    ReportKPICalculationResult,
    ReportKPICalculationStatus,
    ReportAnalyticsExecutionService,
    ReportExecutionException,
)


def make_kpi(
    code: str = "TOTAL_USERS",
) -> ReportKPI:

    return ReportKPI(
        code=code,
        name="Total Users",
        value_type=ReportKPIValueType.INTEGER,
    )


def make_result(
    kpi: ReportKPI,
    value=10,
) -> ReportKPICalculationResult:

    return ReportKPICalculationResult(
        kpi=kpi,
        value=value,
        status=ReportKPICalculationStatus.SUCCESS,
    )


def test_analytics_execution_service_is_publicly_available():

    from app.core.reporting import (
        ReportAnalyticsExecutionService as PublicService,
    )

    assert (
        PublicService
        is ReportAnalyticsExecutionService
    )


def test_analytics_execution_service_rejects_invalid_calculator():

    with pytest.raises(
        ValueError,
        match="analytics KPI calculator",
    ):
        ReportAnalyticsExecutionService(
            None
        )


def test_analytics_execution_service_accepts_callable():

    service = ReportAnalyticsExecutionService(
        lambda request: make_result(
            request.kpi
        )
    )

    assert callable(
        service.calculator
    )


def test_analytics_execution_service_execute_delegates_to_calculator():

    calls = []

    def calculator(
        request,
    ):

        calls.append(
            request
        )

        return make_result(
            request.kpi,
            25,
        )

    service = ReportAnalyticsExecutionService(
        calculator
    )

    kpi = make_kpi()

    result = service.execute(
        kpi
    )

    assert result.value == 25
    assert len(calls) == 1
    assert calls[0].kpi is kpi


def test_analytics_execution_service_passes_data_to_calculator():

    captured = {}

    def calculator(
        request,
    ):

        captured["request"] = request

        return make_result(
            request.kpi
        )

    service = ReportAnalyticsExecutionService(
        calculator
    )

    data = [
        {"value": 10},
        {"value": 20},
    ]

    service.execute(
        make_kpi(),
        data=data,
    )

    assert (
        captured["request"].data
        is data
    )


def test_analytics_execution_service_passes_parameters():

    captured = {}

    def calculator(
        request,
    ):

        captured["parameters"] = request.parameters

        return make_result(
            request.kpi
        )

    service = ReportAnalyticsExecutionService(
        calculator
    )

    parameters = {
        "department": "HR",
        "year": 2026,
    }

    service.execute(
        make_kpi(),
        parameters=parameters,
    )

    assert (
        captured["parameters"]
        == parameters
    )


def test_analytics_execution_service_passes_metadata():

    captured = {}

    def calculator(
        request,
    ):

        captured["metadata"] = request.metadata

        return make_result(
            request.kpi
        )

    service = ReportAnalyticsExecutionService(
        calculator
    )

    metadata = {
        "source": "analytics",
        "request_id": "REQ-001",
    }

    service.execute(
        make_kpi(),
        metadata=metadata,
    )

    assert (
        captured["metadata"]
        == metadata
    )


def test_analytics_execution_service_defaults_optional_dictionaries():

    captured = {}

    def calculator(
        request,
    ):

        captured["request"] = request

        return make_result(
            request.kpi
        )

    service = ReportAnalyticsExecutionService(
        calculator
    )

    service.execute(
        make_kpi()
    )

    assert (
        captured["request"].parameters
        == {}
    )

    assert (
        captured["request"].metadata
        == {}
    )


def test_analytics_execution_service_execute_request_accepts_valid_request():

    captured = {}

    def calculator(
        request,
    ):

        captured["request"] = request

        return make_result(
            request.kpi,
            42,
        )

    service = ReportAnalyticsExecutionService(
        calculator
    )

    kpi = make_kpi()

    request = ReportKPICalculationRequest(
        kpi=kpi,
        data=[1, 2, 3],
        parameters={
            "x": 1,
        },
        metadata={
            "source": "test",
        },
    )

    result = service.execute_request(
        request
    )

    assert result.value == 42
    assert (
        captured["request"]
        is request
    )


def test_analytics_execution_service_rejects_invalid_request():

    service = ReportAnalyticsExecutionService(
        lambda request: make_result(
            request.kpi
        )
    )

    with pytest.raises(
        ValueError,
        match="ReportKPICalculationRequest",
    ):
        service.execute_request(
            object()
        )


def test_analytics_execution_service_rejects_invalid_kpi():

    service = ReportAnalyticsExecutionService(
        lambda request: make_result(
            request.kpi
        )
    )

    with pytest.raises(
        ValueError,
        match="ReportKPI",
    ):
        service.execute(
            object()
        )


def test_analytics_execution_service_rejects_invalid_parameters():

    service = ReportAnalyticsExecutionService(
        lambda request: make_result(
            request.kpi
        )
    )

    with pytest.raises(
        ValueError,
        match="parameters",
    ):
        service.execute(
            make_kpi(),
            parameters=[],
        )


def test_analytics_execution_service_rejects_invalid_metadata():

    service = ReportAnalyticsExecutionService(
        lambda request: make_result(
            request.kpi
        )
    )

    with pytest.raises(
        ValueError,
        match="metadata",
    ):
        service.execute(
            make_kpi(),
            metadata=[],
        )


def test_analytics_execution_service_returns_calculator_result_unchanged():

    result = make_result(
        make_kpi(),
        99,
    )

    service = ReportAnalyticsExecutionService(
        lambda request: result
    )

    returned = service.execute(
        result.kpi
    )

    assert (
        returned
        is result
    )


def test_analytics_execution_service_preserves_kpi_identity():

    kpi = make_kpi()

    service = ReportAnalyticsExecutionService(
        lambda request: make_result(
            request.kpi
        )
    )

    result = service.execute(
        kpi
    )

    assert (
        result.kpi
        is kpi
    )


def test_analytics_execution_service_does_not_modify_parameters():

    parameters = {
        "department": "Finance",
    }

    original = dict(
        parameters
    )

    captured = {}

    def calculator(
        request,
    ):

        captured["request"] = request

        return make_result(
            request.kpi
        )

    service = ReportAnalyticsExecutionService(
        calculator
    )

    service.execute(
        make_kpi(),
        parameters=parameters,
    )

    assert (
        parameters
        == original
    )

    assert (
        captured["request"].parameters
        == original
    )

    assert (
        captured["request"].parameters
        is not parameters
    )


def test_analytics_execution_service_does_not_modify_metadata():

    metadata = {
        "source": "test",
    }

    original = dict(
        metadata
    )

    captured = {}

    def calculator(
        request,
    ):

        captured["request"] = request

        return make_result(
            request.kpi
        )

    service = ReportAnalyticsExecutionService(
        calculator
    )

    service.execute(
        make_kpi(),
        metadata=metadata,
    )

    assert (
        metadata
        == original
    )

    assert (
        captured["request"].metadata
        == original
    )

    assert (
        captured["request"].metadata
        is not metadata
    )


def test_analytics_execution_service_translates_calculator_failure():

    def calculator(
        request,
    ):

        raise RuntimeError(
            "calculator failure"
        )

    service = ReportAnalyticsExecutionService(
        calculator
    )

    with pytest.raises(
        ReportExecutionException,
        match="Analytics KPI execution failed",
    ):
        service.execute(
            make_kpi()
        )


def test_analytics_execution_service_preserves_report_execution_exception():

    original = ReportExecutionException(
        "existing execution failure"
    )

    def calculator(
        request,
    ):

        raise original

    service = ReportAnalyticsExecutionService(
        calculator
    )

    with pytest.raises(
        ReportExecutionException,
        match="existing execution failure",
    ) as exc_info:

        service.execute(
            make_kpi()
        )

    assert (
        exc_info.value
        is original
    )


def test_analytics_execution_service_rejects_invalid_calculator_result():

    service = ReportAnalyticsExecutionService(
        lambda request: object()
    )

    with pytest.raises(
        ReportExecutionException,
        match="invalid calculation result",
    ):
        service.execute(
            make_kpi()
        )


def test_analytics_execution_service_rejects_result_for_different_kpi():

    first_kpi = make_kpi(
        "TOTAL_USERS"
    )

    second_kpi = make_kpi(
        "TOTAL_CASES"
    )

    service = ReportAnalyticsExecutionService(
        lambda request: make_result(
            second_kpi
        )
    )

    with pytest.raises(
        ReportExecutionException,
        match="different KPI",
    ):
        service.execute(
            first_kpi
        )


def test_analytics_execution_service_execute_request_preserves_request_identity():

    kpi = make_kpi()

    request = ReportKPICalculationRequest(
        kpi=kpi,
        data=[1, 2, 3],
        parameters={
            "period": "2026",
        },
        metadata={
            "source": "test",
        },
    )

    captured = {}

    def calculator(
        calculation_request,
    ):

        captured["request"] = calculation_request

        return make_result(
            calculation_request.kpi,
            6,
        )

    service = ReportAnalyticsExecutionService(
        calculator
    )

    result = service.execute_request(
        request
    )

    assert (
        captured["request"]
        is request
    )

    assert result.value == 6


def test_analytics_execution_service_supports_empty_calculation_result():

    kpi = make_kpi()

    result = ReportKPICalculationResult(
        kpi=kpi,
        value=None,
        status=ReportKPICalculationStatus.EMPTY,
    )

    service = ReportAnalyticsExecutionService(
        lambda request: result
    )

    returned = service.execute(
        kpi
    )

    assert (
        returned.status
        is ReportKPICalculationStatus.EMPTY
    )

    assert returned.value is None


def test_analytics_execution_service_supports_failed_calculation_result():

    kpi = make_kpi()

    result = ReportKPICalculationResult(
        kpi=kpi,
        value=None,
        status=ReportKPICalculationStatus.FAILED,
        error="Calculation failed.",
    )

    service = ReportAnalyticsExecutionService(
        lambda request: result
    )

    returned = service.execute(
        kpi
    )

    assert (
        returned.status
        is ReportKPICalculationStatus.FAILED
    )

    assert (
        returned.error
        == "Calculation failed."
    )


def test_analytics_execution_service_preserves_result_metadata():

    kpi = make_kpi()

    result = ReportKPICalculationResult(
        kpi=kpi,
        value=123,
        metadata={
            "calculated_by": "test",
        },
    )

    service = ReportAnalyticsExecutionService(
        lambda request: result
    )

    returned = service.execute(
        kpi
    )

    assert (
        returned.metadata
        == {
            "calculated_by": "test",
        }
    )


def test_analytics_execution_service_accepts_callable_object():

    class Calculator:

        def __call__(
            self,
            request,
        ):

            return make_result(
                request.kpi,
                7,
            )

    service = ReportAnalyticsExecutionService(
        Calculator()
    )

    result = service.execute(
        make_kpi()
    )

    assert result.value == 7
