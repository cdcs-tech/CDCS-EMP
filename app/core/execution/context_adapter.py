"""
CDCS Enterprise Management Platform (CDCS-EMP)

Enterprise Application Execution Framework

Execution context integration utilities.
"""

from __future__ import annotations

from typing import Any

from app.core.execution.context import (
    ExecutionContext,
)

from app.core.execution.exceptions import (
    ExecutionContractException,
)


class ExecutionContextAdapter:
    """
    Provides standardized context enrichment and
    validation for the execution framework.

    The adapter never mutates an existing
    ExecutionContext. All enrichment operations
    return a new context instance.
    """

    @staticmethod
    def validate(
        context: ExecutionContext,
    ) -> None:
        """
        Validate an execution context.
        """

        if not isinstance(
            context,
            ExecutionContext,
        ):

            raise ExecutionContractException(
                "Execution context must be an "
                "ExecutionContext instance."
            )

        context.validate()

    @staticmethod
    def enrich(
        context: ExecutionContext,
        **metadata: Any,
    ) -> ExecutionContext:
        """
        Return a new context containing the
        supplied metadata.
        """

        ExecutionContextAdapter.validate(
            context
        )

        return context.with_metadata(
            **metadata
        )

    @staticmethod
    def for_use_case(
        context: ExecutionContext,
        use_case_name: str,
    ) -> ExecutionContext:
        """
        Add use-case identity to the execution
        context.
        """

        if not use_case_name:
            raise ExecutionContractException(
                "Use-case name is required."
            )

        return ExecutionContextAdapter.enrich(
            context,
            use_case=use_case_name,
        )

    @staticmethod
    def for_command(
        context: ExecutionContext,
        command_name: str,
    ) -> ExecutionContext:
        """
        Add command identity to the execution
        context.
        """

        if not command_name:
            raise ExecutionContractException(
                "Command name is required."
            )

        return ExecutionContextAdapter.enrich(
            context,
            command=command_name,
        )

    @staticmethod
    def for_handler(
        context: ExecutionContext,
        handler_name: str,
    ) -> ExecutionContext:
        """
        Add handler identity to the execution
        context.
        """

        if not handler_name:
            raise ExecutionContractException(
                "Handler name is required."
            )

        return ExecutionContextAdapter.enrich(
            context,
            handler=handler_name,
        )


__all__ = [
    "ExecutionContextAdapter",
]
