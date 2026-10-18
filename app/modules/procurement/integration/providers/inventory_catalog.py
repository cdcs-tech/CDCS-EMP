"""Read-only Inventory product catalog for Procurement forms.

This adapter exposes products that are active and have an active StockItem.
It does not create cross-module foreign keys or modify Inventory records.
"""

from app.modules.catering.models.product import Product
from app.modules.catering.models.stock_item import StockItem


class InventoryProductCatalog:
    """Provide eligible Inventory product choices to Procurement."""

    @staticmethod
    def list_active_stock_managed_products() -> list[Product]:
        """Return active products with active StockItems, ordered by code."""
        return (
            Product.query.join(
                StockItem,
                StockItem.product_id == Product.id,
            )
            .filter(
                Product.is_active == True,  # noqa: E712
                StockItem.is_active == True,  # noqa: E712
            )
            .order_by(Product.code.asc())
            .all()
        )
