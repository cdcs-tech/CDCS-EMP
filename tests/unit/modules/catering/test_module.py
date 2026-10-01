"""
Catering module foundation tests.
"""

from app.core.discovery import ModuleManifest
from app.core.integration import (
    integration_provider_registry,
)
from app.core.modules import BaseModule, ModuleMetadata
from app.core.workflow import workflow_registry

from app.modules.catering import (
    CateringModule,
    MODULE_MANIFEST,
)

from app.modules.catering.integration.providers import (
    CateringExpenseIntegrationProvider,
)

from app.modules.catering.workflows import (
    StockMovementWorkflow,
    StockTransferWorkflow,
)


def test_catering_module_inherits_base_module():
    """
    Catering must integrate through the enterprise
    module framework.
    """

    module = CateringModule()

    assert isinstance(
        module,
        BaseModule,
    )


def test_catering_module_metadata_is_valid():
    """
    Catering metadata must satisfy the platform
    module metadata contract.
    """

    module = CateringModule()

    assert isinstance(
        module.metadata,
        ModuleMetadata,
    )

    assert module.metadata.validate() is True
    assert module.metadata.code == "CATERING"
    assert module.metadata.identifier == "CATERING"
    assert module.metadata.name == "Catering"


def test_catering_module_has_no_platform_dependencies():
    """
    The initial Catering boundary must not introduce
    an artificial dependency on another business module.
    """

    module = CateringModule()

    assert module.metadata.dependencies == []


def test_catering_manifest_is_valid():
    """
    The discovery manifest must satisfy the existing
    ModuleManifest contract.
    """

    assert isinstance(
        MODULE_MANIFEST,
        ModuleManifest,
    )

    assert MODULE_MANIFEST.validate() is True
    assert MODULE_MANIFEST.identifier == "CATERING"
    assert MODULE_MANIFEST.module_class is CateringModule


def test_catering_manifest_is_enabled():
    """
    Catering must be discoverable by default.
    """

    assert MODULE_MANIFEST.enabled is True


def test_catering_module_register_models_loads_module_models():
    """
    Catering model registration must load the module-local
    SQLAlchemy models without exposing them through app.models.
    """

    from app import create_app
    from app.extensions import db

    app = create_app()

    with app.app_context():
        module = CateringModule()

        module.register_models(app)

        assert "product_categories" in db.metadata.tables
        assert "products" in db.metadata.tables


def test_catering_module_models_remain_outside_global_model_package():
    """
    Catering models must remain outside the global platform
    model package even after registration.
    """

    import app.models as platform_models

    assert not hasattr(platform_models, "Product")
    assert not hasattr(platform_models, "ProductCategory")


def test_catering_module_exposes_inventory_workflows():
    """
    Catering must expose its registered workflow definitions
    through the existing enterprise module contract.
    """

    module = CateringModule()

    assert module.has_workflows() is True
    assert len(module.workflows) == 4

    workflow_names = {
        workflow.workflow_name
        for workflow in module.workflows
    }

    assert workflow_names == {
        "catering_request",
        "catering_event",
        "stock_movement",
        "stock_transfer",
    }


def test_catering_module_registers_inventory_workflows():
    """
    Catering workflow definitions must register through the
    existing BaseModule workflow-registration boundary.
    """

    workflow_registry.clear()

    module = CateringModule()

    module.register_workflows(None)

    movement = workflow_registry.get(
        "CATERING",
        "stock_movement",
    )

    transfer = workflow_registry.get(
        "CATERING",
        "stock_transfer",
    )

    assert movement is not None
    assert transfer is not None

    assert isinstance(
        movement.workflow,
        StockMovementWorkflow,
    )

    assert isinstance(
        transfer.workflow,
        StockTransferWorkflow,
    )

    workflow_registry.clear()


def test_catering_inventory_workflow_definitions_are_distinct():
    """
    Stock Movement and Stock Transfer must remain distinct
    workflow definitions even though they currently share
    the same lifecycle shape.
    """

    module = CateringModule()

    movement = next(
        workflow.workflow
        for workflow in module.workflows
        if workflow.workflow_name == "stock_movement"
    )

    transfer = next(
        workflow.workflow
        for workflow in module.workflows
        if workflow.workflow_name == "stock_transfer"
    )

    assert movement is not transfer
    assert type(movement) is StockMovementWorkflow
    assert type(transfer) is StockTransferWorkflow


def test_catering_module_exposes_integration_registration():
    """
    Verify that Catering exposes its approved integration
    provider registration boundary.
    """

    module = CateringModule()

    assert hasattr(
        module,
        "register_integrations",
    )


def test_catering_module_registers_expense_provider():
    """
    Verify that Catering registers the approved Expense
    integration provider through the enterprise registry.
    """

    module = CateringModule()

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
                "catering"
            )
        )

        assert isinstance(
            provider,
            CateringExpenseIntegrationProvider,
        )

        assert provider.provider_name == "catering"

        assert provider.consumption_service is not None

    finally:
        integration_provider_registry.clear()

        for existing_provider in original_providers:
            integration_provider_registry.register(
                existing_provider
            )


def test_catering_module_expense_registration_is_idempotent():
    """
    Verify that repeated Catering integration registration
    does not attempt duplicate Expense provider registration.
    """

    module = CateringModule()

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
                "catering"
            )
        )

        module.register_integrations(
            None
        )

        second_provider = (
            integration_provider_registry.get(
                "catering"
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
