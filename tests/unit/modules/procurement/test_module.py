"""
Procurement module foundation tests.
"""

from app.core.discovery import (
    ModuleDiscovery,
    ModuleManifest,
)

from app.core.modules import (
    BaseModule,
    ModuleMetadata,
)

from app.modules.procurement import (
    MODULE_MANIFEST,
    ProcurementModule,
)


def test_procurement_module_inherits_base_module():
    """
    Procurement must integrate through the enterprise
    module framework.
    """

    module = ProcurementModule()

    assert isinstance(
        module,
        BaseModule,
    )


def test_procurement_module_metadata_is_valid():
    """
    Procurement metadata must satisfy the platform
    module metadata contract.
    """

    module = ProcurementModule()

    assert isinstance(
        module.metadata,
        ModuleMetadata,
    )

    assert module.metadata.validate() is True
    assert module.metadata.code == "PROCUREMENT"
    assert module.metadata.identifier == "PROCUREMENT"
    assert module.metadata.name == "Procurement"


def test_procurement_module_has_no_business_module_dependencies():
    """
    The initial Procurement boundary must not introduce
    an artificial dependency on another business module.
    """

    module = ProcurementModule()

    assert module.metadata.dependencies == []


def test_procurement_module_has_no_foundation_workflows_or_permissions():
    """
    Procurement Foundation must not prematurely introduce
    workflow or module-specific permission behavior.
    """

    module = ProcurementModule()

    assert module.has_workflows() is False
    assert module.has_permissions() is False


def test_procurement_manifest_is_valid():
    """
    The discovery manifest must satisfy the existing
    ModuleManifest contract.
    """

    assert isinstance(
        MODULE_MANIFEST,
        ModuleManifest,
    )

    assert MODULE_MANIFEST.validate() is True
    assert MODULE_MANIFEST.identifier == "PROCUREMENT"
    assert MODULE_MANIFEST.module_class is ProcurementModule


def test_procurement_manifest_is_enabled():
    """
    Procurement must be discoverable by default.
    """

    assert MODULE_MANIFEST.enabled is True


def test_procurement_manifest_is_discoverable():
    """
    Procurement must integrate with the existing enterprise
    module discovery mechanism without a new discovery path.
    """

    manifests = ModuleDiscovery().discover()

    procurement_manifests = [
        manifest
        for manifest in manifests
        if manifest.identifier == "PROCUREMENT"
    ]

    assert len(procurement_manifests) == 1
    assert procurement_manifests[0].module_class is ProcurementModule
