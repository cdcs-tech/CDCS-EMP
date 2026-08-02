"""
CDCS Enterprise Management Platform (CDCS-EMP)

Application Startup Package

Provides the public interface for application
startup and initialization services.
"""

from app.core.startup.modules import (
    initialize_modules,
)

__all__ = [
    "initialize_modules",
]
