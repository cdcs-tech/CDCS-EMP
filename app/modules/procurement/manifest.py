"""
CDCS Enterprise Management Platform (CDCS-EMP)

Procurement Module Manifest
"""

from app.core.discovery import ModuleManifest

from app.modules.procurement.module import (
    ProcurementModule,
)


MODULE_MANIFEST = ModuleManifest(
    name="Procurement",
    code="PROCUREMENT",
    module_class=ProcurementModule,
    version="1.0.0",
    description=(
        "Procurement and purchasing management module."
    ),
    author="CDCS",
    dependencies=[],
    enabled=True,
)


__all__ = [
    "MODULE_MANIFEST",
]
