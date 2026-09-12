"""
CDCS Enterprise Management Platform (CDCS-EMP)

Procurement Forms

Module-local input and validation forms.
"""

from .purchase_requirement import PurchaseRequirementForm
from .supplier import SupplierForm


__all__ = [
    "SupplierForm",
    "PurchaseRequirementForm",
]
