"""
CDCS Enterprise Management Platform (CDCS-EMP)

Enterprise Module Loader

Creates module instances from validated
module manifests and registers them with
the Module Manager.
"""

from typing import Iterable, List

from app.core.discovery.manifest import ModuleManifest
from app.core.modules import BaseModule, ModuleManager


class ModuleLoader:
    """
    Loads validated enterprise modules into
    the Module Manager.
    """

    def __init__(self, manager: ModuleManager):
        """
        Initialize the module loader.

        Args:
            manager:
                Target ModuleManager instance.
        """
        self.manager = manager

    def load(
        self,
        manifests: Iterable[ModuleManifest],
    ) -> List[BaseModule]:
        """
        Load and register modules.

        Args:
            manifests:
                Validated module manifests.

        Returns:
            List of registered module instances.
        """

        loaded_modules: List[BaseModule] = []

        for manifest in manifests:

            module = manifest.create_module()

            self.manager.register_module(module)

            loaded_modules.append(module)

        return loaded_modules
