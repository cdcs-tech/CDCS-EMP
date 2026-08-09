"""
CDCS Enterprise Management Platform (CDCS-EMP)

Enterprise Application Execution Framework

Command metadata.
"""

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True, frozen=True)
class CommandMetadata:
    """
    Describes an enterprise command.
    """

    name: str

    module_name: str

    operation: str

    version: str = "1.0"

    description: str = ""

    category: str = "general"

    metadata: dict[str, Any] = field(
        default_factory=dict
    )

    def qualified_name(self) -> str:
        """
        Return the fully qualified command name.
        """

        return (
            f"{self.module_name}."
            f"{self.operation}"
        )


__all__ = [
    "CommandMetadata",
]
