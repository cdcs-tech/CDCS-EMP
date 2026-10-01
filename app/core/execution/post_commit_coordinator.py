"""
CDCS Enterprise Management Platform (CDCS-EMP)

Enterprise post-commit coordination infrastructure.

Coordinates multiple post-commit executors behind the single
PostCommitExecutor boundary exposed by the CommandDispatcher.
"""

from __future__ import annotations

from collections.abc import Iterable

from app.core.execution.context import ExecutionContext
from app.core.execution.post_commit import PostCommitExecutor
from app.core.execution.results import ExecutionResult


class PostCommitCoordinator(
    PostCommitExecutor
):
    """
    Coordinate multiple post-commit executors.

    The coordinator is an application-infrastructure component.
    It deliberately contains no module-specific business logic.

    Individual executor failures are propagated to the caller.
    CommandDispatcher remains responsible for isolating post-commit
    failures from the already-committed originating transaction.
    """

    def __init__(
        self,
        executors: Iterable[
            PostCommitExecutor
        ] | None = None,
    ) -> None:

        self._executors: list[
            PostCommitExecutor
        ] = []

        if executors is not None:

            for executor in executors:

                self.register(
                    executor
                )

    def register(
        self,
        executor: PostCommitExecutor,
    ) -> None:
        """
        Register one post-commit executor.

        Executors are invoked in registration order.
        """

        if not isinstance(
            executor,
            PostCommitExecutor,
        ):
            raise TypeError(
                "Post-commit executor must "
                "implement PostCommitExecutor."
            )

        self._executors.append(
            executor
        )

    def executors(
        self,
    ) -> tuple[
        PostCommitExecutor,
        ...,
    ]:
        """
        Return the registered executors
        in execution order.
        """

        return tuple(
            self._executors
        )

    def execute(
        self,
        command,
        context: ExecutionContext,
        result: ExecutionResult,
    ) -> None:
        """
        Execute all registered post-commit executors.

        Exceptions are intentionally propagated. The enclosing
        CommandDispatcher owns post-commit failure isolation.
        """

        for executor in self._executors:

            executor.execute(
                command,
                context,
                result,
            )
