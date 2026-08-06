"""
CDCS Enterprise Management Platform (CDCS-EMP)

Enterprise Security Framework

Role registry.
"""


from typing import Dict, List

from app.core.security.roles import Role



class RoleRegistry:
    """
    Central registry for enterprise roles.
    """



    def __init__(self):
        """
        Initialize role registry.
        """

        self._roles: Dict[
            str,
            Role
        ] = {}



    def register(
        self,
        role: Role,
    ):
        """
        Register a role.
        """

        if not isinstance(
            role,
            Role,
        ):
            raise TypeError(
                "Only Role objects can be registered."
            )


        self._roles[
            role.code
        ] = role



    def get(
        self,
        code: str,
    ) -> Role | None:
        """
        Retrieve role by code.
        """

        return self._roles.get(
            code
        )



    def exists(
        self,
        code: str,
    ) -> bool:
        """
        Check whether role exists.
        """

        return (
            code
            in self._roles
        )



    def all(self) -> List[Role]:
        """
        Return all registered roles.
        """

        return list(
            self._roles.values()
        )



    def count(self) -> int:
        """
        Return number of registered roles.
        """

        return len(
            self._roles
        )



    def clear(self):
        """
        Remove all roles.
        """

        self._roles.clear()



    def __repr__(self):
        """
        Developer-friendly representation.
        """

        return (
            f"<RoleRegistry "
            f"{self.count()} roles>"
        )



# Global role registry instance

role_registry = RoleRegistry()
