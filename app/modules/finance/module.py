"""
CDCS Enterprise Management Platform (CDCS-EMP)

Finance Business Module
"""

from __future__ import annotations

from app.core.modules import (
    BaseModule,
    ModuleMetadata,
)


class FinanceModule(BaseModule):
    """
    CDCS-EMP Finance business module.

    Establishes the enterprise Finance module boundary for
    focused financial capabilities introduced through the
    approved Finance architecture.

    Domain capabilities are added incrementally through the
    Finance implementation roadmap.
    """

    def register_models(self, app) -> None:
        """
        Register Finance SQLAlchemy models.

        Importing the module-local model package ensures
        Finance models are attached to the existing
        SQLAlchemy metadata without exposing them through
        app.models.
        """

        from app.modules.finance.models import FinanceRevenue

        # Keep explicit references so the imports are intentional
        # and remain visible to static analysis.
        _ = (FinanceRevenue,)

    def get_metadata(self) -> ModuleMetadata:
        """
        Return Finance module metadata.
        """

        return ModuleMetadata(
            code="FINANCE",
            name="Finance",
            description=(
                "Focused financial management capability "
                "for financial records, revenue and related "
                "financial treatment."
            ),
            version="1.0.0",
            author="CDCS",
            category="Business",
            icon="bi-cash-stack",
            url_prefix="/finance",
            dependencies=[],
            permissions=[],
            navigation_enabled=True,
            dashboard_enabled=False,
            active=True,
        )

    def get_permissions(self):
        """
        Return Finance enterprise security permissions.

        Finance permissions will be introduced alongside the
        corresponding Finance capabilities.
        """

        return []

    def get_workflows(self):
        """
        Return Finance enterprise workflow definitions.

        Finance workflows will be introduced alongside the
        corresponding Finance capabilities.
        """

        return []

    def register_blueprints(self, app) -> None:
        """
        Register the Finance HTTP blueprint.

        No Finance HTTP blueprint exists at the module-boundary
        stage. HTTP capabilities will be introduced with the
        corresponding Finance business capability.
        """

        return None


__all__ = [
    "FinanceModule",
]
