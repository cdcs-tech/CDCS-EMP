"""
CDCS Enterprise Management Platform (CDCS-EMP)

Platform Infrastructure

Platform Governance Foundation.

Provides platform metadata, component
registration and governance validation.
"""

from dataclasses import dataclass, field
from typing import Any, Optional


@dataclass(frozen=True)
class PlatformComponent:
    """
    Describes a registered platform component.
    """

    name: str

    component_type: str

    version: str = "1.0.0"

    description: str = ""

    owner: str = "CDCS-EMP"

    metadata: dict[str, Any] = field(
        default_factory=dict
    )


class PlatformGovernance:
    """
    Central governance registry for
    platform components.
    """

    def __init__(self):

        self._components: dict[
            str,
            PlatformComponent,
        ] = {}

    def register(
        self,
        component: PlatformComponent,
        *,
        replace: bool = False,
    ) -> None:
        """
        Register a platform component.
        """

        if not component.name:
            raise ValueError(
                "Component name is required."
            )

        if not component.component_type:
            raise ValueError(
                "Component type is required."
            )

        if (
            component.name
            in self._components
            and not replace
        ):
            raise ValueError(
                f"Platform component "
                f"'{component.name}' "
                f"is already registered."
            )

        self._components[
            component.name
        ] = component

    def get(
        self,
        name: str,
    ) -> Optional[
        PlatformComponent
    ]:
        """
        Return a registered component.
        """

        return self._components.get(
            name
        )

    def has(
        self,
        name: str,
    ) -> bool:
        """
        Determine whether a component exists.
        """

        return name in self._components

    def all(
        self,
    ) -> list[PlatformComponent]:
        """
        Return all registered components.
        """

        return list(
            self._components.values()
        )

    def count(self) -> int:
        """
        Return component count.
        """

        return len(
            self._components
        )

    def validate(
        self,
    ) -> bool:
        """
        Validate the governance registry.
        """

        for component in (
            self._components.values()
        ):

            if not component.name:
                return False

            if not component.component_type:
                return False

            if not component.version:
                return False

        return True

    def clear(self) -> None:
        """
        Remove all registered components.
        """

        self._components.clear()

    def __repr__(self) -> str:
        """
        Developer-friendly representation.
        """

        return (
            f"<PlatformGovernance "
            f"{self.count()} components>"
        )


platform_governance = (
    PlatformGovernance()
)


__all__ = [
    "PlatformComponent",
    "PlatformGovernance",
    "platform_governance",
]
