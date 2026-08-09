"""
CDCS Enterprise Management Platform (CDCS-EMP)

Enterprise Application Execution Framework

Command dispatcher.
"""

from __future__ import annotations

from typing import Type

from app.core.execution.authorization import (
    AllowAllExecutionAuthorizer,
    ExecutionAuthorizer,
    validate_authorization_contract,
)

from app.core.execution.commands.base import (
    BaseCommand,
)

from app.core.execution.commands.registry import (
    CommandRegistry,
    command_registry,
)

from app.core.execution.context import (
    ExecutionContext,
)

from app.core.execution.contracts import (
    validate_execution_contract,
    validate_execution_result,
)

from app.core.execution.exceptions import (
    ExecutionContractException,
    HandlerContractException,
)

from app.core.execution.handlers.base import (
    BaseCommandHandler,
)

from app.core.execution.results import (
    ExecutionResult,
)


class CommandDispatcher:
    """
    Dispatches enterprise commands to their
    registered handlers.

    The dispatcher is responsible for orchestration
    only. Business logic remains inside handlers.

    Authorization is evaluated before the command
    handler is executed.
    """

    def __init__(
        self,
        registry: CommandRegistry | None = None,
        authorizer: ExecutionAuthorizer | None = None,
    ) -> None:
        """
        Initialize the command dispatcher.

        Parameters
        ----------
        registry:
            Optional command registry.

        authorizer:
            Optional execution authorizer.

            When no authorizer is supplied, the
            compatibility AllowAllExecutionAuthorizer
            is used. This preserves existing command
            execution behavior while allowing the
            enterprise security framework to be
            integrated in a later stage.
        """

        self.registry = (
            registry
            or command_registry
        )

        self.authorizer = (
            authorizer
            or AllowAllExecutionAuthorizer()
        )

        self._handlers: dict[
            Type[BaseCommand],
            BaseCommandHandler,
        ] = {}

    def register_handler(
        self,
        handler: BaseCommandHandler,
    ) -> BaseCommandHandler:
        """
        Register a command handler.

        The handler's command_type determines which
        command class it supports.
        """

        if not isinstance(
            handler,
            BaseCommandHandler,
        ):
            raise HandlerContractException(
                "Handler must inherit from "
                "BaseCommandHandler."
            )

        command_type = getattr(
            handler,
            "command_type",
            None,
        )

        if not isinstance(
            command_type,
            type,
        ):
            raise HandlerContractException(
                "Handler must define a valid "
                "'command_type'."
            )

        if not issubclass(
            command_type,
            BaseCommand,
        ):
            raise HandlerContractException(
                "Handler command_type must "
                "inherit from BaseCommand."
            )

        if command_type in self._handlers:
            raise HandlerContractException(
                f"A handler is already registered "
                f"for command "
                f"'{command_type.command_name}'."
            )

        self._handlers[
            command_type
        ] = handler

        return handler

    def unregister_handler(
        self,
        command_type: Type[BaseCommand],
    ) -> BaseCommandHandler:
        """
        Remove and return a registered handler.
        """

        try:
            return self._handlers.pop(
                command_type
            )

        except KeyError as exc:
            raise HandlerContractException(
                "No handler is registered for "
                "the supplied command type."
            ) from exc

    def get_handler(
        self,
        command_type: Type[BaseCommand],
    ) -> BaseCommandHandler:
        """
        Retrieve the handler registered for
        a command type.
        """

        try:
            return self._handlers[
                command_type
            ]

        except KeyError as exc:
            raise HandlerContractException(
                f"No handler is registered for "
                f"command "
                f"'{command_type.command_name}'."
            ) from exc

    def has_handler(
        self,
        command_type: Type[BaseCommand],
    ) -> bool:
        """
        Determine whether a handler exists for
        the supplied command type.
        """

        return (
            command_type
            in self._handlers
        )

    def handler_count(self) -> int:
        """
        Return the number of registered handlers.
        """

        return len(
            self._handlers
        )

    def clear_handlers(self) -> None:
        """
        Remove all registered handlers.
        """

        self._handlers.clear()

    def set_authorizer(
        self,
        authorizer: ExecutionAuthorizer,
    ) -> None:
        """
        Replace the execution authorizer.
        """

        if not isinstance(
            authorizer,
            ExecutionAuthorizer,
        ):
            raise ExecutionContractException(
                "Authorizer must implement "
                "ExecutionAuthorizer."
            )

        self.authorizer = authorizer

    def authorize(
        self,
        command: BaseCommand,
        context: ExecutionContext,
    ) -> None:
        """
        Authorize a command before execution.

        A denied authorization decision prevents
        the command handler from executing.
        """

        try:
            validate_authorization_contract(
                command,
                context,
                self.authorizer,
            )

            decision = self.authorizer.authorize(
                command,
                context,
            )

        except ExecutionContractException:
            raise

        except Exception as exc:
            raise ExecutionContractException(
                "Authorization evaluation failed."
            ) from exc

        if not decision.is_allowed():
            reason = (
                decision.reason
                or "Command execution was not authorized."
            )

            raise ExecutionContractException(
                reason
            )

    def dispatch(
        self,
        command: BaseCommand,
        context: ExecutionContext,
    ) -> ExecutionResult:
        """
        Dispatch a command for execution.
        """

        try:
            validate_execution_contract(
                command,
                context,
            )

        except Exception as exc:
            raise ExecutionContractException(
                "Invalid command execution "
                "contract."
            ) from exc

        command_type = type(
            command
        )

        if not self.registry.exists(
            command.command_name
        ):
            raise ExecutionContractException(
                f"Command "
                f"'{command.command_name}' "
                "is not registered."
            )

        registered_type = self.registry.get(
            command.command_name
        )

        if registered_type is not command_type:
            raise ExecutionContractException(
                f"Registered command type does "
                f"not match supplied command "
                f"'{command.command_name}'."
            )

        handler = self.get_handler(
            command_type
        )

        if not handler.supports(
            command
        ):
            raise HandlerContractException(
                f"Handler does not support "
                f"command "
                f"'{command.command_name}'."
            )

        # Authorization MUST occur before
        # the handler is invoked.
        self.authorize(
            command,
            context,
        )

        # Preserve the existing execution
        # context enrichment pipeline.
        enriched_context = context.with_metadata(
            command=command.command_name,
            handler=handler.__class__.__name__,
        )

        result = handler.handle(
            command,
            enriched_context,
        )

        try:
            validate_execution_result(
                result
            )

        except Exception as exc:
            raise HandlerContractException(
                "Command handler returned "
                "an invalid execution result."
            ) from exc

        return result


__all__ = [
    "CommandDispatcher",
]
