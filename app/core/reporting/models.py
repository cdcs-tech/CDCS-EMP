"""
CDCS Enterprise Management Platform (CDCS-EMP)

Reporting Framework

Core reporting model contracts.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Iterable, Iterator, Tuple


# ---------------------------------------------------------
# Report Parameter
# ---------------------------------------------------------


@dataclass(frozen=True)
class ReportParameter:
    """
    Represents a parameter accepted by a report definition.

    A report parameter defines the metadata required to
    describe an input value used during report generation.
    """

    name: str

    label: str

    data_type: str = "string"

    required: bool = False

    default: Any = None

    description: str = ""

    def __post_init__(self) -> None:
        """
        Validate and normalize the report parameter.
        """

        if not isinstance(
            self.name,
            str,
        ):
            raise ValueError(
                "Report parameter name must be a string."
            )

        if not self.name.strip():
            raise ValueError(
                "Report parameter name is required."
            )

        if not isinstance(
            self.label,
            str,
        ):
            raise ValueError(
                "Report parameter label must be a string."
            )

        if not self.label.strip():
            raise ValueError(
                "Report parameter label is required."
            )

        if not isinstance(
            self.data_type,
            str,
        ):
            raise ValueError(
                "Report parameter data_type must be a string."
            )

        if not self.data_type.strip():
            raise ValueError(
                "Report parameter data_type is required."
            )


# ---------------------------------------------------------
# Report Parameter Collection
# ---------------------------------------------------------


@dataclass
class ReportParameterCollection:
    """
    Represents an ordered collection of report parameters.

    The collection provides a stable contract for managing
    report parameters independently from the report
    definition itself.
    """

    parameters: list[ReportParameter] = field(
        default_factory=list
    )

    def __post_init__(self) -> None:
        """
        Validate the initial parameter collection.
        """

        normalized: list[ReportParameter] = []

        for parameter in self.parameters:

            if not isinstance(
                parameter,
                ReportParameter,
            ):
                raise ValueError(
                    "Report parameter collection "
                    "must contain ReportParameter instances."
                )

            normalized.append(
                parameter
            )

        self.parameters = normalized

    def add(
        self,
        parameter: ReportParameter,
    ) -> None:
        """
        Add a report parameter.

        Raises:
            ValueError:
                When the supplied value is not a
                ReportParameter instance or when a
                parameter with the same name already exists.
        """

        if not isinstance(
            parameter,
            ReportParameter,
        ):
            raise ValueError(
                "parameter must be a ReportParameter instance."
            )

        if self.has(
            parameter.name
        ):
            raise ValueError(
                f"Report parameter '{parameter.name}' "
                "is already defined."
            )

        self.parameters.append(
            parameter
        )

    def remove(
        self,
        name: str,
    ) -> None:
        """
        Remove a parameter by name.

        Raises:
            KeyError:
                When the parameter does not exist.
        """

        for index, parameter in enumerate(
            self.parameters
        ):

            if parameter.name == name:

                del self.parameters[index]

                return

        raise KeyError(
            f"Report parameter '{name}' "
            "is not defined."
        )

    def get(
        self,
        name: str,
    ) -> ReportParameter:
        """
        Retrieve a parameter by name.

        Raises:
            KeyError:
                When the parameter does not exist.
        """

        for parameter in self.parameters:

            if parameter.name == name:
                return parameter

        raise KeyError(
            f"Report parameter '{name}' "
            "is not defined."
        )

    def has(
        self,
        name: str,
    ) -> bool:
        """
        Determine whether a parameter exists.
        """

        return any(
            parameter.name == name
            for parameter in self.parameters
        )

    def clear(self) -> None:
        """
        Remove all parameters.
        """

        self.parameters.clear()

    def count(self) -> int:
        """
        Return the number of parameters.
        """

        return len(
            self.parameters
        )

    def to_list(self) -> list[dict[str, Any]]:
        """
        Serialize the collection into a list.
        """

        return [
            {
                "name": parameter.name,
                "label": parameter.label,
                "data_type": parameter.data_type,
                "required": parameter.required,
                "default": parameter.default,
                "description": parameter.description,
            }
            for parameter in self.parameters
        ]

    def __len__(self) -> int:
        return len(
            self.parameters
        )

    def __iter__(
        self,
    ) -> Iterator[ReportParameter]:
        return iter(
            self.parameters
        )

    def __contains__(
        self,
        name: str,
    ) -> bool:
        return self.has(
            name
        )


# ---------------------------------------------------------
# Report Definition
# ---------------------------------------------------------


@dataclass(frozen=True)
class ReportDefinition:
    """
    Represents the metadata and contract of a report.
    """

    code: str

    name: str

    description: str = ""

    module: str = ""

    version: str = "1.0.0"

    category: str = "General"

    parameters: Tuple[ReportParameter, ...] = ()

    metadata: dict[str, Any] = field(
        default_factory=dict
    )

    def __post_init__(self) -> None:
        """
        Validate the report definition.
        """

        if not isinstance(
            self.code,
            str,
        ):
            raise ValueError(
                "Report code must be a string."
            )

        if not self.code.strip():
            raise ValueError(
                "Report code is required."
            )

        if not isinstance(
            self.name,
            str,
        ):
            raise ValueError(
                "Report name must be a string."
            )

        if not self.name.strip():
            raise ValueError(
                "Report name is required."
            )

        if not isinstance(
            self.version,
            str,
        ):
            raise ValueError(
                "Report version must be a string."
            )

        if not self.version.strip():
            raise ValueError(
                "Report version is required."
            )

        if not isinstance(
            self.category,
            str,
        ):
            raise ValueError(
                "Report category must be a string."
            )

        if not self.category.strip():
            raise ValueError(
                "Report category is required."
            )

        for parameter in self.parameters:

            if not isinstance(
                parameter,
                ReportParameter,
            ):
                raise ValueError(
                    "Report definition parameters "
                    "must contain ReportParameter instances."
                )

    @property
    def identifier(self) -> str:
        """
        Return the canonical report identifier.
        """

        return self.code.upper()

    def to_dict(self) -> dict[str, Any]:
        """
        Serialize the report definition.
        """

        return {
            "code": self.code,
            "name": self.name,
            "description": self.description,
            "module": self.module,
            "version": self.version,
            "category": self.category,
            "parameters": [
                {
                    "name": parameter.name,
                    "label": parameter.label,
                    "data_type": parameter.data_type,
                    "required": parameter.required,
                    "default": parameter.default,
                    "description": parameter.description,
                }
                for parameter in self.parameters
            ],
            "metadata": dict(
                self.metadata
            ),
        }


__all__ = [
    "ReportParameter",
    "ReportParameterCollection",
    "ReportDefinition",
]
