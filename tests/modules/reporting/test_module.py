"""
Tests for the Reporting enterprise module.
"""

from flask import Flask

from app.core.startup.modules import initialize_modules
from app.core.execution import command_registry

from app.core.modules import BaseModule
from app.core.reporting.permissions import (
    ReportPermissionCode,
    all_report_permissions,
)
from app.core.discovery import ModuleDiscovery
from app.modules.reporting import ReportingModule
from app.modules.reporting.manifest import MODULE_MANIFEST


def test_reporting_module_inherits_base_module():
    module = ReportingModule()

    assert isinstance(module, BaseModule)


def test_reporting_module_exposes_expected_metadata():
    module = ReportingModule()
    metadata = module.get_metadata()

    assert metadata.code == "REPORTING"
    assert metadata.name == "Reporting"
    assert metadata.version == "1.0.0"
    assert metadata.author == "CDCS"
    assert metadata.category == "Business"
    assert metadata.icon == "bi-graph-up"
    assert metadata.url_prefix == "/reports"
    assert metadata.dependencies == []
    assert metadata.navigation_enabled is False
    assert metadata.dashboard_enabled is False
    assert metadata.active is True


def test_reporting_module_exposes_canonical_permissions():
    module = ReportingModule()

    permissions = module.get_permissions()

    assert permissions == list(all_report_permissions())
    assert {permission.code for permission in permissions} == {
        ReportPermissionCode.VIEW,
        ReportPermissionCode.EXECUTE,
        ReportPermissionCode.EXPORT,
        ReportPermissionCode.MANAGE,
    }


def test_reporting_module_manifest_is_discoverable():
    assert MODULE_MANIFEST.name == "Reporting"
    assert MODULE_MANIFEST.code == "REPORTING"
    assert MODULE_MANIFEST.module_class is ReportingModule
    assert MODULE_MANIFEST.version == "1.0.0"
    assert MODULE_MANIFEST.author == "CDCS"
    assert MODULE_MANIFEST.dependencies == []
    assert MODULE_MANIFEST.enabled is True


def test_reporting_module_is_found_by_production_discovery():
    manifests = ModuleDiscovery().discover()

    reporting_manifests = [
        manifest
        for manifest in manifests
        if manifest.code == "REPORTING"
    ]

    assert len(reporting_manifests) == 1
    assert reporting_manifests[0].module_class is ReportingModule


def test_production_startup_registers_reporting_module_and_permissions():
    """Verify Reporting is registered through production module startup."""

    command_registry.clear()

    try:
        app = Flask(__name__)

        manager = initialize_modules(app)

        # Startup exposes the same manager through Flask extensions.
        assert app.extensions["module_manager"] is manager

        # Reporting is registered and available as an active module.
        reporting_module = manager.get_module("REPORTING")

        assert reporting_module in manager.get_active_modules()
        assert isinstance(reporting_module, ReportingModule)

        # The production manager exposes all canonical permissions.
        assert {
            permission.code
            for permission in reporting_module.get_permissions()
        } == {
            ReportPermissionCode.VIEW,
            ReportPermissionCode.EXECUTE,
            ReportPermissionCode.EXPORT,
            ReportPermissionCode.MANAGE,
        }
    finally:
        command_registry.clear()
