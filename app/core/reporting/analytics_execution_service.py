"""
CDCS Enterprise Management Platform (CDCS-EMP)

Reporting & Analytics Framework

Analytics execution service.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from app.core.reporting.analytics import (
    ReportKPI,
)
from app.core.reporting.exceptions import (
    ReportExecutionException,
)
from app.core.reporting.kpi_calculation import (
    ReportKPICalculationRequest,
    ReportKPICalculationResult,
)


class ReportAnalyticsExecutionService:
    """
    Application-level service responsible for orchestrating
    provider-neutral analytics execution.

    The service coordinates:

    - analytics execution request validation,
    - KPI resolution,
    - KPI calculation request construction,
    - calculation delegation,
    - calculation result validation, and
    - execution failure translation.

    Concrete calculation logic, database access, query
    generation, aggregation implementation, persistence,
    presentation, authorization, governance, auditing,
    telemetry, and scheduling remain outside this service.
    """

    def __init__(
        self,
        calculator: Callable[
            [ReportKPICalculationRequest],
            ReportKPICalculationResult,
        ],
    ) -> None:
        """
        Initialize the analytics execution service.

        Args:
            calculator:
                Callable responsible for executing the KPI
                calculation contract.

        Raises:
            ValueError:
                When an invalid calculator is supplied.
        """

        if not callable(
            calculator
        ):
            raise ValueError(
                "An analytics KPI calculator is required."
            )

        self.calculator = calculator

    def execute(
        self,
        kpi: ReportKPI,
        *,
        data: Any = None,
        parameters: dict[str, Any] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> ReportKPICalculationResult:
        """
        Execute an analytics KPI calculation.

        The service constructs a provider-neutral
        ReportKPICalculationRequest and delegates calculation
        to the supplied calculator.

        Args:
            kpi:
                KPI definition to calculate.

            data:
                Optional calculation input data.

            parameters:
                Optional calculation parameters.

            metadata:
                Optional execution metadata.

        Returns:
            ReportKPICalculationResult:
                The calculation result returned by the
                calculator.

        Raises:
            ValueError:
                When the KPI or optional dictionaries are
                invalid.

            ReportExecutionException:
                When calculation execution fails or produces
                an invalid result.
        """

        if not isinstance(
            kpi,
            ReportKPI,
        ):
            raise ValueError(
                "Analytics execution kpi must be a "
                "ReportKPI instance."
            )

        if parameters is not None and not isinstance(
            parameters,
            dict,
        ):
            raise ValueError(
                "Analytics execution parameters must be "
                "a dictionary or None."
            )

        if metadata is not None and not isinstance(
            metadata,
            dict,
        ):
            raise ValueError(
                "Analytics execution metadata must be "
                "a dictionary or None."
            )

        request = ReportKPICalculationRequest(
            kpi=kpi,
            data=data,
            parameters=(
                {}
                if parameters is None
                else dict(parameters)
            ),
            metadata=(
                {}
                if metadata is None
                else dict(metadata)
            ),
        )

        return self.execute_request(
            request
        )

    def execute_request(
        self,
        request: ReportKPICalculationRequest,
    ) -> ReportKPICalculationResult:
        """
        Execute a preconstructed KPI calculation request.

        The supplied request is passed to the calculator
        without mutation.

        Args:
            request:
                Provider-neutral KPI calculation request.

        Returns:
            ReportKPICalculationResult:
                The calculation result returned by the
                calculator.

        Raises:
            ValueError:
                When the request is invalid.

            ReportExecutionException:
                When calculation execution fails or produces
                an invalid result.
        """

        self._validate_request(
            request
        )

        try:

            result = self.calculator(
                request
            )

        except ReportExecutionException:
            raise

        except Exception as exc:

            raise ReportExecutionException(
                "Analytics KPI execution failed."
            ) from exc

        if not isinstance(
            result,
            ReportKPICalculationResult,
        ):
            raise ReportExecutionException(
                "Analytics KPI calculator returned an "
                "invalid calculation result."
            )

        if result.kpi is not request.kpi:
            raise ReportExecutionException(
                "Analytics KPI calculator returned a result "
                "for a different KPI."
            )

        return result

    @staticmethod
    def _validate_request(
        request: ReportKPICalculationRequest,
    ) -> None:
        """
        Validate a provider-neutral KPI calculation request.
        """

        if not isinstance(
            request,
            ReportKPICalculationRequest,
        ):
            raise ValueError(
                "Analytics execution request must be a "
                "ReportKPICalculationRequest instance."
            )


__all__ = [
    "ReportAnalyticsExecutionService",
]
