"""
Catering module foundation tests.
"""

from app.core.discovery import ModuleManifest
from app.core.modules import BaseModule, ModuleMetadata

from app.modules.catering import (
    CateringModule,
    MODULE_MANIFEST,
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
