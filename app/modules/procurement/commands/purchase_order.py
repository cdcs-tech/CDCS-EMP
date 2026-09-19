"""
CDCS Enterprise Management Platform (CDCS-EMP)

Procurement Module

Purchase Order workflow commands.
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


class SubmitPurchaseOrderCommand(
    BaseCommand,
):
    """
    Command to submit a Purchase Order
    for approval.
    """

    command_name = (
        "procurement.purchase_order.submit"
    )

    command_type = CommandType.EXECUTE

    metadata = CommandMetadata(
        name="Submit Purchase Order",
        module_name="PROCUREMENT",
        operation="purchase_order.submit",
        version="1.0",
        description=(
            "Submit a Purchase Order for approval."
        ),
        category="workflow",
    )

    def __init__(
        self,
        purchase_order_id: int,
    ) -> None:
        self.purchase_order_id = (
            purchase_order_id
        )

    def validate(self) -> None:
        """Validate the command payload."""

        super().validate()

        if not isinstance(
            self.purchase_order_id,
            int,
        ):
            raise ValueError(
                "purchase_order_id must be an integer."
            )

        if self.purchase_order_id <= 0:
            raise ValueError(
                "purchase_order_id must be greater than zero."
            )

    def execute_name(self) -> str:
        """Return the represented operation name."""

        return self.command_name


class ApprovePurchaseOrderCommand(
    BaseCommand,
):
    """
    Command to approve a submitted
    Purchase Order.
    """

    command_name = (
        "procurement.purchase_order.approve"
    )

    command_type = CommandType.EXECUTE

    metadata = CommandMetadata(
        name="Approve Purchase Order",
        module_name="PROCUREMENT",
        operation="purchase_order.approve",
        version="1.0",
        description=(
            "Approve a submitted Purchase Order."
        ),
        category="workflow",
    )

    def __init__(
        self,
        purchase_order_id: int,
    ) -> None:
        self.purchase_order_id = (
            purchase_order_id
        )

    def validate(self) -> None:
        """Validate the command payload."""

        super().validate()

        if not isinstance(
            self.purchase_order_id,
            int,
        ):
            raise ValueError(
                "purchase_order_id must be an integer."
            )

        if self.purchase_order_id <= 0:
            raise ValueError(
                "purchase_order_id must be greater than zero."
            )

    def execute_name(self) -> str:
        """Return the represented operation name."""

        return self.command_name


class RejectPurchaseOrderCommand(
    BaseCommand,
):
    """
    Command to reject a submitted
    Purchase Order.
    """

    command_name = (
        "procurement.purchase_order.reject"
    )

    command_type = CommandType.EXECUTE

    metadata = CommandMetadata(
        name="Reject Purchase Order",
        module_name="PROCUREMENT",
        operation="purchase_order.reject",
        version="1.0",
        description=(
            "Reject a submitted Purchase Order."
        ),
        category="workflow",
    )

    def __init__(
        self,
        purchase_order_id: int,
    ) -> None:
        self.purchase_order_id = (
            purchase_order_id
        )

    def validate(self) -> None:
        """Validate the command payload."""

        super().validate()

        if not isinstance(
            self.purchase_order_id,
            int,
        ):
            raise ValueError(
                "purchase_order_id must be an integer."
            )

        if self.purchase_order_id <= 0:
            raise ValueError(
                "purchase_order_id must be greater than zero."
            )

    def execute_name(self) -> str:
        """Return the represented operation name."""

        return self.command_name


class ReturnPurchaseOrderCommand(
    BaseCommand,
):
    """
    Command to return a submitted
    Purchase Order to draft.
    """

    command_name = (
        "procurement.purchase_order.return"
    )

    command_type = CommandType.EXECUTE

    metadata = CommandMetadata(
        name="Return Purchase Order",
        module_name="PROCUREMENT",
        operation="purchase_order.return",
        version="1.0",
        description=(
            "Return a submitted Purchase Order to draft."
        ),
        category="workflow",
    )

    def __init__(
        self,
        purchase_order_id: int,
    ) -> None:
        self.purchase_order_id = (
            purchase_order_id
        )

    def validate(self) -> None:
        """Validate the command payload."""

        super().validate()

        if not isinstance(
            self.purchase_order_id,
            int,
        ):
            raise ValueError(
                "purchase_order_id must be an integer."
            )

        if self.purchase_order_id <= 0:
            raise ValueError(
                "purchase_order_id must be greater than zero."
            )

    def execute_name(self) -> str:
        """Return the represented operation name."""

        return self.command_name


class CancelPurchaseOrderCommand(
    BaseCommand,
):
    """
    Command to cancel an approved
    Purchase Order.
    """

    command_name = (
        "procurement.purchase_order.cancel"
    )

    command_type = CommandType.EXECUTE

    metadata = CommandMetadata(
        name="Cancel Purchase Order",
        module_name="PROCUREMENT",
        operation="purchase_order.cancel",
        version="1.0",
        description=(
            "Cancel an approved Purchase Order."
        ),
        category="workflow",
    )

    def __init__(
        self,
        purchase_order_id: int,
    ) -> None:
        self.purchase_order_id = (
            purchase_order_id
        )

    def validate(self) -> None:
        """Validate the command payload."""

        super().validate()

        if not isinstance(
            self.purchase_order_id,
            int,
        ):
            raise ValueError(
                "purchase_order_id must be an integer."
            )

        if self.purchase_order_id <= 0:
            raise ValueError(
                "purchase_order_id must be greater than zero."
            )

    def execute_name(self) -> str:
        """Return the represented operation name."""

        return self.command_name


__all__ = [
    "ApprovePurchaseOrderCommand",
    "CancelPurchaseOrderCommand",
    "RejectPurchaseOrderCommand",
    "ReturnPurchaseOrderCommand",
    "SubmitPurchaseOrderCommand",
]
