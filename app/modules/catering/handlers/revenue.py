"""
CDCS Enterprise Management Platform (CDCS-EMP)

Catering Revenue execution handlers.
"""

from __future__ import annotations

from app.core.execution.context import (
    ExecutionContext,
)
from app.core.execution.handlers import (
    BaseCommandHandler,
)
from app.core.execution.results import (
    ExecutionResult,
)

from app.modules.catering.commands import (
    RecognizeCateringRevenueCommand,
)
from app.modules.catering.services import (
    CateringRevenueService,
)


class RecognizeCateringRevenueHandler(
    BaseCommandHandler
):
    """
    Handle Catering Revenue recognition.
    """

    command_type = (
        RecognizeCateringRevenueCommand
    )

    def __init__(
        self,
        service: CateringRevenueService | None = None,
    ) -> None:

        self.service = (
            service
            or CateringRevenueService()
        )

    def handle(
        self,
        command: RecognizeCateringRevenueCommand,
        context: ExecutionContext,
    ) -> ExecutionResult:
        """
        Recognize a Catering Revenue record
        through the existing Catering service.
        """

        revenue = self.service.get(
            command.revenue_id
        )

        previous_status = revenue.status

        try:
            self.service.recognize(
                revenue,
                subject=context,
            )
        except ValueError as exc:
            return ExecutionResult.failure_result(
                message=str(exc),
                data=revenue,
                metadata={
                    "revenue_id": revenue.id,
                    "previous_status": previous_status,
                    "new_status": revenue.status,
                    "operation": context.operation,
                },
            )

        return ExecutionResult.success_result(
            data=revenue,
            message=(
                "Catering Revenue recognized."
            ),
            metadata={
                "revenue_id": revenue.id,
                "previous_status": previous_status,
                "new_status": revenue.status,
                "recognized_at": revenue.recognized_at,
                "operation": context.operation,
            },
        )


__all__ = [
    "RecognizeCateringRevenueHandler",
]
