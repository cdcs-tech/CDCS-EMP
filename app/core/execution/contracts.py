"""
CDCS Enterprise Management Platform (CDCS-EMP)

Enterprise Application Execution Framework

Execution contracts.
"""

from app.core.execution.context import (
    ExecutionContext,
)

from app.core.execution.results import (
    ExecutionResult,
)

from app.core.execution.commands.base import (
    BaseCommand,
)

from app.core.execution.handlers.base import (
    BaseCommandHandler,
)


def validate_execution_contract(
    command: BaseCommand,
    context: ExecutionContext,
) -> None:
    """
    Validate the basic execution contract.
    """

    if not isinstance(
        command,
        BaseCommand,
    ):
        raise TypeError(
            "command must be a BaseCommand."
        )

    if not isinstance(
        context,
        ExecutionContext,
    ):
        raise TypeError(
            "context must be an "
            "ExecutionContext."
        )

    command.validate()
    context.validate()


def validate_execution_result(
    result: ExecutionResult,
) -> None:
    """
    Validate an execution result.
    """

    if not isinstance(
        result,
        ExecutionResult,
    ):
        raise TypeError(
            "result must be an "
            "ExecutionResult."
        )

    result.validate()


def normalize_execution_result(
    result: ExecutionResult,
) -> ExecutionResult:
    """
    Validate and return a standardized
    execution result.
    """

    validate_execution_result(
        result
    )

    return result


def enrich_execution_result(
    result: ExecutionResult,
    **metadata,
) -> ExecutionResult:
    """
    Return an execution result enriched with
    additional metadata.
    """

    validate_execution_result(
        result
    )

    enriched = result.with_metadata(
        **metadata
    )

    enriched.validate()

    return enriched


__all__ = [
    "ExecutionContext",
    "ExecutionResult",
    "BaseCommand",
    "BaseCommandHandler",
    "validate_execution_contract",
    "validate_execution_result",
    "normalize_execution_result",
    "enrich_execution_result",
]
