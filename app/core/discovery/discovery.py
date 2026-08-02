"""
CDCS Enterprise Management Platform (CDCS-EMP)

Enterprise Module Discovery Engine

Discovers and loads module manifests.
"""


import importlib
import os

from typing import List

from app.core.discovery import ModuleManifest


class ModuleDiscovery:
    """
    Discovers enterprise modules.
    """


    def __init__(
        self,
        module_path="app.modules",
    ):
        """
        Initialize discovery engine.

        Args:
            module_path:
                Python package containing modules.
        """

        self.module_path = module_path


    def discover(
        self,
    ) -> List[ModuleManifest]:
        """
        Discover all available modules.

        Returns:
            List of ModuleManifest objects.
        """

        manifests = []

        for package in self._find_packages():

            manifest = self._load_manifest(
                package
            )

            if manifest:

                manifest.validate()

                if manifest.enabled:

                    manifests.append(
                        manifest
                    )

        return manifests


    def _find_packages(self):
        """
        Locate module packages.

        """

        packages = []

        try:

            module = importlib.import_module(
                self.module_path
            )

            module_directory = os.path.dirname(
                module.__file__
            )


            for item in os.listdir(
                module_directory
            ):

                path = os.path.join(
                    module_directory,
                    item,
                )

                if (
                    os.path.isdir(path)
                    and item != "__pycache__"
                    and not item.startswith("_")
                ):

                    packages.append(
                        f"{self.module_path}.{item}"
                    )

        except ModuleNotFoundError:

            return []


        return packages


    def _load_manifest(
        self,
        package,
    ):
        """
        Load manifest from module package.
        """

        try:

            manifest_module = importlib.import_module(
                f"{package}.manifest"
            )

            return getattr(
                manifest_module,
                "MODULE_MANIFEST",
                None,
            )

        except ModuleNotFoundError:

            return None
