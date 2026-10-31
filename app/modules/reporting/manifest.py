"""
Reporting Module Manifest
"""

from app.core.discovery import ModuleManifest

from app.modules.reporting.module import (
    ReportingModule,
)


MODULE_MANIFEST = ModuleManifest(
    name="Reporting",
    code="REPORTING",
    module_class=ReportingModule,
    version="1.0.0",
    description=(
        "Enterprise reporting and analytics capabilities."
    ),
    author="CDCS",
    dependencies=[],
    enabled=True,
)


__all__ = [
    "MODULE_MANIFEST",
]
