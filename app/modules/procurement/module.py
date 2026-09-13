"""
CDCS Enterprise Management Platform (CDCS-EMP)

Procurement Module

Module definition and registration.
"""

from __future__ import annotations

from app.core.execution import (
    ExecutionDefinition,
)

from app.core.modules.base import (
    BaseModule,
)

from app.core.modules.metadata import (
    ModuleMetadata,
)

from app.modules.procurement.commands import (
    ApprovePurchaseRequestCommand,
    SubmitPurchaseRequestCommand,
)

from app.modules.procurement.handlers import (
    ApprovePurchaseRequestHandler,
    SubmitPurchaseRequestHandler,
)

from app.modules.procurement.security import (
    PROCUREMENT_PERMISSIONS,
)


class ProcurementModule(
    BaseModule,
):
    """
    Procurement business module.

    Provides the foundational Procurement domain model
    registration, enterprise security permission registration,
    Procurement HTTP blueprint registration, and approved
    Purchase Request workflow execution registration.

    Operational workflows and cross-module integrations are
    introduced only at their approved implementation stages.
    """

    def __init__(self) -> None:
        super().__init__()

    def get_metadata(self) -> ModuleMetadata:
        return ModuleMetadata(
            code="PROCUREMENT",
            name="Procurement",
            description=(
                "Procurement and purchasing management module."
            ),
            version="1.0.0",
            author="CDCS",
            category="Business",
            icon="bi-cart-check",
            url_prefix="/procurement",
            dependencies=[],
            permissions=[],
            navigation_enabled=True,
            dashboard_enabled=False,
            active=True,
        )

    def register_models(self, app) -> None:
        from app.modules.procurement.models import (
            PurchaseOrder,
            PurchaseOrderLine,
            PurchaseRequest,
            PurchaseRequestLine,
            PurchaseRequirement,
            Supplier,
        )

        _ = (
            PurchaseOrder,
            PurchaseOrderLine,
            PurchaseRequest,
            PurchaseRequestLine,
            PurchaseRequirement,
            Supplier,
        )

    def get_permissions(self):
        return list(PROCUREMENT_PERMISSIONS)

    def get_workflows(self):
        return []

    def get_execution_definitions(self):
        """
        Return Procurement workflow execution definitions.

        Workflow command authorization and transaction management
        remain owned by the enterprise execution dispatcher.
        """

        return [
            ExecutionDefinition(
                command=SubmitPurchaseRequestCommand,
                handler=SubmitPurchaseRequestHandler(),
            ),
            ExecutionDefinition(
                command=ApprovePurchaseRequestCommand,
                handler=ApprovePurchaseRequestHandler(),
            ),
        ]

    def register_blueprints(self, app):
        """
        Register the Procurement HTTP blueprint.

        The blueprint is registered through the Enterprise
        Module Framework lifecycle.
        """

        from app.modules.procurement.routes import (
            procurement_bp,
        )

        app.register_blueprint(
            procurement_bp,
            url_prefix=self.metadata.url_prefix,
        )


__all__ = [
    "ProcurementModule",
]
