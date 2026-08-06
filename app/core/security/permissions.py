"""
CDCS Enterprise Management Platform (CDCS-EMP)

Enterprise Security Framework

Permission definitions.
"""


from dataclasses import dataclass


@dataclass(frozen=True)
class Permission:
    """
    Represents a system permission.

    Permissions define what actions
    users can perform within modules.
    """

    code: str

    name: str

    description: str = ""

    module: str = ""

    resource: str = ""

    action: str = ""


    def __post_init__(self):
        """
        Validate permission definition.
        """

        if not self.code:

            raise ValueError(
                "Permission code is required."
            )


    def __repr__(self):
        """
        Developer-friendly representation.
        """

        return (
            f"<Permission "
            f"{self.code}>"
        )
