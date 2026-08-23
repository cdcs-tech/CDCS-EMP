"""
CDCS Enterprise Management Platform (CDCS-EMP)

Reporting Framework

Report parameter binding and validation contracts.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from typing import Any, Mapping

from app.core.reporting.exceptions import (
    ReportValidationException,
)
from app.core.reporting.parameters import (
    ReportParameter,
    ReportParameterCollection,
    ReportParameterType,
)


# ---------------------------------------------------------
# Report Parameter Binding
# ---------------------------------------------------------


@dataclass(frozen=True)
class ReportParameterBinding:
    """
    Represents a validated runtime value bound to a
    report parameter definition.
    """

    name: str

    value: Any

    data_type: ReportParameterType

    supplied: bool = True

    defaulted: bool = False

    def __post_init__(self) -> None:
        """
        Validate and normalize the binding contract.
        """

        if not isinstance(
            self.name,
            str,
        ):
            raise ValueError(
                "Report parameter binding name "
                "must be a string."
            )

        normalized_name = self.name.strip()

        if not normalized_name:
            raise ValueError(
                "Report parameter binding name "
                "is required."
            )

        if not isinstance(
            self.data_type,
            ReportParameterType,
        ):
            try:
                normalized_type = ReportParameterType(
                    self.data_type
                )
            except (
                ValueError,
                TypeError,
            ) as error:
                raise ValueError(
                    "Invalid report parameter binding "
                    "data type."
                ) from error

            object.__setattr__(
                self,
                "data_type",
                normalized_type,
            )

        object.__setattr__(
            self,
            "name",
            normalized_name,
        )

    def to_dict(self) -> dict[str, Any]:
        """
        Convert the binding into a serializable
        dictionary.
        """

        return {
            "name": self.name,
            "value": self.value,
            "data_type": self.data_type.value,
            "supplied": self.supplied,
            "defaulted": self.defaulted,
        }


# ---------------------------------------------------------
# Bound Parameter Collection
# ---------------------------------------------------------


@dataclass(frozen=True)
class ReportParameterBindingCollection:
    """
    Represents the validated parameter values for a
    report execution.

    The collection is immutable at the contract level and
    provides controlled lookup and serialization.
    """

    bindings: tuple[
        ReportParameterBinding,
        ...,
    ] = ()

    def get(
        self,
        name: str,
    ) -> ReportParameterBinding:
        """
        Retrieve a bound parameter by name.
        """

        if not isinstance(
            name,
            str,
        ):
            raise ValueError(
                "Report parameter name must be a string."
            )

        normalized_name = name.strip()

        for binding in self.bindings:

            if binding.name == normalized_name:
                return binding

        raise KeyError(
            f"Report parameter '{normalized_name}' "
            "is not bound."
        )

    def contains(
        self,
        name: str,
    ) -> bool:
        """
        Determine whether a parameter is bound.
        """

        if not isinstance(
            name,
            str,
        ):
            return False

        normalized_name = name.strip()

        return any(
            binding.name == normalized_name
            for binding in self.bindings
        )

    def values(self) -> dict[str, Any]:
        """
        Return bound parameter values keyed by name.
        """

        return {
            binding.name: binding.value
            for binding in self.bindings
        }

    def to_dict(self) -> dict[str, Any]:
        """
        Serialize the complete binding collection.
        """

        return {
            binding.name: binding.to_dict()
            for binding in self.bindings
        }

    def __len__(self) -> int:
        return len(self.bindings)

    def __iter__(self):
        return iter(self.bindings)

    def __contains__(
        self,
        name: str,
    ) -> bool:
        return self.contains(name)


# ---------------------------------------------------------
# Report Parameter Binder
# ---------------------------------------------------------


class ReportParameterBinder:
    """
    Validates and binds runtime parameter values against
    declared report parameter definitions.

    The binder is provider-neutral and performs no query
    execution or persistence.
    """

    def bind(
        self,
        definitions: ReportParameterCollection,
        values: Mapping[str, Any] | None = None,
    ) -> ReportParameterBindingCollection:
        """
        Validate and bind supplied parameter values.

        Args:
            definitions:
                Declared report parameter definitions.

            values:
                Runtime parameter values supplied for
                report execution.

        Returns:
            Validated report parameter bindings.

        Raises:
            ReportValidationException:
                When supplied parameters violate the
                declared parameter contract.
        """

        if not isinstance(
            definitions,
            ReportParameterCollection,
        ):
            raise ReportValidationException(
                "Report parameter definitions must be "
                "a ReportParameterCollection."
            )

        if values is None:
            values = {}

        if not isinstance(
            values,
            Mapping,
        ):
            raise ReportValidationException(
                "Report parameter values must be a mapping."
            )

        normalized_values = self._normalize_values(
            values
        )

        self._validate_unknown_parameters(
            definitions,
            normalized_values,
        )

        bindings: list[
            ReportParameterBinding
        ] = []

        for definition in definitions:

            supplied = (
                definition.name
                in normalized_values
            )

            if supplied:

                raw_value = normalized_values[
                    definition.name
                ]

                value = self._validate_value(
                    definition,
                    raw_value,
                )

                bindings.append(
                    ReportParameterBinding(
                        name=definition.name,
                        value=value,
                        data_type=definition.data_type,
                        supplied=True,
                        defaulted=False,
                    )
                )

                continue

            if definition.default_value is not None:

                value = self._validate_value(
                    definition,
                    definition.default_value,
                )

                bindings.append(
                    ReportParameterBinding(
                        name=definition.name,
                        value=value,
                        data_type=definition.data_type,
                        supplied=False,
                        defaulted=True,
                    )
                )

                continue

            if definition.required:

                raise ReportValidationException(
                    f"Required report parameter "
                    f"'{definition.name}' was not supplied."
                )

            bindings.append(
                ReportParameterBinding(
                    name=definition.name,
                    value=None,
                    data_type=definition.data_type,
                    supplied=False,
                    defaulted=False,
                )
            )

        return ReportParameterBindingCollection(
            bindings=tuple(bindings)
        )

    def _normalize_values(
        self,
        values: Mapping[str, Any],
    ) -> dict[str, Any]:
        """
        Normalize runtime parameter names.
        """

        normalized: dict[str, Any] = {}

        for name, value in values.items():

            if not isinstance(
                name,
                str,
            ):
                raise ReportValidationException(
                    "Report parameter names must be strings."
                )

            normalized_name = name.strip()

            if not normalized_name:
                raise ReportValidationException(
                    "Report parameter name cannot be empty."
                )

            if normalized_name in normalized:
                raise ReportValidationException(
                    f"Duplicate report parameter "
                    f"'{normalized_name}' was supplied."
                )

            normalized[
                normalized_name
            ] = value

        return normalized

    def _validate_unknown_parameters(
        self,
        definitions: ReportParameterCollection,
        values: Mapping[str, Any],
    ) -> None:
        """
        Reject runtime parameters that are not declared.
        """

        for name in values:

            if not definitions.contains(name):

                raise ReportValidationException(
                    f"Unknown report parameter "
                    f"'{name}' was supplied."
                )

    def _validate_value(
        self,
        definition: ReportParameter,
        value: Any,
    ) -> Any:
        """
        Validate and normalize a runtime parameter value.
        """

        if value is None:

            if definition.required:

                raise ReportValidationException(
                    f"Required report parameter "
                    f"'{definition.name}' cannot be None."
                )

            return None

        try:

            normalized = self._convert_value(
                definition.data_type,
                value,
            )

        except (
            ValueError,
            TypeError,
            InvalidOperation,
        ) as error:

            raise ReportValidationException(
                f"Invalid value for report parameter "
                f"'{definition.name}'."
            ) from error

        if definition.allowed_values:

            if normalized not in definition.allowed_values:

                raise ReportValidationException(
                    f"Value for report parameter "
                    f"'{definition.name}' is not allowed."
                )

        return normalized

    def _convert_value(
        self,
        data_type: ReportParameterType,
        value: Any,
    ) -> Any:
        """
        Convert a runtime value to its declared type.
        """

        if data_type == ReportParameterType.STRING:

            if isinstance(
                value,
                str,
            ):
                return value

            return str(value)

        if data_type == ReportParameterType.INTEGER:

            if isinstance(
                value,
                bool,
            ):
                raise TypeError(
                    "Boolean is not a valid integer."
                )

            return int(value)

        if data_type == ReportParameterType.FLOAT:

            if isinstance(
                value,
                bool,
            ):
                raise TypeError(
                    "Boolean is not a valid float."
                )

            return float(value)

        if data_type == ReportParameterType.BOOLEAN:

            if isinstance(
                value,
                bool,
            ):
                return value

            if isinstance(
                value,
                str,
            ):

                normalized = value.strip().lower()

                if normalized in {
                    "true",
                    "1",
                    "yes",
                    "y",
                }:
                    return True

                if normalized in {
                    "false",
                    "0",
                    "no",
                    "n",
                }:
                    return False

            if isinstance(
                value,
                int,
            ) and value in {
                0,
                1,
            }:
                return bool(value)

            raise ValueError(
                "Invalid boolean value."
            )

        if data_type == ReportParameterType.DATE:

            if isinstance(
                value,
                datetime,
            ):
                return value.date()

            if isinstance(
                value,
                date,
            ):
                return value

            if isinstance(
                value,
                str,
            ):
                return date.fromisoformat(
                    value.strip()
                )

            raise TypeError(
                "Invalid date value."
            )

        if data_type == ReportParameterType.DATETIME:

            if isinstance(
                value,
                datetime,
            ):
                return value

            if isinstance(
                value,
                str,
            ):
                return datetime.fromisoformat(
                    value.strip()
                )

            raise TypeError(
                "Invalid datetime value."
            )

        if data_type == ReportParameterType.DECIMAL:

            if isinstance(
                value,
                bool,
            ):
                raise TypeError(
                    "Boolean is not a valid decimal."
                )

            return Decimal(
                str(value)
            )

        raise ValueError(
            f"Unsupported report parameter type "
            f"'{data_type}'."
        )


__all__ = [
    "ReportParameterBinding",
    "ReportParameterBindingCollection",
    "ReportParameterBinder",
]
