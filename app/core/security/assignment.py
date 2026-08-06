"""
CDCS Enterprise Management Platform (CDCS-EMP)

Enterprise Security Framework

Role permission assignment framework.
"""


from app.core.security.roles import Role

from app.core.security.permissions import Permission



class RolePermissionAssignment:
    """
    Manages role-permission relationships.
    """



    def __init__(
        self,
        role: Role,
    ):
        """
        Initialize assignment manager.
        """

        if not isinstance(
            role,
            Role,
        ):
            raise TypeError(
                "Assignment requires a Role object."
            )


        self.role = role



    def assign(
        self,
        permission: Permission,
    ):
        """
        Assign permission to role.
        """

        if not isinstance(
            permission,
            Permission,
        ):
            raise TypeError(
                "Only Permission objects can be assigned."
            )


        self.role.add_permission(
            permission
        )



    def remove(
        self,
        permission: Permission,
    ):
        """
        Remove permission from role.
        """

        self.role.remove_permission(
            permission
        )



    def has_permission(
        self,
        code: str,
    ) -> bool:
        """
        Check role permission.
        """

        return self.role.has_permission(
            code
        )



    def permissions(self):
        """
        Return assigned permissions.
        """

        return self.role.permissions



    def __repr__(self):
        """
        Developer-friendly representation.
        """

        return (
            f"<RolePermissionAssignment "
            f"{self.role.code}>"
        )
