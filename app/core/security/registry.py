"""
CDCS Enterprise Management Platform (CDCS-EMP)

Enterprise Security Framework

Permission registry.
"""


from typing import Dict, List

from app.core.security.permissions import Permission


class PermissionRegistry:
    """
    Central registry for system permissions.
    """


    def __init__(self):
        """
        Initialize registry.
        """

        self._permissions: Dict[
            str,
            Permission
        ] = {}



    def register(
        self,
        permission: Permission,
    ):
        """
        Register a permission.
        """

        if not isinstance(
            permission,
            Permission,
        ):
            raise TypeError(
                "Only Permission objects can be registered."
            )


        self._permissions[
            permission.code
        ] = permission



    def get(
        self,
        code: str,
    ) -> Permission | None:
        """
        Retrieve permission by code.
        """

        return self._permissions.get(
            code
        )



    def exists(
        self,
        code: str,
    ) -> bool:
        """
        Check whether permission exists.
        """

        return (
            code
            in self._permissions
        )



    def all(self) -> List[Permission]:
        """
        Return all registered permissions.
        """

        return list(
            self._permissions.values()
        )



    def count(self) -> int:
        """
        Return permission count.
        """

        return len(
            self._permissions
        )



    def clear(self):
        """
        Remove all registered permissions.
        """

        self._permissions.clear()



    def __repr__(self):
        """
        Developer-friendly representation.
        """

        return (
            f"<PermissionRegistry "
            f"{self.count()} permissions>"
        )



# Global permission registry instance

permission_registry = PermissionRegistry()
