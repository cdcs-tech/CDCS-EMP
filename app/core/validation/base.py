"""
CDCS Enterprise Management Platform (CDCS-EMP)

Enterprise Validation Framework

Base validation framework.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class ValidationResult:
    """
    Represents the outcome of a validation operation.
    """

    valid: bool = True

    errors: list[str] = field(default_factory=list)

    warnings: list[str] = field(default_factory=list)

    metadata: dict[str, Any] = field(default_factory=dict)

    def add_error(self, message: str) -> None:
        """
        Add a validation error.
        """

        self.valid = False
        self.errors.append(message)

    def add_warning(self, message: str) -> None:
        """
        Add a validation warning.
        """

        self.warnings.append(message)

    def merge(
        self,
        other: "ValidationResult",
    ) -> None:
        """
        Merge another validation result.
        """

        if not other.valid:
            self.valid = False

        self.errors.extend(other.errors)
        self.warnings.extend(other.warnings)
        self.metadata.update(other.metadata)

    @property
    def has_errors(self) -> bool:
        """
        Return True if validation contains errors.
        """

        return bool(self.errors)

    @property
    def has_warnings(self) -> bool:
        """
        Return True if validation contains warnings.
        """

        return bool(self.warnings)


class BaseValidator(ABC):
    """
    Base class for all enterprise validators.
    """

    @abstractmethod
    def validate(
        self,
        target: Any,
    ) -> ValidationResult:
        """
        Validate the supplied object.

        Must be implemented by child validators.
        """

        raise NotImplementedError

    def validate_or_raise(
        self,
        target: Any,
        exception_class: type[Exception] | None = None,
    ) -> ValidationResult:
        """
        Validate an object and optionally raise
        an exception if validation fails.
        """

        result = self.validate(target)

        if result.valid:
            return result

        if exception_class is not None:
            raise exception_class(
                "; ".join(result.errors)
            )

        return result
