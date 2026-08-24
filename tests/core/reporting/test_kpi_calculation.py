"""
CDCS Enterprise Management Platform (CDCS-EMP)

Reporting & Analytics Framework Tests

KPI calculation contract tests.
"""

from __future__ import annotations

import pytest

from app.core.reporting import (
    ReportKPI,
    ReportKPICalculationRequest,
    ReportKPICalculationResult,
    ReportKPICalculationStatus,
)


def create_kpi(
    code: str = "total_staff",
    name: str = "Total Staff",
) -> ReportKPI:

    return ReportKPI(
        code=code,
        name=name,
    )


def test_kpi_calculation_status_defines_success():

    assert (
        ReportKPICalculationStatus.SUCCESS.value
        == "success"
    )


def test_kpi_calculation_status_defines_empty():

    assert (
        ReportKPICalculationStatus.EMPTY.value
        == "empty"
    )


def test_kpi_calculation_status_defines_failed():

    assert (
        ReportKPICalculationStatus.FAILED.value
        == "failed"
    )


def test_kpi_calculation_request_accepts_kpi():

    kpi = create_kpi()

    request = ReportKPICalculationRequest(
        kpi=kpi
    )

    assert request.kpi is kpi


def test_kpi_calculation_request_preserves_data():

    kpi = create_kpi()

    data = {
        "staff": 125,
        "department": "HR",
    }

    request = ReportKPICalculationRequest(
        kpi=kpi,
        data=data,
    )

    assert request.data is data


def test_kpi_calculation_request_preserves_parameters():

    kpi = create_kpi()

    parameters = {
        "year": 2026,
        "quarter": 3,
    }

    request = ReportKPICalculationRequest(
        kpi=kpi,
        parameters=parameters,
    )

    assert request.parameters == parameters

    assert request.parameters is not parameters


def test_kpi_calculation_request_preserves_metadata():

    kpi = create_kpi()

    metadata = {
        "source": "HR",
        "version": 1,
    }

    request = ReportKPICalculationRequest(
        kpi=kpi,
        metadata=metadata,
    )

    assert request.metadata == metadata

    assert request.metadata is not metadata


def test_kpi_calculation_request_exposes_kpi_code():

    request = ReportKPICalculationRequest(
        kpi=create_kpi(
            code="active_staff"
        )
    )

    assert request.kpi_code == "active_staff"


def test_kpi_calculation_request_exposes_identifier():

    request = ReportKPICalculationRequest(
        kpi=create_kpi(
            code="active_staff"
        )
    )

    assert request.identifier == "ACTIVE_STAFF"


def test_kpi_calculation_request_defaults_are_empty():

    request = ReportKPICalculationRequest(
        kpi=create_kpi()
    )

    assert request.data is None
    assert request.parameters == {}
    assert request.metadata == {}


def test_kpi_calculation_request_rejects_invalid_kpi():

    with pytest.raises(
        ValueError,
        match="kpi must be a ReportKPI",
    ):
        ReportKPICalculationRequest(
            kpi=object()
        )


def test_kpi_calculation_request_rejects_invalid_parameters():

    with pytest.raises(
        ValueError,
        match="parameters must be a dictionary",
    ):
        ReportKPICalculationRequest(
            kpi=create_kpi(),
            parameters=[],
        )


def test_kpi_calculation_request_rejects_invalid_metadata():

    with pytest.raises(
        ValueError,
        match="metadata must be a dictionary",
    ):
        ReportKPICalculationRequest(
            kpi=create_kpi(),
            metadata=[],
        )


def test_kpi_calculation_request_to_dict():

    kpi = create_kpi()

    request = ReportKPICalculationRequest(
        kpi=kpi,
        data=125,
        parameters={
            "year": 2026,
        },
        metadata={
            "source": "HR",
        },
    )

    result = request.to_dict()

    assert result == {
        "kpi": kpi.to_dict(),
        "data": 125,
        "parameters": {
            "year": 2026,
        },
        "metadata": {
            "source": "HR",
        },
    }


def test_kpi_calculation_request_is_immutable():

    request = ReportKPICalculationRequest(
        kpi=create_kpi()
    )

    with pytest.raises(
        AttributeError
    ):
        request.kpi = create_kpi(
            code="another_kpi"
        )


def test_kpi_calculation_result_defaults_to_success():

    result = ReportKPICalculationResult(
        kpi=create_kpi(),
        value=125,
    )

    assert (
        result.status
        is ReportKPICalculationStatus.SUCCESS
    )

    assert result.value == 125


def test_kpi_calculation_result_preserves_value():

    result = ReportKPICalculationResult(
        kpi=create_kpi(),
        value=98.75,
    )

    assert result.value == 98.75


