"""
CDCS Enterprise Management Platform (CDCS-EMP)

Procurement Module

Purchase Request workflow commands.
"""

from __future__ import annotations

from app.core.execution.commands.base import (
    BaseCommand,
)

from app.core.execution.commands.metadata import (
    CommandMetadata,
)

from app.core.execution.commands.types import (
    CommandType,
)


class SubmitPurchaseRequestCommand(
    BaseCommand,
):
    """
    Command to submit a Purchase Request
    for approval.
    """

    command_name = (
        "procurement.purchase_request.submit"
    )

    command_type = CommandType.EXECUTE

    metadata = CommandMetadata(
        name="Submit Purchase Request",
        module_name="PROCUREMENT",
        operation="purchase_request.submit",
        version="1.0",
        description=(
            "Submit a Purchase Request for approval."
        ),
        category="workflow",
    )

    def __init__(
        self,
        purchase_request_id: int,
    ) -> None:
        self.purchase_request_id = (
            purchase_request_id
        )

    def validate(self) -> None:
        """Validate the command payload."""

        super().validate()

        if not isinstance(
            self.purchase_request_id,
            int,
        ):
            raise ValueError(
                "purchase_request_id must be an integer."
            )

        if self.purchase_request_id <= 0:
            raise ValueError(
                "purchase_request_id must be greater than zero."
            )

    def execute_name(self) -> str:
        """Return the represented operation name."""

        return self.command_name


class ApprovePurchaseRequestCommand(
    BaseCommand,
):
    """
    Command to approve a submitted
    Purchase Request.
    """

    command_name = (
        "procurement.purchase_request.approve"
    )

    command_type = CommandType.EXECUTE

    metadata = CommandMetadata(
        name="Approve Purchase Request",
        module_name="PROCUREMENT",
        operation="purchase_request.approve",
        version="1.0",
        description=(
            "Approve a submitted Purchase Request."
        ),
        category="workflow",
    )

    def __init__(
        self,
        purchase_request_id: int,
    ) -> None:
        self.purchase_request_id = (
            purchase_request_id
        )

    def validate(self) -> None:
        """Validate the command payload."""

        super().validate()

        if not isinstance(
            self.purchase_request_id,
            int,
        ):
            raise ValueError(
                "purchase_request_id must be an integer."
            )

        if self.purchase_request_id <= 0:
            raise ValueError(
                "purchase_request_id must be greater than zero."
            )

    def execute_name(self) -> str:
        """Return the represented operation name."""

        return self.command_name


__all__ = [
    "ApprovePurchaseRequestCommand",
    "SubmitPurchaseRequestCommand",
]
