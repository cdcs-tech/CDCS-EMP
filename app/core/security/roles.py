"""
CDCS Enterprise Management Platform (CDCS-EMP)

Enterprise Security Framework

Role definitions.
"""


from dataclasses import dataclass, field

from typing import Set

from app.core.security.permissions import Permission



@dataclass
class Role:
    """
    Represents an enterprise security role.

    Roles group permissions together
    and define access capabilities.
    """


    code: str

    name: str

    description: str = ""

    system_role: bool = False


    permissions: Set[
        Permission
    ] = field(
        default_factory=set
    )



    def __post_init__(self):
        """
        Validate role definition.
        """

        if not self.code:

            raise ValueError(
                "Role code is required."
            )


        if not self.name:

            raise ValueError(
                "Role name is required."
            )



    def add_permission(
        self,
        permission: Permission,
    ):
        """
        Add permission to role.
        """

        if not isinstance(
            permission,
            Permission,
        ):
            raise TypeError(
                "Only Permission objects can be added."
            )


        self.permissions.add(
            permission
        )



    def remove_permission(
        self,
        permission: Permission,
    ):
        """
        Remove permission from role.
        """

        self.permissions.discard(
            permission
        )



    def has_permission(
        self,
        code: str,
    ) -> bool:
        """
        Check whether role contains permission.
        """

        return any(
            permission.code == code
            for permission
            in self.permissions
        )



    def permission_codes(self):
        """
        Return permission codes.
        """

        return [
            permission.code
            for permission
            in self.permissions
        ]



    def __repr__(self):
        """
        Developer-friendly representation.
        """

        return (
            f"<Role "
            f"{self.code}>"
        )
