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

from app.core.execution.authorization_enforcement import (
    GovernanceAwareAuthorizationEnforcement,
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

from app.core.execution.event_emitter import (
    ExecutionEventEmitter,
)

from app.core.execution.events import (
    ExecutionEvent,
    ExecutionEventType,
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

from app.core.execution.transaction import (
    ExecutionTransactionBoundary,
)


class CommandDispatcher:
    """
    Dispatches enterprise commands to their
    registered handlers.

    The dispatcher is responsible for orchestration
    only. Business logic remains inside handlers.

    Authorization is evaluated before the command
    handler is executed.

    When a transaction boundary is configured,
    transaction lifecycle is controlled by the
    dispatcher.

    When an event emitter is configured, execution
    lifecycle events are emitted without allowing
    emitter failures to interfere with command
    execution semantics.
    """

    def __init__(
        self,
        registry: CommandRegistry | None = None,
        authorizer: ExecutionAuthorizer | None = None,
        authorization_enforcement: (
            GovernanceAwareAuthorizationEnforcement
            | None
        ) = None,
        transaction_boundary: (
            ExecutionTransactionBoundary
            | None
        ) = None,
        event_emitter: (
            ExecutionEventEmitter
            | None
        ) = None,
    ) -> None:
        """
        Initialize the command dispatcher.
        """

        self.registry = (
            registry
            or command_registry
        )

        self.authorizer = (
            authorizer
            or AllowAllExecutionAuthorizer()
        )

        self.authorization_enforcement = (
            authorization_enforcement
        )

        if (
            transaction_boundary is not None
            and not isinstance(
                transaction_boundary,
                ExecutionTransactionBoundary,
            )
        ):
            raise ExecutionContractException(
                "Transaction boundary must "
                "implement "
                "ExecutionTransactionBoundary."
            )

        self.transaction_boundary = (
            transaction_boundary
        )

        if (
            event_emitter is not None
            and not isinstance(
                event_emitter,
                ExecutionEventEmitter,
            )
        ):
            raise ExecutionContractException(
                "Event emitter must implement "
                "ExecutionEventEmitter."
            )

        self.event_emitter = (
            event_emitter
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

    def set_authorization_enforcement(
        self,
        enforcement: (
            GovernanceAwareAuthorizationEnforcement
            | None
        ),
    ) -> None:
        """
        Configure the optional governance-aware
        authorization enforcement boundary.
        """

        if (
            enforcement is not None
            and not isinstance(
                enforcement,
                GovernanceAwareAuthorizationEnforcement,
            )
        ):
            raise ExecutionContractException(
                "Authorization enforcement must "
                "implement "
                "GovernanceAwareAuthorizationEnforcement."
            )

        self.authorization_enforcement = (
            enforcement
        )

    def set_transaction_boundary(
        self,
        transaction_boundary: (
            ExecutionTransactionBoundary
            | None
        ),
    ) -> None:
        """
        Configure the optional execution
        transaction boundary.

        Passing None disables transaction-aware
        command execution.
        """

        if (
            transaction_boundary is not None
            and not isinstance(
                transaction_boundary,
                ExecutionTransactionBoundary,
            )
        ):
            raise ExecutionContractException(
                "Transaction boundary must "
                "implement "
                "ExecutionTransactionBoundary."
            )

        self.transaction_boundary = (
            transaction_boundary
        )

    def set_event_emitter(
        self,
        event_emitter: (
            ExecutionEventEmitter
            | None
        ),
    ) -> None:
        """
        Configure the optional execution
        event emitter.

        Passing None disables execution event
        emission.
        """

        if (
            event_emitter is not None
            and not isinstance(
                event_emitter,
                ExecutionEventEmitter,
            )
        ):
            raise ExecutionContractException(
                "Event emitter must implement "
                "ExecutionEventEmitter."
            )

        self.event_emitter = (
            event_emitter
        )

    def _emit_event(
        self,
        event: ExecutionEvent,
    ) -> None:
        """
        Emit an execution event when an emitter
        is configured.

        Event-emitter failures are intentionally
        isolated from command execution.
        """

        if self.event_emitter is None:
            return

        try:
            self.event_emitter.emit(
                event
            )

        except Exception:
            # Event emission is observability
            # infrastructure and must not alter
            # command execution semantics.
            return

    def _build_event(
        self,
        event_type: ExecutionEventType,
        command: BaseCommand,
        context: ExecutionContext,
        outcome: str,
        **metadata,
    ) -> ExecutionEvent:
        """
        Build an execution lifecycle event.

        All dispatcher-generated events identify
        the dispatcher as their source.
        """

        event_metadata = {
            "source": "dispatcher",
        }

        event_metadata.update(
            metadata
        )

        return ExecutionEvent(
            event_type=event_type,
            command_name=command.command_name,
            context=context,
            outcome=outcome,
            metadata=event_metadata,
        )

    def _emit_started_event(
        self,
        command: BaseCommand,
        context: ExecutionContext,
    ) -> None:
        """
        Emit the execution-started event.
        """

        self._emit_event(
            self._build_event(
                ExecutionEventType.STARTED,
                command,
                context,
                "success",
            )
        )

    def _emit_completed_event(
        self,
        command: BaseCommand,
        context: ExecutionContext,
        result: ExecutionResult,
    ) -> None:
        """
        Emit the execution-completed event.
        """

        self._emit_event(
            self._build_event(
                ExecutionEventType.COMPLETED,
                command,
                context,
                "success",
                error_code=result.error_code,
            )
        )

    def _emit_failed_event(
        self,
        command: BaseCommand,
        context: ExecutionContext,
        result: ExecutionResult | None = None,
    ) -> None:
        """
        Emit the execution-failed event.
        """

        metadata = {}

        if result is not None:
            metadata["error_code"] = (
                result.error_code
            )

        self._emit_event(
            self._build_event(
                ExecutionEventType.FAILED,
                command,
                context,
                "failure",
                **metadata,
            )
        )

    def _emit_denied_event(
        self,
        command: BaseCommand,
        context: ExecutionContext,
    ) -> None:
        """
        Emit the execution-denied event.
        """

        self._emit_event(
            self._build_event(
                ExecutionEventType.DENIED,
                command,
                context,
                "denied",
            )
        )

    def authorize(
        self,
        command: BaseCommand,
        context: ExecutionContext,
    ) -> None:
        """
        Authorize a command before execution.
        """

        if (
            self.authorization_enforcement
            is not None
        ):
            try:
                decision = (
                    self.authorization_enforcement.authorize(
                        command,
                        context,
                    )
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
                    or (
                        "Command execution was "
                        "not authorized."
                    )
                )

                self._emit_denied_event(
                    command,
                    context,
                )

                raise ExecutionContractException(
                    reason
                )

            return

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
                or (
                    "Command execution was "
                    "not authorized."
                )
            )

            self._emit_denied_event(
                command,
                context,
            )

            raise ExecutionContractException(
                reason
            )

    def _execute_handler(
        self,
        command: BaseCommand,
        context: ExecutionContext,
        handler: BaseCommandHandler,
    ) -> ExecutionResult:
        """
        Execute a command handler and validate
        the returned execution result.
        """

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

    def _execute_transactionally(
        self,
        command: BaseCommand,
        context: ExecutionContext,
        handler: BaseCommandHandler,
    ) -> ExecutionResult:
        """
        Execute a command inside the configured
        transaction boundary.
        """

        transaction = self.transaction_boundary

        if transaction is None:
            try:
                result = self._execute_handler(
                    command,
                    context,
                    handler,
                )

            except Exception:
                self._emit_failed_event(
                    command,
                    context,
                )
                raise

            if result.is_success():
                self._emit_completed_event(
                    command,
                    context,
                    result,
                )

            else:
                self._emit_failed_event(
                    command,
                    context,
                    result,
                )

            return result

        transaction.begin()

        try:
            result = self._execute_handler(
                command,
                context,
                handler,
            )

            if result.is_success():
                transaction.commit()

                self._emit_completed_event(
                    command,
                    context,
                    result,
                )

            else:
                transaction.rollback()

                self._emit_failed_event(
                    command,
                    context,
                    result,
                )

            return result

        except Exception:
            try:
                transaction.rollback()

            except Exception:
                # Preserve the original execution
                # exception. Transaction rollback
                # failure must not mask it.
                pass

            self._emit_failed_event(
                command,
                context,
            )

            raise

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

        # Establish the execution as RUNNING
        # before authorization is evaluated.
        #
        # This permits authorization denial to
        # follow the governed lifecycle:
        #
        #     STARTED -> DENIED
        #
        # Authorization still occurs before any
        # transaction is started or handler is
        # executed.
        self._emit_started_event(
            command,
            context,
        )

        self.authorize(
            command,
            context,
        )

        return self._execute_transactionally(
            command,
            context,
            handler,
        )
