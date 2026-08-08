"""
CDCS Enterprise Management Platform (CDCS-EMP)

Platform Infrastructure

Platform configuration foundation.

Provides a centralized and controlled
configuration object for platform services.
"""

import os

from dataclasses import dataclass
from typing import Optional


@dataclass(slots=True)
class PlatformConfig:
    """
    Central platform configuration.

    Configuration values may be supplied
    explicitly or loaded from environment
    variables.
    """

    environment: str = "development"

    debug: bool = False

    testing: bool = False

    secret_key: str = ""

    database_url: Optional[str] = None

    log_level: str = "INFO"

    app_name: str = (
        "CDCS Enterprise Management Platform"
    )

    app_version: str = "1.0.0"


    @classmethod
    def from_environment(
        cls,
    ) -> "PlatformConfig":
        """
        Build platform configuration from
        environment variables.
        """

        return cls(
            environment=os.getenv(
                "CDCS_ENVIRONMENT",
                "development",
            ),

            debug=(
                os.getenv(
                    "CDCS_DEBUG",
                    "false",
                ).lower()
                == "true"
            ),

            testing=(
                os.getenv(
                    "CDCS_TESTING",
                    "false",
                ).lower()
                == "true"
            ),

            secret_key=os.getenv(
                "CDCS_SECRET_KEY",
                "",
            ),

            database_url=os.getenv(
                "CDCS_DATABASE_URL"
            ),

            log_level=os.getenv(
                "CDCS_LOG_LEVEL",
                "INFO",
            ),

            app_name=os.getenv(
                "CDCS_APP_NAME",
                "CDCS Enterprise Management Platform",
            ),

            app_version=os.getenv(
                "CDCS_APP_VERSION",
                "1.0.0",
            ),
        )


    def validate(self) -> bool:
        """
        Validate platform configuration.
        """

        if not self.environment:
            raise ValueError(
                "Platform environment is required."
            )

        if not self.app_name:
            raise ValueError(
                "Platform application name is required."
            )

        if not self.app_version:
            raise ValueError(
                "Platform application version is required."
            )

        if not self.log_level:
            raise ValueError(
                "Platform log level is required."
            )

        return True


    @property
    def is_development(self) -> bool:
        """
        Determine whether the platform is running
        in development mode.
        """

        return (
            self.environment.lower()
            == "development"
        )


    @property
    def is_testing(self) -> bool:
        """
        Determine whether the platform is running
        in testing mode.
        """

        return (
            self.testing
            or self.environment.lower()
            == "testing"
        )


    @property
    def is_production(self) -> bool:
        """
        Determine whether the platform is running
        in production mode.
        """

        return (
            self.environment.lower()
            == "production"
        )


    def __repr__(self) -> str:
        """
        Developer-friendly representation.
        """

        return (
            f"<PlatformConfig "
            f"environment={self.environment!r} "
            f"debug={self.debug} "
            f"testing={self.testing}>"
        )


platform_config = (
    PlatformConfig.from_environment()
)

