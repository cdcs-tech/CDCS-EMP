"""
CDCS Enterprise Management Platform (CDCS-EMP)

Enterprise Configuration Framework

Configuration providers.
"""

from app.core.configuration.providers.memory import (
    MemoryConfigurationProvider,
)


__all__ = [
    "MemoryConfigurationProvider",
]
