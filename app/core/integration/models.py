"""
CDCS Enterprise Management Platform (CDCS-EMP)

Enterprise Integration Framework

Integration Models

Defines standardized request, response,
status, and metadata contracts used by
enterprise integration providers.
"""

from dataclasses import (
    dataclass,
    field,
)
from datetime import datetime, timezone
from typing import Any, Optional
from uuid import uuid4


@dataclass(slots=True)
class IntegrationRequest:
    """
    Standard integration request.

    Represents an outbound operation initiated
    by a CDCS-EMP service or module.
    """

    provider: str

    operation: str

    payload: Any = None

    headers: dict[str, str] = field(
        default_factory=dict
    )

    metadata: dict[str, Any] = field(
        default_factory=dict
    )

    request_id: str = field(
        default_factory=lambda: str(uuid4())
    )

    created_at: datetime = field(
        default_factory=lambda:
        datetime.now(timezone.utc)
    )

    timeout: Optional[float] = None

    def __post_init__(self):
        """
        Validate the integration request.
        """

        if not self.provider:
            raise ValueError(
                "Integration provider is required."
            )

        if not self.operation:
            raise ValueError(
                "Integration operation is required."
            )

        if self.timeout is not None:
            if self.timeout <= 0:
                raise ValueError(
                    "Integration timeout must be greater than zero."
                )


@dataclass(slots=True)
class IntegrationResponse:
    """
    Standard integration response.

    Represents the normalized result returned
    by an integration provider.
    """

    success: bool

    status_code: Optional[int] = None

    data: Any = None

    message: str = ""

    error: Optional[str] = None

    metadata: dict[str, Any] = field(
        default_factory=dict
    )

    request_id: Optional[str] = None

    received_at: datetime = field(
        default_factory=lambda:
        datetime.now(timezone.utc)
    )

    @property
    def failed(self) -> bool:
        """
        Determine whether the response failed.
        """

        return not self.success


@dataclass(slots=True)
class IntegrationResult:
    """
    Standard integration operation result.

    Provides a consistent representation of
    the complete integration lifecycle.
    """

    request: IntegrationRequest

    response: Optional[
        IntegrationResponse
    ] = None

    duration_ms: Optional[float] = None

    provider: Optional[str] = None

    operation: Optional[str] = None

    metadata: dict[str, Any] = field(
        default_factory=dict
    )

    @property
    def success(self) -> bool:
        """
        Determine whether the integration
        operation succeeded.
        """

        return (
            self.response is not None
            and self.response.success
        )

    @property
    def failed(self) -> bool:
        """
        Determine whether the integration
        operation failed.
        """

        return not self.success

