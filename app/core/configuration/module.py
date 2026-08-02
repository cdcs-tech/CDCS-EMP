"""
CDCS Enterprise Management Platform (CDCS-EMP)

Enterprise Module Configuration

Defines runtime configuration structure
for enterprise modules.
"""


from dataclasses import dataclass, field

from typing import Any, Dict


@dataclass
class ModuleConfiguration:
    """
    Represents configuration settings
    for an enterprise module.
    """

    module_code: str

    enabled: bool = True

    settings: Dict[str, Any] = field(
        default_factory=dict
    )


    def get(
        self,
        key: str,
        default=None,
    ):
        """
        Retrieve configuration value.

        Args:
            key:
                Configuration key.

            default:
                Value returned if key
                does not exist.
        """

        return self.settings.get(
            key,
            default,
        )


    def set(
        self,
        key: str,
        value: Any,
    ):
        """
        Update configuration value.
        """

        self.settings[key] = value


    def update(
        self,
        values: Dict[str, Any],
    ):
        """
        Update multiple settings.
        """

        self.settings.update(
            values
        )


    def has(
        self,
        key: str,
    ):
        """
        Check whether a configuration
        key exists.
        """

        return key in self.settings


    def to_dict(self):
        """
        Convert configuration into
        dictionary format.
        """

        return {

            "module_code": self.module_code,

            "enabled": self.enabled,

            "settings": self.settings,

        }
