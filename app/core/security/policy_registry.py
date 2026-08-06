"""
CDCS Enterprise Management Platform (CDCS-EMP)

Enterprise Security Framework

Security policy registry.
"""


from typing import Dict, List

from app.core.security.policies import (
    SecurityPolicy,
)



class PolicyRegistry:
    """
    Central registry for security policies.
    """



    def __init__(self):
        """
        Initialize policy registry.
        """

        self._policies: Dict[
            str,
            SecurityPolicy
        ] = {}



    def register(
        self,
        policy: SecurityPolicy,
    ):
        """
        Register a security policy.
        """

        if not isinstance(
            policy,
            SecurityPolicy,
        ):
            raise TypeError(
                "Only SecurityPolicy objects can be registered."
            )


        self._policies[
            policy.code
        ] = policy



    def get(
        self,
        code: str,
    ) -> SecurityPolicy | None:
        """
        Retrieve policy by code.
        """

        return self._policies.get(
            code
        )



    def exists(
        self,
        code: str,
    ) -> bool:
        """
        Check whether policy exists.
        """

        return (
            code
            in self._policies
        )



    def all(self) -> List[SecurityPolicy]:
        """
        Return all policies.
        """

        return list(
            self._policies.values()
        )



    def active(self) -> List[SecurityPolicy]:
        """
        Return enabled policies.
        """

        return [
            policy
            for policy
            in self._policies.values()
            if policy.is_active()
        ]



    def count(self) -> int:
        """
        Return policy count.
        """

        return len(
            self._policies
        )



    def clear(self):
        """
        Remove all policies.
        """

        self._policies.clear()



    def __repr__(self):
        """
        Developer-friendly representation.
        """

        return (
            f"<PolicyRegistry "
            f"{self.count()} policies>"
        )



# Global policy registry instance

policy_registry = PolicyRegistry()
