"""
CDCS Enterprise Management Platform (CDCS-EMP)

Procurement Module

HTTP routes.
"""

from app.modules.procurement.routes.routes import (
    procurement_bp,
)

__all__ = [
    "procurement_bp",
]
