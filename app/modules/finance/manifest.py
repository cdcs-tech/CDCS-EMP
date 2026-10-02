"""
CDCS Enterprise Management Platform (CDCS-EMP)

Finance Module Manifest
"""

from app.core.discovery import ModuleManifest

from app.modules.finance.module import FinanceModule


MODULE_MANIFEST = ModuleManifest(
    name="Finance",
    code="FINANCE",
    module_class=FinanceModule,
    version="1.0.0",
    description=(
        "Focused financial management capability."
    ),
    author="CDCS",
    dependencies=[],
    enabled=True,
)


__all__ = [
    "MODULE_MANIFEST",
]
