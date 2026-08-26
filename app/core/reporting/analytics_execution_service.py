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
from app.core.reporting.authorization import (
    ReportAuthorizationRequest,
)
from app.core.reporting.authorization_adapter import (
    ReportingAuthorizationAdapter,
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
    - optional analytics authorization,
    - KPI resolution,
    - KPI calculation request construction,
    - calculation delegation,
    - calculation result validation, and
    - execution failure translation.

    Concrete calculation logic, database access, query
    generation, aggregation implementation, persistence,
    presentation, governance, auditing, telemetry, and
    scheduling remain outside this service.
    """

    def __init__(
        self,
        calculator: Callable[
            [ReportKPICalculationRequest],
            ReportKPICalculationResult,
        ],
        authorization_adapter: ReportingAuthorizationAdapter | None = None,
    ) -> None:
        """
        Initialize the analytics execution service.

        Args:
            calculator:
                Callable responsible for executing the KPI
                calculation contract.

            authorization_adapter:
                Optional reporting authorization adapter used
                when an authorization request is supplied.

        Raises:
            ValueError:
                When an invalid calculator or authorization
                adapter is supplied.
        """

        if not callable(
            calculator
        ):
            raise ValueError(
                "An analytics KPI calculator is required."
            )

        if (
            authorization_adapter is not None
            and not isinstance(
                authorization_adapter,
                ReportingAuthorizationAdapter,
            )
        ):
            raise ValueError(
                "A ReportingAuthorizationAdapter is required."
            )

        self.calculator = calculator

        self.authorization_adapter = (
            authorization_adapter
        )

    def execute(
        self,
        kpi: ReportKPI,
        *,
        data: Any = None,
        parameters: dict[str, Any] | None = None,
        metadata: dict[str, Any] | None = None,
        authorization_request: ReportAuthorizationRequest | None = None,
    ) -> ReportKPICalculationResult:
        """
        Execute an analytics KPI calculation.

        The service constructs a provider-neutral
        ReportKPICalculationRequest, optionally evaluates
        analytics authorization, and delegates calculation
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

            authorization_request:
                Optional reporting authorization request.

        Returns:
            ReportKPICalculationResult:
                The calculation result returned by the
                calculator.

        Raises:
            ValueError:
                When the KPI or optional dictionaries are
                invalid.

            ReportExecutionException:
                When authorization or calculation execution
                fails or produces an invalid result.
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
            request,
            authorization_request=authorization_request,
        )

    def execute_request(
        self,
        request: ReportKPICalculationRequest,
        *,
        authorization_request: ReportAuthorizationRequest | None = None,
    ) -> ReportKPICalculationResult:
        """
        Execute a preconstructed KPI calculation request.

        The supplied request is passed to the calculator
        without mutation.

        Args:
            request:
                Provider-neutral KPI calculation request.

            authorization_request:
                Optional reporting authorization request.

        Returns:
            ReportKPICalculationResult:
                The calculation result returned by the
                calculator.

        Raises:
            ValueError:
                When the request is invalid.

            ReportExecutionException:
                When authorization or calculation execution
                fails or produces an invalid result.
        """

        self._validate_request(
            request
        )

        self._authorize(
            authorization_request
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

    def _authorize(
        self,
        authorization_request: ReportAuthorizationRequest | None,
    ) -> None:
        """
        Evaluate analytics execution authorization when an
        authorization request is supplied.
        """

        if authorization_request is None:
            return

        if self.authorization_adapter is None:
            raise ReportExecutionException(
                "Analytics authorization adapter is required."
            )

        if authorization_request.operation.value != "execute":
            raise ReportExecutionException(
                "Analytics execution authorization requires the "
                "execute operation."
            )

        try:

            decision = self.authorization_adapter.authorize(
                authorization_request
            )

        except Exception as exc:

            raise ReportExecutionException(
                "Analytics authorization failed."
            ) from exc

        if not decision.is_allowed:
            raise ReportExecutionException(
                decision.reason
                or "Analytics execution authorization denied."
            )

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
