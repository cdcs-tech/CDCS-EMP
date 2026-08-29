"""
CDCS Enterprise Management Platform (CDCS-EMP)

Catering Module Manifest
"""

from app.core.discovery import ModuleManifest

from app.modules.catering.module import (
    CateringModule,
)


MODULE_MANIFEST = ModuleManifest(
    name="Catering",
    code="CATERING",
    module_class=CateringModule,
    version="1.0.0",
    description=(
        "Catering operations management module."
    ),
    author="CDCS",
    dependencies=[],
    enabled=True,
)


__all__ = [
    "MODULE_MANIFEST",
]
