"""
CDCS Enterprise Management Platform (CDCS-EMP)

Enterprise Startup Framework

Public interface for application startup services.
"""

from app.core.startup.modules import (
    initialize_modules,
)

__all__ = [
    "initialize_modules",
]
