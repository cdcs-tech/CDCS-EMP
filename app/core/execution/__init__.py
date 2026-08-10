"""
CDCS Enterprise Management Platform (CDCS-EMP)

Enterprise Application Execution Framework

Public package interface.
"""

from app.core.execution.context import (
    ExecutionContext,
)

from app.core.execution.exceptions import (
    ExecutionException,
    ExecutionContractException,
    ExecutionContextException,
    ExecutionResultException,
    CommandException,
    CommandValidationException,
    HandlerException,
    HandlerContractException,
)

from app.core.execution.results import (
    ExecutionResult,
)

from app.core.execution.commands import (
    BaseCommand,
    CommandMetadata,
    CommandType,
    validate_command,
    validate_command_metadata,
    CommandRegistry,
    command_registry,
)

from app.core.execution.handlers import (
    BaseCommandHandler,
)

from app.core.execution.contracts import (
    validate_execution_contract,
    validate_execution_result,
    normalize_execution_result,
    enrich_execution_result,
)

from app.core.execution.dispatcher import (
    CommandDispatcher,
)

from app.core.execution.use_cases import (
    BaseUseCase,
    UseCaseExecutor,
)

from app.core.execution.context_adapter import (
    ExecutionContextAdapter,
)

from app.core.execution.authorization import (
    AuthorizationDecision,
    ExecutionAuthorizer,
    AllowAllExecutionAuthorizer,
    RoleAssignmentExecutionAuthorizer,
    validate_authorization_contract,
)

from app.core.execution.authorization_service import (
    ExecutionAuthorizationService,
)

from app.core.execution.authorization_audit import (
    AuthorizationAuditContract,
)

from app.core.execution.authorization_result import (
    AuthorizationResultGovernance,
)

from app.core.execution.governance import (
    ExecutionGovernance,
)

from app.core.execution.authorization_enforcement import (
    GovernanceAwareAuthorizationEnforcement,
)


__all__ = [
    "ExecutionContext",
    "ExecutionResult",
    "BaseCommand",
    "BaseCommandHandler",

    "ExecutionException",
    "ExecutionContractException",
    "ExecutionContextException",
    "ExecutionResultException",

    "CommandException",
    "CommandValidationException",

    "HandlerException",
    "HandlerContractException",

    "validate_execution_contract",
    "validate_execution_result",
    "normalize_execution_result",
    "enrich_execution_result",

    "CommandMetadata",
    "CommandType",
    "validate_command",
    "validate_command_metadata",

    "CommandRegistry",
    "command_registry",

    "CommandDispatcher",

    "BaseUseCase",
    "UseCaseExecutor",

    "ExecutionContextAdapter",

    "AuthorizationDecision",
    "ExecutionAuthorizer",
    "AllowAllExecutionAuthorizer",
    "RoleAssignmentExecutionAuthorizer",
    "validate_authorization_contract",

    "ExecutionAuthorizationService",
    "AuthorizationAuditContract",
    "AuthorizationResultGovernance",
    "ExecutionGovernance",
    "GovernanceAwareAuthorizationEnforcement",
]
