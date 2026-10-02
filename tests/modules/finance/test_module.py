"""
Tests for the Finance business module.
"""

from app.core.modules import BaseModule
from app.core.workflow import WorkflowDefinition
from app.modules.finance import FinanceModule
from app.modules.finance.workflows import FinanceRevenueWorkflow


def test_finance_module_inherits_base_module():
    """
    Verify that FinanceModule uses the enterprise BaseModule
    contract.
    """

    module = FinanceModule()

    assert isinstance(
        module,
        BaseModule,
    )


def test_finance_module_exposes_expected_metadata():
    """
    FinanceModule exposes the approved enterprise module
    metadata.
    """

    module = FinanceModule()

    metadata = module.get_metadata()

    assert metadata.code == "FINANCE"
    assert metadata.name == "Finance"
    assert metadata.version == "1.0.0"
    assert metadata.author == "CDCS"
    assert metadata.category == "Business"
    assert metadata.icon == "bi-cash-stack"
    assert metadata.url_prefix == "/finance"
    assert metadata.dependencies == []
    assert metadata.navigation_enabled is True
    assert metadata.dashboard_enabled is False
    assert metadata.active is True


def test_finance_module_exposes_revenue_workflow():
    """
    Verify that the Finance Revenue lifecycle is registered
    through the enterprise workflow definition contract.
    """

    module = FinanceModule()

    workflows = module.get_workflows()

    assert len(workflows) == 1

    definition = workflows[0]

    assert isinstance(
        definition,
        WorkflowDefinition,
    )
    assert definition.module_name == "FINANCE"
    assert definition.workflow_name == "finance_revenue"
    assert isinstance(
        definition.workflow,
        FinanceRevenueWorkflow,
    )


def test_finance_module_exposes_no_permissions_yet():
    """
    Finance permissions remain deferred until the corresponding
    Finance capabilities introduce their security requirements.
    """

    module = FinanceModule()

    assert module.get_permissions() == []


def test_finance_module_register_models_is_safe():
    """
    Verify that Finance model registration remains safe.
    """

    module = FinanceModule()

    assert module.register_models(None) is None


def test_finance_module_manifest_is_discoverable():
    """
    Verify that the Finance manifest exposes the enterprise
    module discovery contract.
    """

    from app.modules.finance.manifest import MODULE_MANIFEST

    assert MODULE_MANIFEST.name == "Finance"
    assert MODULE_MANIFEST.code == "FINANCE"
    assert MODULE_MANIFEST.module_class is FinanceModule
    assert MODULE_MANIFEST.version == "1.0.0"
    assert MODULE_MANIFEST.author == "CDCS"
    assert MODULE_MANIFEST.dependencies == []
    assert MODULE_MANIFEST.enabled is True
