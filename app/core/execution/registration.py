from __future__ import annotations

from dataclasses import dataclass
from typing import Type

from app.core.execution.commands.base import BaseCommand
from app.core.execution.handlers.base import BaseCommandHandler


@dataclass(frozen=True, slots=True)
class ExecutionDefinition:
    """Definition of a command and its handler for module registration."""

    command: Type[BaseCommand]
    handler: BaseCommandHandler


def validate_execution_definition(
    definition: ExecutionDefinition,
) -> None:
    """Validate an execution registration definition."""

    if not isinstance(
        definition,
        ExecutionDefinition,
    ):
        raise TypeError(
            "Execution definition must be an ExecutionDefinition."
        )

    command = definition.command
    handler = definition.handler

    if not isinstance(
        command,
        type,
    ) or not issubclass(
        command,
        BaseCommand,
    ):
        raise TypeError(
            "Execution definition command must be a BaseCommand subclass."
        )

    if not isinstance(
        handler,
        BaseCommandHandler,
    ):
        raise TypeError(
            "Execution definition handler must be a BaseCommandHandler instance."
        )

    if handler.command_type is not command:
        raise TypeError(
            "Execution definition handler command_type must match the command."
        )

    if not isinstance(
        command.command_name,
        str,
    ) or not command.command_name:
        raise TypeError(
            "Execution definition command must define a command_name."
        )

    execute_name = getattr(
        command,
        "execute_name",
        None,
    )

    if not callable(
        execute_name,
    ):
        raise TypeError(
            "Execution definition command must implement execute_name()."
        )
