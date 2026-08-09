"""
CDCS Enterprise Management Platform (CDCS-EMP)

Enterprise Application Execution Framework

Execution results.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional

from app.core.execution.exceptions import (
    ExecutionResultException,
)


@dataclass(slots=True)
class ExecutionResult:
    """
    Represents the result of an enterprise
    operation.
    """

    success: bool

    message: str = ""

    data: Any = None

    error_code: Optional[str] = None

    metadata: dict[str, Any] = field(
        default_factory=dict
    )

    def validate(self) -> None:
        """
        Validate the execution result.
        """

        if not isinstance(
            self.success,
            bool,
        ):
            raise ExecutionResultException(
                "Execution result 'success' "
                "must be a boolean."
            )

        if not isinstance(
            self.message,
            str,
        ):
            raise ExecutionResultException(
                "Execution result 'message' "
                "must be a string."
            )

        if self.error_code is not None:

            if not isinstance(
                self.error_code,
                str,
            ):

                raise ExecutionResultException(
                    "Execution result 'error_code' "
                    "must be a string or None."
                )

            if not self.error_code.strip():

                raise ExecutionResultException(
                    "Execution result 'error_code' "
                    "cannot be empty."
                )

        if not isinstance(
            self.metadata,
            dict,
        ):

            raise ExecutionResultException(
                "Execution result 'metadata' "
                "must be a dictionary."
            )

        if self.success and self.error_code:

            raise ExecutionResultException(
                "A successful execution result "
                "cannot contain an error code."
            )

    @classmethod
    def success_result(
        cls,
        data: Any = None,
        message: str = "",
        *,
        metadata: Optional[
            dict[str, Any]
        ] = None,
    ) -> "ExecutionResult":
        """
        Create a successful execution result.
        """

        result = cls(
            success=True,
            message=message,
            data=data,
            metadata=dict(
                metadata or {}
            ),
        )

        result.validate()

        return result

    @classmethod
    def failure_result(
        cls,
        message: str,
        *,
        error_code: Optional[str] = None,
        data: Any = None,
        metadata: Optional[
            dict[str, Any]
        ] = None,
    ) -> "ExecutionResult":
        """
        Create a failed execution result.
        """

        result = cls(
            success=False,
            message=message,
            data=data,
            error_code=error_code,
            metadata=dict(
                metadata or {}
            ),
        )

        result.validate()

        return result

    def is_success(self) -> bool:
        """
        Determine whether execution succeeded.
        """

        return self.success

    def is_failure(self) -> bool:
        """
        Determine whether execution failed.
        """

        return not self.success

    def with_metadata(
        self,
        **metadata: Any,
    ) -> "ExecutionResult":
        """
        Return a copy of the result with
        additional metadata.
        """

        combined = dict(
            self.metadata
        )

        combined.update(
            metadata
        )

        return ExecutionResult(
            success=self.success,
            message=self.message,
            data=self.data,
            error_code=self.error_code,
            metadata=combined,
        )


__all__ = [
    "ExecutionResult",
]
