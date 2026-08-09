"""
CDCS Enterprise Management Platform (CDCS-EMP)

Enterprise Application Execution Framework

Base command handler contract.
"""

from abc import ABC, abstractmethod

from app.core.execution.context import (
    ExecutionContext,
)

from app.core.execution.results import (
    ExecutionResult,
)

from app.core.execution.commands.base import (
    BaseCommand,
)


class BaseCommandHandler(ABC):
    """
    Base handler contract for enterprise commands.
    """

    command_type: type[
        BaseCommand
    ]

    @abstractmethod
    def handle(
        self,
        command: BaseCommand,
        context: ExecutionContext,
    ) -> ExecutionResult:
        """
        Execute a command.
        """

        raise NotImplementedError

    def supports(
        self,
        command: BaseCommand,
    ) -> bool:
        """
        Determine whether this handler supports
        the supplied command.
        """

        return isinstance(
            command,
            self.command_type,
        )


__all__ = [
    "BaseCommandHandler",
]
