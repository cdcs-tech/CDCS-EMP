"""
CDCS Enterprise Management Platform (CDCS-EMP)

Enterprise Application Execution Framework

Use-case executor.
"""

from __future__ import annotations

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

from app.core.execution.dispatcher import (
    CommandDispatcher,
)

from app.core.execution.exceptions import (
    ExecutionContractException,
)

from app.core.execution.results import (
    ExecutionResult,
)


class UseCaseExecutor:
    """
    Executes application use cases through the
    command execution infrastructure.

    The executor provides the application-level
    bridge between a use case and the command
    dispatcher.
    """

    def __init__(
        self,
        dispatcher: CommandDispatcher | None = None,
    ) -> None:

        self.dispatcher = (
            dispatcher
            or CommandDispatcher()
        )

    def execute(
        self,
        command: BaseCommand,
        context: ExecutionContext,
    ) -> ExecutionResult:
        """
        Execute a command through the command
        dispatcher.

        The command identity is added to a new
        execution context before dispatch.
        """

        if not isinstance(
            command,
            BaseCommand,
        ):

            raise ExecutionContractException(
                "Use-case execution requires "
                "a BaseCommand."
            )

        ExecutionContextAdapter.validate(
            context
        )

        prepared_context = (
            ExecutionContextAdapter.for_command(
                context,
                command.command_name,
            )
        )

        return self.dispatcher.dispatch(
            command,
            prepared_context,
        )

    def execute_use_case(
        self,
        use_case: Any,
        context: ExecutionContext,
        **kwargs: Any,
    ) -> ExecutionResult:
        """
        Execute a BaseUseCase instance.
        """

        from app.core.execution.use_cases.base import (
            BaseUseCase,
        )

        if not isinstance(
            use_case,
            BaseUseCase,
        ):

            raise ExecutionContractException(
                "Object must be a BaseUseCase."
            )

        ExecutionContextAdapter.validate(
            context
        )

        return use_case.execute(
            self,
            context,
            **kwargs,
        )


__all__ = [
    "UseCaseExecutor",
]
