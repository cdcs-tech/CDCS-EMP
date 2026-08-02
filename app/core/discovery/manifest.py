"""
CDCS Enterprise Management Platform (CDCS-EMP)

Enterprise Module Manifest

Defines the standard declaration format
for discoverable platform modules.
"""


from dataclasses import dataclass, field
from typing import Dict, List, Optional, Type

from app.core.modules import BaseModule


@dataclass
class ModuleManifest:
    """
    Defines a module discovery manifest.
    """

    name: str

    code: str

    module_class: Type[BaseModule]

    version: str = "1.0.0"

    description: str = ""

    author: str = "CDCS"

    dependencies: List[str] = field(
        default_factory=list
    )

    enabled: bool = True

    configuration: Dict = field(
        default_factory=dict
    )


    def validate(self):
        """
        Validate manifest definition.

        Returns:
            bool

        Raises:
            ValueError
        """

        if not self.name:
            raise ValueError(
                "Module name is required."
            )

        if not self.code:
            raise ValueError(
                "Module code is required."
            )

        if not isinstance(
            self.module_class,
            type,
        ):
            raise ValueError(
                "module_class must be a class."
            )

        if not issubclass(
            self.module_class,
            BaseModule,
        ):
            raise ValueError(
                "module_class must inherit "
                "from BaseModule."
            )

        return True


    @property
    def identifier(self):
        """
        Return normalized module identifier.
        """

        return self.code.upper()


    def create_module(self) -> BaseModule:
        """
        Create module instance from manifest.
        """

        return self.module_class()


    def to_dict(self):
        """
        Convert manifest information
        into dictionary format.
        """

        return {

            "name": self.name,

            "code": self.code,

            "version": self.version,

            "description": self.description,

            "author": self.author,

            "dependencies": self.dependencies,

            "enabled": self.enabled,

            "configuration": self.configuration,

        }
