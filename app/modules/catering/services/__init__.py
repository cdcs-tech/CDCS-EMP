"""
CDCS Enterprise Management Platform (CDCS-EMP)

Catering Services

Module-local application services.
"""

from .product import ProductService
from .product_category import ProductCategoryService

__all__ = [
    "ProductService",
    "ProductCategoryService",
]
