"""
CDCS Enterprise Management Platform (CDCS-EMP)

Enterprise Data Framework

Public interface for reusable enterprise
data abstractions.
"""

from app.core.data.entity import (
    BaseEntity,
)

from app.core.data.repository import (
    BaseRepository,
)

from app.core.data.service import (
    BaseService,
)

__all__ = [
    "BaseEntity",
    "BaseRepository",
    "BaseService",
]
