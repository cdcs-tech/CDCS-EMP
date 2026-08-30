"""
CDCS Enterprise Management Platform (CDCS-EMP)

Catering Repositories

Module-local persistence repositories.
"""

from .product import ProductRepository
from .product_category import ProductCategoryRepository

__all__ = [
    "ProductRepository",
    "ProductCategoryRepository",
]
