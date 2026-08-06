"""
CDCS Enterprise Management Platform (CDCS-EMP)

Enterprise Security Framework

Compliance control registry.
"""

from app.core.security.compliance import (
    ComplianceControl,
)


class ComplianceRegistry:
    """
    Central registry for compliance controls.
    """

    def __init__(self):
        """
        Initialize registry.
        """

        self._controls = {}

    def register(
        self,
        control: ComplianceControl,
    ):
        """
        Register a compliance control.
        """

        if not isinstance(
            control,
            ComplianceControl,
        ):
            raise TypeError(
                "Expected ComplianceControl."
            )

        self._controls[
            control.code
        ] = control

    def get(
        self,
        code: str,
    ):
        """
        Return a compliance control.
        """

        return self._controls.get(
            code
        )

    def exists(
        self,
        code: str,
    ) -> bool:
        """
        Check whether a control exists.
        """

        return (
            code in self._controls
        )

    def all(self):
        """
        Return all controls.
        """

        return list(
            self._controls.values()
        )

    def count(self) -> int:
        """
        Return total controls.
        """

        return len(
            self._controls
        )

    def clear(self):
        """
        Remove all controls.
        """

        self._controls.clear()

    def __repr__(self):
        """
        Developer-friendly representation.
        """

        return (
            f"<ComplianceRegistry "
            f"{self.count()} controls>"
        )


# Global compliance registry

compliance_registry = ComplianceRegistry()