def test_kpi_calculation_result_preserves_metadata():

    metadata = {
        "source": "Finance",
        "period": "2026-Q3",
    }

    result = ReportKPICalculationResult(
        kpi=create_kpi(),
        value=98.75,
        metadata=metadata,
    )

    assert result.metadata == metadata
    assert result.metadata is not metadata


def test_kpi_calculation_result_preserves_message():

    result = ReportKPICalculationResult(
        kpi=create_kpi(),
        status=ReportKPICalculationStatus.EMPTY,
        message="No data available.",
    )

    assert result.message == "No data available."


def test_kpi_calculation_result_preserves_error():

    result = ReportKPICalculationResult(
        kpi=create_kpi(),
        status=ReportKPICalculationStatus.FAILED,
        error="Calculation failed.",
    )

    assert result.error == "Calculation failed."


@pytest.mark.parametrize(
    "status, expected",
    [
        (
            "success",
            ReportKPICalculationStatus.SUCCESS,
        ),
        (
            "SUCCESS",
            ReportKPICalculationStatus.SUCCESS,
        ),
        (
            " success ",
            ReportKPICalculationStatus.SUCCESS,
        ),
        (
            "empty",
            ReportKPICalculationStatus.EMPTY,
        ),
        (
            "EMPTY",
            ReportKPICalculationStatus.EMPTY,
        ),
        (
            "failed",
            ReportKPICalculationStatus.FAILED,
        ),
        (
            "FAILED",
            ReportKPICalculationStatus.FAILED,
        ),
    ],
)
def test_kpi_calculation_result_normalizes_status(
    status,
    expected,
):

    result = ReportKPICalculationResult(
        kpi=create_kpi(),
        status=status,
    )

    assert result.status is expected


@pytest.mark.parametrize(
    "status",
    [
        "",
        " ",
        "unsupported",
        "unknown",
        None,
        123,
        object(),
    ],
)
def test_kpi_calculation_result_rejects_invalid_status(
    status,
):

    with pytest.raises(
        ValueError,
        match="KPI calculation",
    ):
        ReportKPICalculationResult(
            kpi=create_kpi(),
            status=status,
        )


def test_kpi_calculation_result_rejects_invalid_kpi():

    with pytest.raises(
        ValueError,
        match="kpi must be a ReportKPI",
    ):
        ReportKPICalculationResult(
            kpi=object()
        )


@pytest.mark.parametrize(
    "status",
    [
        ReportKPICalculationStatus.SUCCESS,
        ReportKPICalculationStatus.EMPTY,
        ReportKPICalculationStatus.FAILED,
    ],
)
def test_kpi_calculation_result_status_flags(
    status,
):

    result = ReportKPICalculationResult(
        kpi=create_kpi(),
        status=status,
    )

    assert result.is_success is (
        status
        is ReportKPICalculationStatus.SUCCESS
    )

    assert result.is_empty is (
        status
        is ReportKPICalculationStatus.EMPTY
    )

    assert result.is_failed is (
        status
        is ReportKPICalculationStatus.FAILED
    )


def test_kpi_calculation_result_exposes_kpi_code():

    result = ReportKPICalculationResult(
        kpi=create_kpi(
            code="active_staff"
        )
    )

    assert result.kpi_code == "active_staff"


def test_kpi_calculation_result_exposes_identifier():

    result = ReportKPICalculationResult(
        kpi=create_kpi(
            code="active_staff"
        )
    )

    assert result.identifier == "ACTIVE_STAFF"


def test_kpi_calculation_result_to_dict():

    kpi = create_kpi()

    result = ReportKPICalculationResult(
        kpi=kpi,
        value=125,
        status=ReportKPICalculationStatus.SUCCESS,
        metadata={
            "source": "HR",
        },
        message="Calculation completed.",
        error=None,
    )

    assert result.to_dict() == {
        "kpi": kpi.to_dict(),
        "value": 125,
        "status": "success",
        "metadata": {
            "source": "HR",
        },
        "message": "Calculation completed.",
        "error": None,
    }


def test_public_kpi_calculation_contracts_are_available():

    from app.core.reporting import (
        ReportKPICalculationRequest as PublicRequest,
        ReportKPICalculationResult as PublicResult,
        ReportKPICalculationStatus as PublicStatus,
    )

    from app.core.reporting.kpi_calculation import (
        ReportKPICalculationRequest,
        ReportKPICalculationResult,
        ReportKPICalculationStatus,
    )

    assert PublicRequest is ReportKPICalculationRequest
    assert PublicResult is ReportKPICalculationResult
    assert PublicStatus is ReportKPICalculationStatus
