"""
CDCS Enterprise Management Platform (CDCS-EMP)

Catering Business Module
"""

from app.core.modules import (
    BaseModule,
    ModuleMetadata,
)


class CateringModule(BaseModule):
    """
    CDCS-EMP Catering business module.

    Provides the business-module boundary for catering
    operations and related domain capabilities.
    """

    def register_models(self, app):
        """
        Register Catering SQLAlchemy models.

        Importing the module-local model package ensures
        Catering models are attached to the existing
        SQLAlchemy metadata without exposing them through
        app.models.
        """

        from app.modules.catering.models import (
            Product,
            ProductCategory,
        )

        # Keep explicit references so the imports are intentional
        # and remain visible to static analysis.
        _ = (
            Product,
            ProductCategory,
        )

    def get_metadata(self) -> ModuleMetadata:
        """
        Return Catering module metadata.
        """

        return ModuleMetadata(
            code="CATERING",
            name="Catering",
            description=(
                "Catering operations management module "
                "for food service, purchasing, inventory, "
                "income, expenses, invoicing and receipts."
            ),
            version="1.0.0",
            author="CDCS",
            category="Business",
            icon="bi-cup-hot",
            url_prefix="/catering",
            dependencies=[],
            permissions=[],
            navigation_enabled=True,
            dashboard_enabled=False,
            active=True,
        )


__all__ = [
    "CateringModule",
]
