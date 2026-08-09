"""
CDCS Enterprise Management Platform (CDCS-EMP)

Enterprise Application Execution Framework

Command package.
"""

from app.core.execution.commands.base import (
    BaseCommand,
)

from app.core.execution.commands.metadata import (
    CommandMetadata,
)

from app.core.execution.commands.types import (
    CommandType,
)

from app.core.execution.commands.validation import (
    validate_command,
    validate_command_metadata,
)

from app.core.execution.commands.registry import (
    CommandRegistry,
    command_registry,
)

__all__ = [
    "BaseCommand",
    "CommandMetadata",
    "CommandType",
    "validate_command",
    "validate_command_metadata",
    "CommandRegistry",
    "command_registry",
]
