"""
CDCS Enterprise Management Platform (CDCS-EMP)

Catering Business Module
"""

from app.core.modules import (
    BaseModule,
    ModuleMetadata,
)

from app.modules.catering.security import (
    CATERING_PERMISSIONS,
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
            InventoryLocation,
            Product,
            ProductCategory,
            StockBalance,
            StockItem,
            StockMovement,
            StockTransfer,
        )

        # Keep explicit references so the imports are intentional
        # and remain visible to static analysis.
        _ = (
            Product,
            ProductCategory,
            StockItem,
            InventoryLocation,
            StockBalance,
            StockMovement,
            StockTransfer,
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

    def get_permissions(self):
        """
        Return Catering enterprise security permissions.

        Permission registration is delegated to the
        enterprise BaseModule lifecycle.
        """

        return list(
            CATERING_PERMISSIONS
        )

    def register_blueprints(self, app):
        """
        Register the Catering HTTP blueprint.

        The blueprint is registered through the
        Enterprise Module Framework lifecycle.
        """

        from app.modules.catering.routes import (
            catering_bp,
        )

        app.register_blueprint(
            catering_bp,
            url_prefix=self.metadata.url_prefix,
        )


__all__ = [
    "CateringModule",
]
