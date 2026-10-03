"""
CDCS Enterprise Management Platform (CDCS-EMP)

Catering Revenue execution commands.
"""

from __future__ import annotations

from app.core.execution.commands import (
    BaseCommand,
    CommandMetadata,
    CommandType,
)


class RecognizeCateringRevenueCommand(
    BaseCommand
):
    """
    Recognize an eligible Catering Revenue record.

    Recognition is an explicit Catering business operation.
    Finance delivery occurs separately through the post-commit
    integration boundary.
    """

    command_name = (
        "catering.revenue.recognize"
    )

    command_type = CommandType.EXECUTE

    metadata = CommandMetadata(
        name="Recognize Catering Revenue",
        module_name="CATERING",
        operation="catering.revenue.recognize",
        version="1.0",
        description=(
            "Recognize an eligible Catering "
            "Revenue record."
        ),
        category="workflow",
    )

    def __init__(
        self,
        revenue_id: int,
    ) -> None:

        self.revenue_id = revenue_id

    def validate(self) -> None:
        """
        Validate the command payload.
        """

        if not isinstance(
            self.revenue_id,
            int,
        ):
            raise ValueError(
                "revenue_id must be an integer."
            )

        if self.revenue_id <= 0:
            raise ValueError(
                "revenue_id must be greater than zero."
            )

    def execute_name(self) -> str:
        """
        Return the enterprise execution name.
        """

        return self.command_name


__all__ = [
    "RecognizeCateringRevenueCommand",
]
