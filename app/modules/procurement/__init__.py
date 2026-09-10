"""
CDCS Enterprise Management Platform (CDCS-EMP)

Procurement Business Module

Public API.
"""

from app.modules.procurement.module import (
    ProcurementModule,
)

from app.modules.procurement.manifest import (
    MODULE_MANIFEST,
)


__all__ = [
    "ProcurementModule",
    "MODULE_MANIFEST",
]
