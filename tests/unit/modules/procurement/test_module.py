"""
CDCS Enterprise Management Platform (CDCS-EMP)

Procurement Module

Module tests.
"""

from app.core.modules import BaseModule
from app.modules.procurement import ProcurementModule
from app.modules.procurement.workflows import (
    PurchaseOrderWorkflow,
    PurchaseRequestWorkflow,
)

from app.core.integration import (
    integration_provider_registry,
)

from app.modules.procurement.integration.providers.inventory import (
    InventoryReceiptIntegrationProvider,
)


def test_procurement_module_inherits_base_module():
    """
    Verify that ProcurementModule uses the enterprise
    BaseModule contract.
    """
    module = ProcurementModule()

    assert isinstance(
        module,
        BaseModule,
    )


def test_procurement_module_metadata_is_valid():
    """
    Verify the Procurement module metadata.
    """
    module = ProcurementModule()

    assert module.metadata.code == "PROCUREMENT"
    assert module.metadata.name == "Procurement"
    assert module.metadata.version == "1.0.0"
    assert module.metadata.author == "CDCS"
    assert module.metadata.category == "Business"
    assert module.metadata.icon == "bi-cart-check"
    assert module.metadata.url_prefix == "/procurement"
    assert module.metadata.dependencies == []
    assert module.metadata.navigation_enabled is True
    assert module.metadata.dashboard_enabled is False
    assert module.metadata.active is True


def test_procurement_module_has_no_business_module_dependencies():
    """
    Verify that Procurement has no dependencies on other
    business modules.
    """
    module = ProcurementModule()

    assert module.metadata.dependencies == []


def test_procurement_module_exposes_procurement_permissions():
    """
    Verify that the Procurement module exposes the approved
    Procurement business, workflow, and integration permissions.
    """
    module = ProcurementModule()

    assert module.has_permissions() is True
    assert len(module.permissions) == 34

    permission_codes = {
        permission.code
        for permission in module.permissions
    }

    assert permission_codes == {
        "PROCUREMENT.SUPPLIER.CREATE",
        "PROCUREMENT.SUPPLIER.READ",
        "PROCUREMENT.SUPPLIER.UPDATE",
        "PROCUREMENT.SUPPLIER.DELETE",
        "PROCUREMENT.PURCHASE_REQUIREMENT.CREATE",
        "PROCUREMENT.PURCHASE_REQUIREMENT.READ",
        "PROCUREMENT.PURCHASE_REQUIREMENT.UPDATE",
        "PROCUREMENT.PURCHASE_REQUIREMENT.DELETE",
        "PROCUREMENT.PURCHASE_REQUEST.CREATE",
        "PROCUREMENT.PURCHASE_REQUEST.READ",
        "PROCUREMENT.PURCHASE_REQUEST.UPDATE",
        "PROCUREMENT.PURCHASE_REQUEST.DELETE",
        "PROCUREMENT.PURCHASE_REQUEST.SUBMIT",
        "PROCUREMENT.PURCHASE_REQUEST.APPROVE",
        "PROCUREMENT.PURCHASE_REQUEST.REJECT",
        "PROCUREMENT.PURCHASE_REQUEST.RETURN",
        "PROCUREMENT.PURCHASE_REQUEST_LINE.CREATE",
        "PROCUREMENT.PURCHASE_REQUEST_LINE.READ",
        "PROCUREMENT.PURCHASE_REQUEST_LINE.UPDATE",
        "PROCUREMENT.PURCHASE_REQUEST_LINE.DELETE",
        "PROCUREMENT.PURCHASE_ORDER.CREATE",
        "PROCUREMENT.PURCHASE_ORDER.READ",
        "PROCUREMENT.PURCHASE_ORDER.UPDATE",
        "PROCUREMENT.PURCHASE_ORDER.DELETE",
        "PROCUREMENT.PURCHASE_ORDER.SUBMIT",
        "PROCUREMENT.PURCHASE_ORDER.APPROVE",
        "PROCUREMENT.PURCHASE_ORDER.REJECT",
        "PROCUREMENT.PURCHASE_ORDER.RETURN",
        "PROCUREMENT.PURCHASE_ORDER.CANCEL",
        "PROCUREMENT.PURCHASE_ORDER.RECEIVE",
        "PROCUREMENT.PURCHASE_ORDER_LINE.CREATE",
        "PROCUREMENT.PURCHASE_ORDER_LINE.READ",
        "PROCUREMENT.PURCHASE_ORDER_LINE.UPDATE",
        "PROCUREMENT.PURCHASE_ORDER_LINE.DELETE",
    }


