"""
CDCS Enterprise Management Platform (CDCS-EMP)

Reporting Framework

Report parameter contracts.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Iterable


class ReportParameterType(str, Enum):
    """
    Supported framework-level report parameter types.
    """

    STRING = "string"

    INTEGER = "integer"

    FLOAT = "float"

    BOOLEAN = "boolean"

    DATE = "date"

    DATETIME = "datetime"

    DECIMAL = "decimal"


@dataclass
class ReportParameter:
    """
    Defines a parameter accepted by a report.

    The parameter contract describes the parameter itself.
    Parameter validation, UI rendering, persistence, and
    report-specific interpretation remain outside this
    contract.
    """

    name: str

    label: str

    data_type: ReportParameterType = (
        ReportParameterType.STRING
    )

    description: str = ""

    default_value: Any = None

    required: bool = False

    allowed_values: list[Any] = field(
        default_factory=list
    )

    metadata: dict[str, Any] = field(
        default_factory=dict
    )

    def __post_init__(self) -> None:
        """
        Normalize and validate the parameter definition.
        """

        if not isinstance(
            self.name,
            str,
        ):
            raise ValueError(
                "Report parameter name must be a string."
            )

        if not isinstance(
            self.label,
            str,
        ):
            raise ValueError(
                "Report parameter label must be a string."
            )

        self.name = self.name.strip()

        self.label = self.label.strip()

        if not self.name:
            raise ValueError(
                "Report parameter name is required."
            )

        if not self.label:
            raise ValueError(
                "Report parameter label is required."
            )

        if not isinstance(
            self.data_type,
            ReportParameterType,
        ):
            try:
                self.data_type = (
                    ReportParameterType(
                        self.data_type
                    )
                )

            except (
                ValueError,
                TypeError,
            ) as error:

                raise ValueError(
                    "Invalid report parameter data type."
                ) from error

        self.description = (
            self.description.strip()
            if isinstance(
                self.description,
                str,
            )
            else str(
                self.description
            )
        )

        self.allowed_values = list(
            self.allowed_values
        )

        self.metadata = dict(
            self.metadata
        )

    def to_dict(self) -> dict[str, Any]:
        """
        Convert the parameter definition into
        a serializable dictionary.
        """

        return {
            "name": self.name,
            "label": self.label,
            "data_type": self.data_type.value,
            "description": self.description,
            "default_value": self.default_value,
            "required": self.required,
            "allowed_values": list(
                self.allowed_values
            ),
            "metadata": dict(
                self.metadata
            ),
        }


@dataclass
class ReportParameterCollection:
    """
    Collection of report parameter definitions.
    """

    parameters: list[
        ReportParameter
    ] = field(
        default_factory=list
    )

    def add(
        self,
        parameter: ReportParameter,
    ) -> None:
        """
        Add a parameter to the collection.
        """

        if not isinstance(
            parameter,
            ReportParameter,
        ):
            raise TypeError(
                "parameter must be a "
                "ReportParameter instance."
            )

        if self.contains(
            parameter.name
        ):
            raise ValueError(
                f"Report parameter "
                f"'{parameter.name}' "
                "is already defined."
            )

        self.parameters.append(
            parameter
        )

    def get(
        self,
        name: str,
    ) -> ReportParameter:
        """
        Retrieve a parameter by name.
        """

        if not isinstance(
            name,
            str,
        ):
            raise ValueError(
                "Report parameter name must be a string."
            )

        name = name.strip()

        for parameter in self.parameters:

            if parameter.name == name:
                return parameter

        raise KeyError(
            f"Report parameter "
            f"'{name}' was not found."
        )

    def contains(
        self,
        name: str,
    ) -> bool:
        """
        Determine whether a parameter exists.
        """

        if not isinstance(
            name,
            str,
        ):
            return False

        name = name.strip()

        return any(
            parameter.name == name
            for parameter in self.parameters
        )

    def remove(
        self,
        name: str,
    ) -> None:
        """
        Remove a parameter by name.
        """

        parameter = self.get(
            name
        )

        self.parameters.remove(
            parameter
        )

    def clear(self) -> None:
        """
        Remove all parameters.
        """

        self.parameters.clear()

    def all(
        self,
    ) -> list[ReportParameter]:
        """
        Return all parameter definitions.

        A new list is returned to prevent callers
        from replacing the collection directly.
        """

        return list(
            self.parameters
        )

    def to_list(
        self,
    ) -> list[dict[str, Any]]:
        """
        Convert all parameters into serializable
        dictionaries.
        """

        return [
            parameter.to_dict()
            for parameter in self.parameters
        ]

    def __len__(self) -> int:
        return len(
            self.parameters
        )

    def __iter__(
        self,
    ) -> Iterable[ReportParameter]:
        return iter(
            self.parameters
        )


__all__ = [
    "ReportParameterType",
    "ReportParameter",
    "ReportParameterCollection",
]
