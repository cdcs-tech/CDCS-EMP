"""
CDCS Enterprise Management Platform (CDCS-EMP)

Platform Infrastructure

Runtime Context.

Provides standardized information about
the current CDCS-EMP runtime environment.
"""

from dataclasses import dataclass
from typing import Optional

from app.core.platform.config import (
    PlatformConfig,
    platform_config,
)


@dataclass(slots=True)
class RuntimeContext:
    """
    Represents the active platform runtime context.
    """

    config: PlatformConfig

    application_name: str = ""
    application_version: str = ""

    environment: str = ""

    debug: bool = False
    testing: bool = False

    runtime_id: Optional[str] = None

    def __post_init__(self):
        """
        Initialize runtime information from
        platform configuration.
        """

        if not self.application_name:
            self.application_name = (
                self.config.app_name
            )

        if not self.application_version:
            self.application_version = (
                self.config.app_version
            )

        if not self.environment:
            self.environment = (
                self.config.environment
            )

        self.debug = self.config.debug
        self.testing = self.config.testing

    @property
    def is_development(self) -> bool:
        """
        Determine whether runtime is development.
        """

        return (
            self.environment.lower()
            == "development"
        )

    @property
    def is_testing(self) -> bool:
        """
        Determine whether runtime is testing.
        """

        return (
            self.testing
            or self.environment.lower()
            == "testing"
        )

    @property
    def is_production(self) -> bool:
        """
        Determine whether runtime is production.
        """

        return (
            self.environment.lower()
            == "production"
        )

    def identity(self) -> dict:
        """
        Return runtime identity information.
        """

        return {
            "application_name": (
                self.application_name
            ),
            "application_version": (
                self.application_version
            ),
            "environment": (
                self.environment
            ),
            "debug": self.debug,
            "testing": self.testing,
            "runtime_id": self.runtime_id,
        }

    def validate(self) -> bool:
        """
        Validate runtime context.
        """

        self.config.validate()

        if not self.application_name:
            raise ValueError(
                "Runtime application name is required."
            )

        if not self.application_version:
            raise ValueError(
                "Runtime application version is required."
            )

        if not self.environment:
            raise ValueError(
                "Runtime environment is required."
            )

        return True

    def __repr__(self) -> str:
        """
        Developer-friendly representation.
        """

        return (
            f"<RuntimeContext "
            f"application="
            f"{self.application_name!r} "
            f"version="
            f"{self.application_version!r} "
            f"environment="
            f"{self.environment!r}>"
        )


runtime_context = RuntimeContext(
    config=platform_config
)


__all__ = [
    "RuntimeContext",
    "runtime_context",
]

