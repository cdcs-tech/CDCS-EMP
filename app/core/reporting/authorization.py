"""
CDCS Enterprise Management Platform (CDCS-EMP)

Reporting & Analytics Framework

Provider-neutral reporting authorization contracts.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class ReportAuthorizationOperation(str, Enum):
    """
    Supported provider-neutral reporting authorization
    operations.

    The operation describes what the requesting subject wants
    to do with a reporting resource.
    """

    VIEW = "view"

    EXECUTE = "execute"

    EXPORT = "export"

    MANAGE = "manage"

    @classmethod
    def normalize(
        cls,
        value: ReportAuthorizationOperation | str,
    ) -> ReportAuthorizationOperation:
        """
        Normalize an authorization operation value.

        Args:
            value:
                A ReportAuthorizationOperation instance or
                supported string representation.

        Returns:
            ReportAuthorizationOperation:
                The normalized operation.

        Raises:
            ValueError:
                When the supplied value is invalid.
        """

        if isinstance(
            value,
            cls,
        ):
            return value

        if not isinstance(
            value,
            str,
        ):
            raise ValueError(
                "Report authorization operation must be a "
                "ReportAuthorizationOperation instance "
                "or string."
            )

        normalized_value = value.strip().lower()

        if not normalized_value:
            raise ValueError(
                "Report authorization operation is required."
            )

        try:
            return cls(
                normalized_value
            )

        except ValueError as exc:
            raise ValueError(
                "Report authorization operation is invalid."
            ) from exc

    @property
    def code(
        self,
    ) -> str:
        """
        Return the canonical operation code.
        """

        return self.value

    def to_dict(
        self,
    ) -> dict[str, str]:
        """
        Convert the operation into a stable dictionary
        representation.
        """

        return {
            "code": self.code,
        }


@dataclass(frozen=True)
class ReportAuthorizationResource:
    """
    Represents a provider-neutral reporting resource.

    The resource identifies what reporting object is being
    protected without coupling the authorization contract to
    persistence or application-specific resource models.
    """

    resource_type: str

    identifier: str

    metadata: dict[str, Any] = field(
        default_factory=dict
    )

    def __post_init__(self) -> None:
        """
        Validate and normalize the reporting resource.
        """

        if not isinstance(
            self.resource_type,
            str,
        ):
            raise ValueError(
                "Report authorization resource_type must be "
                "a string."
            )

        normalized_resource_type = (
            self.resource_type.strip().lower()
        )

        if not normalized_resource_type:
            raise ValueError(
                "Report authorization resource_type is required."
            )

        object.__setattr__(
            self,
            "resource_type",
            normalized_resource_type,
        )

        if not isinstance(
            self.identifier,
            str,
        ):
            raise ValueError(
                "Report authorization resource identifier "
                "must be a string."
            )

        normalized_identifier = (
            self.identifier.strip()
        )

        if not normalized_identifier:
            raise ValueError(
                "Report authorization resource identifier "
                "is required."
            )

        object.__setattr__(
            self,
            "identifier",
            normalized_identifier,
        )

        if not isinstance(
            self.metadata,
            dict,
        ):
            raise ValueError(
                "Report authorization resource metadata "
                "must be a dictionary."
            )

        object.__setattr__(
            self,
            "metadata",
            dict(
                self.metadata
            ),
        )

    @property
    def canonical_identifier(
        self,
    ) -> str:
        """
        Return the canonical resource identifier.

        The resource type and identifier are combined to
        provide a stable provider-neutral resource identity.
        """

        return (
            f"{self.resource_type}:"
            f"{self.identifier}"
        )

    def to_dict(
        self,
    ) -> dict[str, Any]:
        """
        Convert the resource into a stable dictionary
        representation.
        """

        return {
            "resource_type": self.resource_type,
            "identifier": self.identifier,
            "canonical_identifier": (
                self.canonical_identifier
            ),
            "metadata": dict(
                self.metadata
            ),
        }


@dataclass(frozen=True)
class ReportAuthorizationSubject:
    """
    Represents a provider-neutral authorization subject.

    The subject identifies the actor requesting access without
    embedding an application-specific user or identity model.
    """

    identifier: str

    subject_type: str = "user"

    metadata: dict[str, Any] = field(
        default_factory=dict
    )

    def __post_init__(self) -> None:
        """
        Validate and normalize the authorization subject.
        """

        if not isinstance(
            self.identifier,
            str,
        ):
            raise ValueError(
                "Report authorization subject identifier "
                "must be a string."
            )

        normalized_identifier = (
            self.identifier.strip()
        )

        if not normalized_identifier:
            raise ValueError(
                "Report authorization subject identifier "
                "is required."
            )

        object.__setattr__(
            self,
            "identifier",
            normalized_identifier,
        )

        if not isinstance(
            self.subject_type,
            str,
        ):
            raise ValueError(
                "Report authorization subject_type must "
                "be a string."
            )

        normalized_subject_type = (
            self.subject_type.strip().lower()
        )

        if not normalized_subject_type:
            raise ValueError(
                "Report authorization subject_type "
                "is required."
            )

        object.__setattr__(
            self,
            "subject_type",
            normalized_subject_type,
        )

        if not isinstance(
            self.metadata,
            dict,
        ):
            raise ValueError(
                "Report authorization subject metadata "
                "must be a dictionary."
            )

        object.__setattr__(
            self,
            "metadata",
            dict(
                self.metadata
            ),
        )

    @property
    def canonical_identifier(
        self,
    ) -> str:
        """
        Return the canonical subject identifier.
        """

        return (
            f"{self.subject_type}:"
            f"{self.identifier}"
        )

    def to_dict(
        self,
    ) -> dict[str, Any]:
        """
        Convert the subject into a stable dictionary
        representation.
        """

        return {
            "identifier": self.identifier,
            "subject_type": self.subject_type,
            "canonical_identifier": (
                self.canonical_identifier
            ),
            "metadata": dict(
                self.metadata
            ),
        }


@dataclass(frozen=True)
class ReportAuthorizationContext:
    """
    Represents provider-neutral context accompanying a
    reporting authorization request.

    Context provides additional attributes required by an
    authorization boundary without embedding authorization
    implementation details.
    """

    metadata: dict[str, Any] = field(
        default_factory=dict
    )

    def __post_init__(self) -> None:
        """
        Validate and isolate authorization context metadata.
        """

        if not isinstance(
            self.metadata,
            dict,
        ):
            raise ValueError(
                "Report authorization context metadata "
                "must be a dictionary."
            )

        object.__setattr__(
            self,
            "metadata",
            dict(
                self.metadata
            ),
        )

    def to_dict(
        self,
    ) -> dict[str, Any]:
        """
        Convert the authorization context into a stable
        dictionary representation.
        """

        return {
            "metadata": dict(
                self.metadata
            ),
        }


@dataclass(frozen=True)
class ReportAuthorizationRequest:
    """
    Represents a complete provider-neutral reporting
    authorization request.

    The request combines:

    - authorization subject,
    - requested operation,
    - protected reporting resource, and
    - authorization context.

    The request does not evaluate authorization.
    """

    subject: ReportAuthorizationSubject

    operation: ReportAuthorizationOperation

    resource: ReportAuthorizationResource

    context: ReportAuthorizationContext = field(
        default_factory=ReportAuthorizationContext
    )

    metadata: dict[str, Any] = field(
        default_factory=dict
    )

    def __post_init__(self) -> None:
        """
        Validate and normalize the authorization request.
        """

        if not isinstance(
            self.subject,
            ReportAuthorizationSubject,
        ):
            raise ValueError(
                "Report authorization request subject must "
                "be a ReportAuthorizationSubject."
            )

        operation = self.operation

        if isinstance(
            operation,
            str,
        ):
            operation = (
                ReportAuthorizationOperation.normalize(
                    operation
                )
            )

            object.__setattr__(
                self,
                "operation",
                operation,
            )

        elif not isinstance(
            operation,
            ReportAuthorizationOperation,
        ):
            raise ValueError(
                "Report authorization request operation must "
                "be a ReportAuthorizationOperation."
            )

        if not isinstance(
            self.resource,
            ReportAuthorizationResource,
        ):
            raise ValueError(
                "Report authorization request resource must "
                "be a ReportAuthorizationResource."
            )

        if not isinstance(
            self.context,
            ReportAuthorizationContext,
        ):
            raise ValueError(
                "Report authorization request context must "
                "be a ReportAuthorizationContext."
            )

        if not isinstance(
            self.metadata,
            dict,
        ):
            raise ValueError(
                "Report authorization request metadata "
                "must be a dictionary."
            )

        object.__setattr__(
            self,
            "metadata",
            dict(
                self.metadata
            ),
        )

    @property
    def identifier(
        self,
    ) -> str:
        """
        Return the canonical authorization request
        identifier.

        The identifier combines subject, operation, and
        resource identity.
        """

        return (
            f"{self.subject.canonical_identifier}:"
            f"{self.operation.code}:"
            f"{self.resource.canonical_identifier}"
        )

    def to_dict(
        self,
    ) -> dict[str, Any]:
        """
        Convert the authorization request into a stable
        dictionary representation.
        """

        return {
            "subject": self.subject.to_dict(),
            "operation": self.operation.to_dict(),
            "resource": self.resource.to_dict(),
            "context": self.context.to_dict(),
            "metadata": dict(
                self.metadata
            ),
            "identifier": self.identifier,
        }


class ReportAuthorizationDecisionStatus(str, Enum):
    """
    Supported provider-neutral reporting authorization
    decision states.
    """

    ALLOW = "allow"

    DENY = "deny"

    @classmethod
    def normalize(
        cls,
        value: (
            ReportAuthorizationDecisionStatus
            | str
        ),
    ) -> ReportAuthorizationDecisionStatus:
        """
        Normalize an authorization decision status.

        Args:
            value:
                A ReportAuthorizationDecisionStatus instance
                or supported string representation.

        Returns:
            ReportAuthorizationDecisionStatus:
                The normalized decision status.

        Raises:
            ValueError:
                When the supplied value is invalid.
        """

        if isinstance(
            value,
            cls,
        ):
            return value

        if not isinstance(
            value,
            str,
        ):
            raise ValueError(
                "Report authorization decision status must "
                "be a ReportAuthorizationDecisionStatus "
                "instance or string."
            )

        normalized_value = value.strip().lower()

        if not normalized_value:
            raise ValueError(
                "Report authorization decision status "
                "is required."
            )

        try:
            return cls(
                normalized_value
            )

        except ValueError as exc:
            raise ValueError(
                "Report authorization decision status "
                "is invalid."
            ) from exc

    @property
    def is_allowed(
        self,
    ) -> bool:
        """
        Determine whether the decision allows the request.
        """

        return (
            self
            is ReportAuthorizationDecisionStatus.ALLOW
        )

    @property
    def is_denied(
        self,
    ) -> bool:
        """
        Determine whether the decision denies the request.
        """

        return (
            self
            is ReportAuthorizationDecisionStatus.DENY
        )

    def to_dict(
        self,
    ) -> dict[str, str]:
        """
        Convert the decision status into a stable dictionary
        representation.
        """

        return {
            "status": self.value,
        }


@dataclass(frozen=True)
class ReportAuthorizationDecision:
    """
    Represents the provider-neutral result of a reporting
    authorization decision.

    The decision communicates the authorization outcome but
    does not prescribe how that outcome was produced.
    """

    status: ReportAuthorizationDecisionStatus

    reason: str | None = None

    metadata: dict[str, Any] = field(
        default_factory=dict
    )

    def __post_init__(self) -> None:
        """
        Validate and normalize the authorization decision.
        """

        status = self.status

        if isinstance(
            status,
            str,
        ):
            status = (
                ReportAuthorizationDecisionStatus.normalize(
                    status
                )
            )

            object.__setattr__(
                self,
                "status",
                status,
            )

        elif not isinstance(
            status,
            ReportAuthorizationDecisionStatus,
        ):
            raise ValueError(
                "Report authorization decision status must "
                "be a ReportAuthorizationDecisionStatus."
            )

        if self.reason is not None:

            if not isinstance(
                self.reason,
                str,
            ):
                raise ValueError(
                    "Report authorization decision reason "
                    "must be a string or None."
                )

            normalized_reason = (
                self.reason.strip()
            )

            if not normalized_reason:
                object.__setattr__(
                    self,
                    "reason",
                    None,
                )
            else:
                object.__setattr__(
                    self,
                    "reason",
                    normalized_reason,
                )

        if not isinstance(
            self.metadata,
            dict,
        ):
            raise ValueError(
                "Report authorization decision metadata "
                "must be a dictionary."
            )

        object.__setattr__(
            self,
            "metadata",
            dict(
                self.metadata
            ),
        )

    @property
    def is_allowed(
        self,
    ) -> bool:
        """
        Determine whether authorization was granted.
        """

        return self.status.is_allowed

    @property
    def is_denied(
        self,
    ) -> bool:
        """
        Determine whether authorization was denied.
        """

        return self.status.is_denied

    def to_dict(
        self,
    ) -> dict[str, Any]:
        """
        Convert the authorization decision into a stable
        dictionary representation.
        """

        return {
            "status": self.status.value,
            "reason": self.reason,
            "metadata": dict(
                self.metadata
            ),
            "is_allowed": self.is_allowed,
            "is_denied": self.is_denied,
        }


__all__ = [
    "ReportAuthorizationOperation",
    "ReportAuthorizationResource",
    "ReportAuthorizationSubject",
    "ReportAuthorizationContext",
    "ReportAuthorizationRequest",
    "ReportAuthorizationDecisionStatus",
    "ReportAuthorizationDecision",
]
