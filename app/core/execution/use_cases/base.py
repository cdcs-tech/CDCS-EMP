"""
CDCS Enterprise Management Platform (CDCS-EMP)

Enterprise Application Execution Framework

Base use-case contract.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from app.core.execution.commands.base import (
    BaseCommand,
)

from app.core.execution.context import (
    ExecutionContext,
)

from app.core.execution.context_adapter import (
    ExecutionContextAdapter,
)

from app.core.execution.exceptions import (
    ExecutionContractException,
)


class BaseUseCase(ABC):
    """
    Base contract for enterprise application
    use cases.

    A use case represents one application-level
    business operation.

    The use case is responsible for preparing the
    command and delegating execution to the command
    dispatcher.
    """

    use_case_name: str = ""

    command_type: type[
        BaseCommand
    ]

    def validate(self) -> None:
        """
        Validate the use-case contract.
        """

        if not self.use_case_name:

            raise ExecutionContractException(
                "Use case must define "
                "'use_case_name'."
            )

        command_type = getattr(
            self,
            "command_type",
            None,
        )

        if not isinstance(
            command_type,
            type,
        ):

            raise ExecutionContractException(
                "Use case must define a valid "
                "'command_type'."
            )

        if not issubclass(
            command_type,
            BaseCommand,
        ):

            raise ExecutionContractException(
                "Use case command_type must "
                "inherit from BaseCommand."
            )

    @abstractmethod
    def build_command(
        self,
        **kwargs: Any,
    ) -> BaseCommand:
        """
        Build the command represented by
        this use case.
        """

        raise NotImplementedError

    def prepare_context(
        self,
        context: ExecutionContext,
    ) -> ExecutionContext:
        """
        Prepare the execution context.

        The default implementation adds the
        current use-case identity.
        """

        ExecutionContextAdapter.validate(
            context
        )

        return (
            ExecutionContextAdapter.for_use_case(
                context,
                self.use_case_name,
            )
        )

    def execute(
        self,
        executor: "UseCaseExecutor",
        context: ExecutionContext,
        **kwargs: Any,
    ):
        """
        Execute the use case through the supplied
        use-case executor.
        """

        self.validate()

        prepared_context = (
            self.prepare_context(
                context
            )
        )

        command = self.build_command(
            **kwargs
        )

        if not isinstance(
            command,
            BaseCommand,
        ):

            raise ExecutionContractException(
                "Use case must build a "
                "BaseCommand."
            )

        if not isinstance(
            command,
            self.command_type,
        ):

            raise ExecutionContractException(
                "Use case built a command that "
                "does not match its command_type."
            )

        return executor.execute(
            command,
            prepared_context,
        )


__all__ = [
    "BaseUseCase",
]
