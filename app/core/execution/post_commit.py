"""
CDCS Enterprise Management Platform (CDCS-EMP)

Enterprise Application Execution Framework

Post-commit execution capability.
"""

from abc import ABC, abstractmethod
from typing import Any


class PostCommitAction(ABC):
    """
    Contract for an action that executes after a
    successful transaction commit.
    """

    @abstractmethod
    def execute(
        self,
        command: Any,
        context: Any,
        result: Any,
    ) -> None:
        """
        Execute the post-commit action.

        The action receives the originating command,
        execution context, and successful execution
        result.

        Implementations must not assume ownership of
        the originating transaction.
        """
        raise NotImplementedError


class PostCommitExecutor:
    """
    Execute post-commit actions independently of the
    originating transaction lifecycle.

    Post-commit action failures are isolated so that an
    already-committed transaction cannot be rolled back
    or converted into a command failure.
    """

    def execute(
        self,
        action: PostCommitAction,
        command: Any,
        context: Any,
        result: Any,
    ) -> None:
        """
        Execute a post-commit action.

        Runtime failures raised by the action are isolated
        from the committed transaction.
        """
        if not isinstance(
            action,
            PostCommitAction,
        ):
            raise TypeError(
                "action must be a PostCommitAction."
            )

        try:
            action.execute(
                command,
                context,
                result,
            )
        except Exception:
            return


__all__ = [
    "PostCommitAction",
    "PostCommitExecutor",
]
