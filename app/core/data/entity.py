"""
CDCS Enterprise Management Platform (CDCS-EMP)

Enterprise Data Framework

Base entity abstraction.
"""

from __future__ import annotations

from abc import ABC
from dataclasses import dataclass, field
from typing import Any, Dict


@dataclass
class BaseEntity(ABC):
    """
    Base abstraction for enterprise entities.

    This class is intentionally independent of
    SQLAlchemy and other persistence frameworks.
    """

    id: Any = None

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

    def is_persisted(self) -> bool:
        """
        Determine whether the entity has been
        persisted.

        Returns:
            True if an identifier exists.
        """

        return self.id is not None

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the entity into a dictionary.

        Returns:
            Dictionary representation of the entity.
        """

        return {
            "id": self.id,
            "metadata": dict(self.metadata),
        }

    @classmethod
    def from_dict(
        cls,
        values: Dict[str, Any],
    ) -> "BaseEntity":
        """
        Create an entity instance from a dictionary.
        """

        return cls(
            id=values.get("id"),
            metadata=dict(
                values.get("metadata", {})
            ),
        )
