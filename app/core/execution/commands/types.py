"""
CDCS Enterprise Management Platform (CDCS-EMP)

Enterprise Application Execution Framework

Command type definitions.
"""

from enum import StrEnum


class CommandType(StrEnum):
    """
    Standard enterprise command categories.
    """

    CREATE = "create"

    READ = "read"

    UPDATE = "update"

    DELETE = "delete"

    EXECUTE = "execute"


__all__ = [
    "CommandType",
]
