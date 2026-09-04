"""
CDCS Enterprise Management Platform (CDCS-EMP)

Catering Repositories

Module-local persistence repositories.
"""

from .balance import StockBalanceRepository
from .location import InventoryLocationRepository
from .movement import StockMovementRepository
from .product import ProductRepository
from .product_category import ProductCategoryRepository
from .stock_item import StockItemRepository
from .transfer import StockTransferRepository

__all__ = [
    "ProductRepository",
    "ProductCategoryRepository",
    "StockItemRepository",
    "InventoryLocationRepository",
    "StockBalanceRepository",
    "StockMovementRepository",
    "StockTransferRepository",
]
