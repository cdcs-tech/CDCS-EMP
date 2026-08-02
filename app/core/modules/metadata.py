"""
CDCS Enterprise Management Platform (CDCS-EMP)

Enterprise Module Metadata

Defines the standard metadata structure
used by all platform modules.
"""


from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class ModuleMetadata:
    """
    Defines the identity and configuration
    information of an enterprise module.
    """

    code: str

    name: str

    description: str = ""

    version: str = "1.0.0"

    author: str = "CDCS"

    category: str = "Business"

    icon: str = "bi-grid"

    url_prefix: Optional[str] = None

    dependencies: List[str] = field(
        default_factory=list
    )

    permissions: List[str] = field(
        default_factory=list
    )

    navigation_enabled: bool = True

    dashboard_enabled: bool = False

    active: bool = True


    def validate(self):
        """
        Validate module metadata.

        Raises:
            ValueError:
                When required metadata is missing.
        """

        if not self.code:
            raise ValueError(
                "Module code is required."
            )

        if not self.name:
            raise ValueError(
                "Module name is required."
            )

        if " " in self.code:
            raise ValueError(
                "Module code cannot contain spaces."
            )

        return True


    @property
    def identifier(self):
        """
        Unique module identifier.
        """

        return self.code.upper()


    def to_dict(self):
        """
        Convert metadata into dictionary form.

        Useful for:
        - API responses
        - Logging
        - Dashboard registration
        - Administrative screens
        """

        return {
            "code": self.code,
            "name": self.name,
            "description": self.description,
            "version": self.version,
            "author": self.author,
            "category": self.category,
            "icon": self.icon,
            "url_prefix": self.url_prefix,
            "dependencies": self.dependencies,
            "permissions": self.permissions,
            "navigation_enabled": (
                self.navigation_enabled
            ),
            "dashboard_enabled": (
                self.dashboard_enabled
            ),
            "active": self.active,
        }
