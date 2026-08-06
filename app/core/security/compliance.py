"""
CDCS Enterprise Management Platform (CDCS-EMP)

Enterprise Security Framework

Security compliance definitions.
"""


from dataclasses import dataclass, field

from typing import Dict, Any



@dataclass
class ComplianceControl:
    """
    Represents a security compliance control.

    Compliance controls define governance
    requirements that can be evaluated
    across the platform.
    """

    code: str

    name: str

    description: str = ""

    category: str = "general"

    enabled: bool = True

    metadata: Dict[
        str,
        Any
    ] = field(
        default_factory=dict
    )



    def __post_init__(self):
        """
        Validate compliance control.
        """

        if not self.code:

            raise ValueError(
                "Compliance control code is required."
            )


        if not self.name:

            raise ValueError(
                "Compliance control name is required."
            )



    def enable(self):
        """
        Enable compliance control.
        """

        self.enabled = True



    def disable(self):
        """
        Disable compliance control.
        """

        self.enabled = False



    def is_active(self):
        """
        Check whether control is active.
        """

        return self.enabled



    def __repr__(self):
        """
        Developer-friendly representation.
        """

        return (
            f"<ComplianceControl "
            f"{self.code}>"
        )