def test_procurement_module_exposes_purchase_request_workflow():
    """
    Verify that Procurement exposes the approved Purchase
    Request workflow definition.
    """
    module = ProcurementModule()

    assert module.has_workflows() is True
    assert len(module.workflows) == 2

    purchase_request_workflow = next(
        workflow
        for workflow in module.workflows
        if workflow.workflow_name == "purchase_request"
    )

    assert isinstance(
        purchase_request_workflow.workflow,
        PurchaseRequestWorkflow,
    )

    assert purchase_request_workflow.module_name == "PROCUREMENT"


def test_procurement_module_exposes_purchase_order_workflow():
    """
    Verify that Procurement exposes the approved Purchase Order
    workflow definition.
    """
    module = ProcurementModule()

    assert module.has_workflows() is True

    purchase_order_workflow = next(
        workflow
        for workflow in module.workflows
        if workflow.workflow_name == "purchase_order"
    )

    assert isinstance(
        purchase_order_workflow.workflow,
        PurchaseOrderWorkflow,
    )

    assert purchase_order_workflow.module_name == "PROCUREMENT"
    assert purchase_order_workflow.workflow_name == "purchase_order"


def test_procurement_module_registers_models():
    """
    Verify that Procurement models remain registered through
    the standard module model-registration mechanism.
    """
    module = ProcurementModule()

    assert hasattr(
        module,
        "register_models",
    )


def test_procurement_module_public_import_boundary():
    """
    Verify that ProcurementModule is publicly exposed by
    the Procurement module package.
    """
    from app.modules.procurement import ProcurementModule as ImportedModule

    assert ImportedModule is ProcurementModule


def test_procurement_module_exposes_purchase_request_execution_permissions():
    """
    Procurement exposes the approved Purchase Request
    workflow command-to-permission mappings.
    """
    module = ProcurementModule()

    execution_permissions = module.get_execution_permissions()

    assert {
        key: execution_permissions[key]
        for key in (
            "procurement.purchase_request.submit",
            "procurement.purchase_request.approve",
            "procurement.purchase_request.reject",
            "procurement.purchase_request.return",
        )
    } == {
        "procurement.purchase_request.submit":
            "PROCUREMENT.PURCHASE_REQUEST.SUBMIT",
        "procurement.purchase_request.approve":
            "PROCUREMENT.PURCHASE_REQUEST.APPROVE",
        "procurement.purchase_request.reject":
            "PROCUREMENT.PURCHASE_REQUEST.REJECT",
        "procurement.purchase_request.return":
            "PROCUREMENT.PURCHASE_REQUEST.RETURN",
    }


def test_procurement_module_exposes_purchase_order_execution_permissions():
    """
    Procurement exposes the approved Purchase Order
    workflow command-to-permission mappings.
    """
    module = ProcurementModule()

    execution_permissions = module.get_execution_permissions()

    assert {
        key: execution_permissions[key]
        for key in (
            "procurement.purchase_order.submit",
            "procurement.purchase_order.approve",
            "procurement.purchase_order.reject",
            "procurement.purchase_order.return",
            "procurement.purchase_order.cancel",
        )
    } == {
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
    }


def test_procurement_module_exposes_integration_registration():
    """
    Verify that Procurement exposes its approved integration
    provider registration boundary.
    """
    module = ProcurementModule()

    assert hasattr(
        module,
        "register_integrations",
    )


def test_procurement_module_registers_inventory_provider():
    """
    Verify that Procurement registers the approved Inventory
    integration provider through the enterprise registry.
    """
    module = ProcurementModule()

    original_providers = (
        integration_provider_registry.all()
    )

    try:
        integration_provider_registry.clear()

        module.register_integrations(
            None
        )

        provider = (
            integration_provider_registry.get(
                "inventory"
            )
        )

        assert isinstance(
            provider,
            InventoryReceiptIntegrationProvider,
        )

        assert provider.provider_name == "inventory"

        assert provider.movement_service is not None

        assert (
            provider.movement_service.authorization_adapter
            is not None
        )

    finally:
        integration_provider_registry.clear()

        for existing_provider in original_providers:
            integration_provider_registry.register(
                existing_provider
            )


def test_procurement_module_inventory_registration_is_idempotent():
    """
    Verify that repeated Procurement integration registration
    does not attempt duplicate Inventory provider registration.
    """
    module = ProcurementModule()

    original_providers = (
        integration_provider_registry.all()
    )

    try:
        integration_provider_registry.clear()

        module.register_integrations(
            None
        )

        first_provider = (
            integration_provider_registry.get(
                "inventory"
            )
        )

        module.register_integrations(
            None
        )

        second_provider = (
            integration_provider_registry.get(
                "inventory"
            )
        )

        assert first_provider is second_provider

        assert (
            integration_provider_registry.count()
            == 1
        )

    finally:
        integration_provider_registry.clear()

        for existing_provider in original_providers:
            integration_provider_registry.register(
                existing_provider
            )
