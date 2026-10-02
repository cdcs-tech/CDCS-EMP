"""
Tests for the Finance business module.
"""

from app.core.modules import BaseModule
from app.modules.finance import FinanceModule


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


def test_finance_module_has_no_domain_capabilities_yet():
    """
    Verify that the initial Finance module boundary does not
    prematurely introduce domain models, permissions or
    workflows.
    """

    module = FinanceModule()

    assert module.get_permissions() == []
    assert module.get_workflows() == []


def test_finance_module_register_models_is_safe_before_domain_models():
    """
    Finance must remain loadable before its first domain model
    is introduced.
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
