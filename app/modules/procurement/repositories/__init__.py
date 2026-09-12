"""
CDCS Enterprise Management Platform (CDCS-EMP)

Procurement Repositories

Module-local persistence repositories.
"""

from .purchase_requirement import PurchaseRequirementRepository
from .supplier import SupplierRepository


__all__ = [
    "SupplierRepository",
    "PurchaseRequirementRepository",
]
