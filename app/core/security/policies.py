"""
CDCS Enterprise Management Platform (CDCS-EMP)

Enterprise Security Framework

Security policy definitions.
"""


from dataclasses import dataclass, field

from typing import Dict, Any



@dataclass
class SecurityPolicy:
    """
    Represents an enterprise security policy.

    Policies define governance rules that
    influence authorization decisions.
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
        Validate policy definition.
        """

        if not self.code:

            raise ValueError(
                "Policy code is required."
            )


        if not self.name:

            raise ValueError(
                "Policy name is required."
            )



    def disable(self):
        """
        Disable policy.
        """

        self.enabled = False



    def enable(self):
        """
        Enable policy.
        """

        self.enabled = True



    def is_active(self):
        """
        Check whether policy is active.
        """

        return self.enabled



    def __repr__(self):
        """
        Developer-friendly representation.
        """

        return (
            f"<SecurityPolicy "
            f"{self.code}>"
        )
