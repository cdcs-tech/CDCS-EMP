"""
CDCS Enterprise Management Platform (CDCS-EMP)

Procurement Module

Module definition and registration.
"""

from __future__ import annotations

from app.core.execution import (
    ExecutionDefinition,
)

from app.core.integration import (
    integration_provider_registry,
)

from app.core.modules.base import (
    BaseModule,
)

from app.core.modules.metadata import (
    ModuleMetadata,
)

from app.core.workflow import (
    WorkflowDefinition,
)

from app.modules.procurement.commands import (
    ApprovePurchaseOrderCommand,
    ApprovePurchaseRequestCommand,
    CancelPurchaseOrderCommand,
    RejectPurchaseOrderCommand,
    RejectPurchaseRequestCommand,
    ReturnPurchaseOrderCommand,
    ReturnPurchaseRequestCommand,
    SubmitPurchaseOrderCommand,
    SubmitPurchaseRequestCommand,
)

from app.modules.procurement.handlers import (
    ApprovePurchaseOrderHandler,
    ApprovePurchaseRequestHandler,
    CancelPurchaseOrderHandler,
    RejectPurchaseOrderHandler,
    RejectPurchaseRequestHandler,
    ReturnPurchaseOrderHandler,
    ReturnPurchaseRequestHandler,
    SubmitPurchaseOrderHandler,
    SubmitPurchaseRequestHandler,
)

from app.modules.procurement.security import (
    PROCUREMENT_PERMISSIONS,
)

from app.modules.procurement.commands import (
    ReceivePurchaseOrderCommand,
)

from app.modules.procurement.handlers import (
    ReceivePurchaseOrderHandler,
)


class ProcurementModule(BaseModule):
    """
    Provides the foundational Procurement domain model
    registration, enterprise security permission registration,
    Procurement HTTP blueprint registration, approved Purchase
    Request and Purchase Order workflow definition registration,
    approved workflow execution registration, and Procurement
    integration-provider registration.

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
        """
        Return Procurement enterprise workflow definitions.

        Workflow registration is delegated to the
        enterprise BaseModule lifecycle.
        """

        from app.modules.procurement.workflows import (
            PurchaseOrderWorkflow,
            PurchaseRequestWorkflow,
        )

        return [
            WorkflowDefinition(
                module_name="PROCUREMENT",
                workflow_name="purchase_request",
                workflow=PurchaseRequestWorkflow(),
            ),
            WorkflowDefinition(
                module_name="PROCUREMENT",
                workflow_name="purchase_order",
                workflow=PurchaseOrderWorkflow(),
            ),
        ]

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
            ExecutionDefinition(
                command=RejectPurchaseRequestCommand,
                handler=RejectPurchaseRequestHandler(),
            ),
            ExecutionDefinition(
                command=ReturnPurchaseRequestCommand,
                handler=ReturnPurchaseRequestHandler(),
            ),
            ExecutionDefinition(
                command=SubmitPurchaseOrderCommand,
                handler=SubmitPurchaseOrderHandler(),
            ),
            ExecutionDefinition(
                command=ApprovePurchaseOrderCommand,
                handler=ApprovePurchaseOrderHandler(),
            ),
            ExecutionDefinition(
                command=RejectPurchaseOrderCommand,
                handler=RejectPurchaseOrderHandler(),
            ),
            ExecutionDefinition(
                command=ReturnPurchaseOrderCommand,
                handler=ReturnPurchaseOrderHandler(),
            ),
            ExecutionDefinition(
                command=CancelPurchaseOrderCommand,
                handler=CancelPurchaseOrderHandler(),
            ),
            ExecutionDefinition(
                command=ReceivePurchaseOrderCommand,
                handler=ReceivePurchaseOrderHandler(),
            ),
        ]

    def get_execution_permissions(self) -> dict[str, str]:
        """
        Return Procurement execution permission mappings.

        Each approved Procurement workflow command is
        explicitly mapped to its corresponding Procurement
        execution permission.

        Permission definitions remain owned by the Procurement
        security boundary. This mapping only declares which
        permission is required to execute a command.
        """

        return {
            "procurement.purchase_request.submit":
                "PROCUREMENT.PURCHASE_REQUEST.SUBMIT",
            "procurement.purchase_request.approve":
                "PROCUREMENT.PURCHASE_REQUEST.APPROVE",
            "procurement.purchase_request.reject":
                "PROCUREMENT.PURCHASE_REQUEST.REJECT",
            "procurement.purchase_request.return":
                "PROCUREMENT.PURCHASE_REQUEST.RETURN",
            "procurement.purchase_order.submit":
                "PROCUREMENT.PURCHASE_ORDER.SUBMIT",
            "procurement.purchase_order.approve":
                "PROCUREMENT.PURCHASE_ORDER.APPROVE",
            "procurement.purchase_order.reject":
                "PROCUREMENT.PURCHASE_ORDER.REJECT",
            "procurement.purchase_order.return":
                "PROCUREMENT.PURCHASE_ORDER.RETURN",
            "procurement.purchase_order.cancel":
                "PROCUREMENT.PURCHASE_ORDER.CANCEL",
            "procurement.purchase_order.receive":
                "PROCUREMENT.PURCHASE_ORDER.RECEIVE",
        }

    def register_integrations(self, app) -> None:
        """
        Register Procurement-owned integration providers.

        The Inventory provider is registered through the
        enterprise IntegrationProviderRegistry. Inventory
        authorization and physical stock mutation remain
        owned by the Inventory service boundary.
        """

        if integration_provider_registry.has(
            "inventory"
        ):
            return None

        from app.modules.catering.security.authorization import (
            CateringAuthorizationAdapter,
        )

        from app.security.authorization import (
            AuthorizationService,
        )

        from app.modules.catering.services import (
            StockMovementService,
        )

        from app.modules.procurement.integration.providers.inventory import (
            InventoryReceiptIntegrationProvider,
        )

        authorization_adapter = (
            CateringAuthorizationAdapter(
                AuthorizationService.authorize_execution
            )
        )

        movement_service = StockMovementService(
            authorization_adapter=authorization_adapter,
        )

        provider = InventoryReceiptIntegrationProvider(
            movement_service=movement_service,
        )

        integration_provider_registry.register(
            provider
        )

        return None

    def initialize(self, app) -> None:
        """
        Initialize the Procurement module using the standard
        enterprise lifecycle, then register Procurement-owned
        integration providers.
        """

        super().initialize(app)

        self.register_integrations(app)

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
