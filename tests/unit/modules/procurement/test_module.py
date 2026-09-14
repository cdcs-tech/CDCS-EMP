"""
CDCS Enterprise Management Platform (CDCS-EMP)

Procurement Module

Module tests.
"""

from app.core.modules import BaseModule
from app.modules.procurement import ProcurementModule
from app.modules.procurement.workflows import (
    PurchaseRequestWorkflow,
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
    Supplier and PurchaseRequirement operational permissions.
    """

    module = ProcurementModule()

    assert module.has_permissions() is True
    assert len(module.permissions) == 8

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
    }


def test_procurement_module_exposes_purchase_request_workflow():
    """
    Verify that Procurement exposes the approved Purchase
    Request workflow definition.
    """

    module = ProcurementModule()

    assert module.has_workflows() is True
    assert len(module.workflows) == 1
    assert isinstance(
        module.workflows[0].workflow,
        PurchaseRequestWorkflow,
    )

    assert module.workflows[0].module_name == "PROCUREMENT"
    assert module.workflows[0].workflow_name == "purchase_request"


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
