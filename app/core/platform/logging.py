"""
CDCS Enterprise Management Platform (CDCS-EMP)

Platform Infrastructure

Platform Logging Foundation.

Provides a standardized logging interface
for enterprise platform components.
"""

import logging
from typing import Any, Optional

from app.core.platform.context import (
    RequestContext,
)


DEFAULT_LOGGER_NAME = "cdcs_emp"


class PlatformLogger:
    """
    Centralized platform logging wrapper.
    """

    def __init__(
        self,
        name: str = DEFAULT_LOGGER_NAME,
        logger: Optional[
            logging.Logger
        ] = None,
    ):
        """
        Initialize the platform logger.
        """

        self.logger = (
            logger
            or logging.getLogger(name)
        )

    def _extra(
        self,
        context: Optional[
            RequestContext
        ] = None,
        **extra: Any,
    ) -> dict[str, Any]:
        """
        Build structured logging metadata.
        """

        data = dict(extra)

        if context is not None:

            data.setdefault(
                "request_id",
                context.request_id,
            )

            data.setdefault(
                "correlation_id",
                context.correlation_id,
            )

            data.setdefault(
                "trace_id",
                context.trace_id,
            )

            data.setdefault(
                "user_id",
                context.user_id,
            )

            data.setdefault(
                "module_name",
                context.module_name,
            )

            data.setdefault(
                "operation",
                context.operation,
            )

        return data

    def debug(
        self,
        message: str,
        *,
        context: Optional[
            RequestContext
        ] = None,
        **extra: Any,
    ) -> None:
        """
        Log a DEBUG message.
        """

        self.logger.debug(
            message,
            extra=self._extra(
                context,
                **extra,
            ),
        )

    def info(
        self,
        message: str,
        *,
        context: Optional[
            RequestContext
        ] = None,
        **extra: Any,
    ) -> None:
        """
        Log an INFO message.
        """

        self.logger.info(
            message,
            extra=self._extra(
                context,
                **extra,
            ),
        )

    def warning(
        self,
        message: str,
        *,
        context: Optional[
            RequestContext
        ] = None,
        **extra: Any,
    ) -> None:
        """
        Log a WARNING message.
        """

        self.logger.warning(
            message,
            extra=self._extra(
                context,
                **extra,
            ),
        )

    def error(
        self,
        message: str,
        *,
        context: Optional[
            RequestContext
        ] = None,
        **extra: Any,
    ) -> None:
        """
        Log an ERROR message.
        """

        self.logger.error(
            message,
            extra=self._extra(
                context,
                **extra,
            ),
        )

    def critical(
        self,
        message: str,
        *,
        context: Optional[
            RequestContext
        ] = None,
        **extra: Any,
    ) -> None:
        """
        Log a CRITICAL message.
        """

        self.logger.critical(
            message,
            extra=self._extra(
                context,
                **extra,
            ),
        )

    def exception(
        self,
        message: str,
        *,
        context: Optional[
            RequestContext
        ] = None,
        **extra: Any,
    ) -> None:
        """
        Log an exception with traceback information.
        """

        self.logger.exception(
            message,
            extra=self._extra(
                context,
                **extra,
            ),
        )

    def set_level(
        self,
        level: int,
    ) -> None:
        """
        Set the logger level.
        """

        self.logger.setLevel(
            level
        )

    def get_level(self) -> int:
        """
        Return the current logger level.
        """

        return self.logger.level

    def __repr__(self) -> str:
        """
        Developer-friendly representation.
        """

        return (
            f"<PlatformLogger "
            f"name={self.logger.name!r} "
            f"level={self.logger.level}>"
        )


platform_logger = PlatformLogger()


__all__ = [
    "DEFAULT_LOGGER_NAME",
    "PlatformLogger",
    "platform_logger",
]
