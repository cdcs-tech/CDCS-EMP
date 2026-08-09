"""
CDCS Enterprise Management Platform (CDCS-EMP)

Enterprise Application Execution Framework

Base command contract.
"""

from abc import ABC, abstractmethod
from typing import Any, Optional

from app.core.execution.commands.metadata import (
    CommandMetadata,
)

from app.core.execution.commands.types import (
    CommandType,
)

from app.core.execution.exceptions import (
    CommandValidationException,
)


class BaseCommand(ABC):
    """
    Base command contract.

    Concrete commands should represent one
    enterprise operation.
    """

    command_name: str = ""

    command_type: CommandType = (
        CommandType.EXECUTE
    )

    metadata: Optional[
        CommandMetadata
    ] = None

    def validate(self) -> None:
        """
        Validate the command.

        Concrete commands may override this method
        but should call super().validate().
        """

        if not self.command_name:
            raise CommandValidationException(
                "Command must define "
                "'command_name'."
            )

        if not isinstance(
            self.command_type,
            CommandType,
        ):
            raise CommandValidationException(
                "Command must define a valid "
                "'command_type'."
            )

        if self.metadata is not None:

            if not isinstance(
                self.metadata,
                CommandMetadata,
            ):
                raise CommandValidationException(
                    "Command metadata must be "
                    "a CommandMetadata instance."
                )

    def payload(self) -> dict[str, Any]:
        """
        Return the command payload.
        """

        return dict(
            self.__dict__
        )

    def command_metadata(
        self,
    ) -> Optional[CommandMetadata]:
        """
        Return command metadata.
        """

        return self.metadata

    def qualified_name(self) -> str:
        """
        Return the qualified command name.

        If metadata is available, its qualified
        name is used. Otherwise the command name
        is returned.
        """

        if self.metadata is not None:
            return (
                self.metadata.qualified_name()
            )

        return self.command_name

    @abstractmethod
    def execute_name(self) -> str:
        """
        Return the operation name represented
        by this command.
        """

        raise NotImplementedError


__all__ = [
    "BaseCommand",
]
