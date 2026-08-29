"""
CDCS Enterprise Management Platform (CDCS-EMP)

Catering Business Module

Public API.
"""

from app.modules.catering.module import (
    CateringModule,
)

from app.modules.catering.manifest import (
    MODULE_MANIFEST,
)


__all__ = [
    "CateringModule",
    "MODULE_MANIFEST",
]
