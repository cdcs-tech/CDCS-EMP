"""
CDCS Enterprise Management Platform (CDCS-EMP)

Enterprise Application Execution Framework

Command validation utilities.
"""

from app.core.execution.commands.base import (
    BaseCommand,
)

from app.core.execution.commands.metadata import (
    CommandMetadata,
)

from app.core.execution.exceptions import (
    CommandValidationException,
)


def validate_command(
    command: BaseCommand,
) -> None:
    """
    Validate a command against the base
    command contract.
    """

    if not isinstance(
        command,
        BaseCommand,
    ):
        raise CommandValidationException(
            "Object must be a BaseCommand."
        )

    command.validate()


def validate_command_metadata(
    metadata: CommandMetadata,
) -> None:
    """
    Validate command metadata.
    """

    if not isinstance(
        metadata,
        CommandMetadata,
    ):
        raise CommandValidationException(
            "Metadata must be a CommandMetadata."
        )

    if not metadata.name.strip():
        raise CommandValidationException(
            "Command metadata requires a name."
        )

    if not metadata.module_name.strip():
        raise CommandValidationException(
            "Command metadata requires "
            "a module name."
        )

    if not metadata.operation.strip():
        raise CommandValidationException(
            "Command metadata requires "
            "an operation."
        )

    if not metadata.version.strip():
        raise CommandValidationException(
            "Command metadata requires "
            "a version."
        )


__all__ = [
    "validate_command",
    "validate_command_metadata",
]
