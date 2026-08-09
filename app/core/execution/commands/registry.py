"""
CDCS Enterprise Management Platform (CDCS-EMP)

Enterprise Application Execution Framework

Command registry.
"""

from __future__ import annotations

from threading import RLock
from typing import Type

from app.core.execution.commands.base import (
    BaseCommand,
)

from app.core.execution.commands.validation import (
    validate_command,
)

from app.core.execution.exceptions import (
    CommandValidationException,
)


class CommandRegistry:
    """
    Central registry for enterprise command types.

    The registry is responsible for:

    - registering command classes;
    - discovering registered commands;
    - retrieving commands by name;
    - preventing duplicate registrations;
    - unregistering commands;
    - clearing registered commands.

    The registry does not execute commands.
    """

    def __init__(self) -> None:
        self._commands: dict[
            str,
            Type[BaseCommand],
        ] = {}

        self._lock = RLock()

    def register(
        self,
        command_type: Type[BaseCommand],
    ) -> Type[BaseCommand]:
        """
        Register a command class.

        Returns the supplied command class so that
        registration can also be used as a decorator.
        """

        if not isinstance(
            command_type,
            type,
        ):

            raise CommandValidationException(
                "Command registration requires "
                "a command class."
            )

        if not issubclass(
            command_type,
            BaseCommand,
        ):

            raise CommandValidationException(
                "Registered command must inherit "
                "from BaseCommand."
            )

        command_name = (
            command_type.command_name
        )

        if not command_name:

            raise CommandValidationException(
                "Registered command must define "
                "'command_name'."
            )

        with self._lock:

            if command_name in self._commands:

                raise CommandValidationException(
                    f"Command '{command_name}' "
                    "is already registered."
                )

            self._commands[
                command_name
            ] = command_type

        return command_type

    def get(
        self,
        command_name: str,
    ) -> Type[BaseCommand]:
        """
        Retrieve a registered command class.
        """

        if not command_name:

            raise CommandValidationException(
                "Command name is required."
            )

        with self._lock:

            try:

                return self._commands[
                    command_name
                ]

            except KeyError as exc:

                raise CommandValidationException(
                    f"Command '{command_name}' "
                    "is not registered."
                ) from exc

    def exists(
        self,
        command_name: str,
    ) -> bool:
        """
        Determine whether a command is registered.
        """

        if not command_name:
            return False

        with self._lock:

            return (
                command_name
                in self._commands
            )

    def unregister(
        self,
        command_name: str,
    ) -> Type[BaseCommand]:
        """
        Remove and return a registered command.
        """

        if not command_name:

            raise CommandValidationException(
                "Command name is required."
            )

        with self._lock:

            try:

                return self._commands.pop(
                    command_name
                )

            except KeyError as exc:

                raise CommandValidationException(
                    f"Command '{command_name}' "
                    "is not registered."
                ) from exc

    def clear(self) -> None:
        """
        Remove all registered commands.
        """

        with self._lock:
            self._commands.clear()

    def count(self) -> int:
        """
        Return the number of registered commands.
        """

        with self._lock:
            return len(
                self._commands
            )

    def names(self) -> tuple[str, ...]:
        """
        Return registered command names.
        """

        with self._lock:

            return tuple(
                self._commands.keys()
            )

    def all(
        self,
    ) -> dict[
        str,
        Type[BaseCommand],
    ]:
        """
        Return a snapshot of all registered commands.
        """

        with self._lock:

            return dict(
                self._commands
            )

    def validate(
        self,
    ) -> None:
        """
        Validate all registered command classes.

        Validation is performed against the base
        command contract without executing commands.
        """

        with self._lock:

            commands = tuple(
                self._commands.values()
            )

        for command_type in commands:

            try:

                command = command_type.__new__(
                    command_type
                )

                validate_command(
                    command
                )

            except Exception as exc:

                raise CommandValidationException(
                    f"Invalid registered command "
                    f"'{command_type.command_name}'."
                ) from exc


# Shared application-level registry.
command_registry = CommandRegistry()


__all__ = [
    "CommandRegistry",
    "command_registry",
]
