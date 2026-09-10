"""
CDCS Enterprise Management Platform (CDCS-EMP)

Procurement Business Module
"""

from app.core.modules import (
    BaseModule,
    ModuleMetadata,
)


class ProcurementModule(BaseModule):
    """
    CDCS-EMP Procurement business module.

    Provides the business-module boundary for procurement
    and purchasing capabilities.
    """

    def register_models(self, app):
        """
        Register Procurement SQLAlchemy models.

        Importing the module-local model package ensures
        Procurement models are attached to the existing
        SQLAlchemy metadata without exposing them through
        app.models.
        """

        from app.modules.procurement.models import (
            PurchaseOrder,
            PurchaseOrderLine,
            PurchaseRequest,
            PurchaseRequestLine,
            PurchaseRequirement,
            Supplier,
        )

        # Keep explicit references so the imports are intentional
        # and remain visible to static analysis.
        _ = (
            Supplier,
            PurchaseRequirement,
            PurchaseRequest,
            PurchaseRequestLine,
            PurchaseOrder,
            PurchaseOrderLine,
        )

    def get_metadata(self) -> ModuleMetadata:
        """
        Return Procurement module metadata.
        """

        return ModuleMetadata(
            code="PROCUREMENT",
            name="Procurement",
            description=(
                "Procurement and purchasing management "
                "module."
            ),
            version="1.0.0",
            author="CDCS",
            category="Business",
            icon="bi-cart-check",
            url_prefix="/procurement",
            dependencies=[],
            permissions=[],
            navigation_enabled=True,
            dashboard_enabled=False,
            active=True,
        )


__all__ = [
    "ProcurementModule",
]
