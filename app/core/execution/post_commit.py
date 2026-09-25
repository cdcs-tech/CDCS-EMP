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


class PostCommitExecutor(ABC):
    """
    Dispatcher-facing contract for post-commit execution.

    The executor is invoked only after the originating
    transaction has committed successfully.

    Implementations are responsible for coordinating
    eligible post-commit actions or integrations.

    The dispatcher does not select individual actions.
    """

    @abstractmethod
    def execute(
        self,
        command: Any,
        context: Any,
        result: Any,
    ) -> None:
        """
        Execute eligible post-commit processing.

        The originating transaction has already committed
        successfully when this method is invoked.

        Implementations must not attempt to roll back,
        reject, cancel, or otherwise alter the already
        committed command transaction.
        """
        raise NotImplementedError


__all__ = [
    "PostCommitAction",
    "PostCommitExecutor",
]
