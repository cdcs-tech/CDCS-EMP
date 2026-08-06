"""
CDCS Enterprise Management Platform (CDCS-EMP)

Enterprise Validation Framework

Reusable validation rule engine.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Iterable

from app.core.validation.base import ValidationResult


class ValidationRule(ABC):
    """
    Base class for reusable validation rules.
    """

    @abstractmethod
    def validate(
        self,
        target: Any,
    ) -> ValidationResult:
        """
        Execute rule validation.

        Must return a ValidationResult.
        """

        raise NotImplementedError


class RuleSet:
    """
    Executes multiple validation rules.
    """

    def __init__(
        self,
        rules: Iterable[ValidationRule] | None = None,
    ):
        self._rules = list(rules or [])


    def add_rule(
        self,
        rule: ValidationRule,
    ) -> None:
        """
        Add a validation rule.
        """

        self._rules.append(rule)


    def remove_rule(
        self,
        rule: ValidationRule,
    ) -> None:
        """
        Remove a validation rule.
        """

        if rule in self._rules:
            self._rules.remove(rule)


    def clear(self) -> None:
        """
        Remove all validation rules.
        """

        self._rules.clear()


    def validate(
        self,
        target: Any,
    ) -> ValidationResult:
        """
        Execute all validation rules.
        """

        result = ValidationResult()

        for rule in self._rules:
            result.merge(
                rule.validate(target)
            )

        return result


    def count(self) -> int:
        """
        Return registered rule count.
        """

        return len(self._rules)


    def __iter__(self):
        """
        Iterate through rules.
        """

        return iter(self._rules)
