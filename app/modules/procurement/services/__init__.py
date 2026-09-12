"""
CDCS Enterprise Management Platform (CDCS-EMP)

Procurement Services

Module-local application services.
"""

from .purchase_requirement import PurchaseRequirementService
from .supplier import SupplierService


__all__ = [
    "SupplierService",
    "PurchaseRequirementService",
]
