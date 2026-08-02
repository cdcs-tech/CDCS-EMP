"""
CDCS Enterprise Management Platform (CDCS-EMP)

Enterprise Module Dependency Validator

Validates module dependency requirements
before application startup.
"""


from typing import Dict, List, Set

from app.core.discovery import ModuleManifest


class ModuleDependencyValidator:
    """
    Validates dependencies between modules.
    """


    def __init__(
        self,
        manifests: List[ModuleManifest],
    ):
        """
        Initialize validator.

        Args:
            manifests:
                Discovered module manifests.
        """

        self.manifests = manifests

        self.module_map = {
            manifest.identifier: manifest
            for manifest in manifests
        }


    def validate(self):
        """
        Validate all module dependencies.

        Returns:
            True

        Raises:
            ValueError
        """

        for manifest in self.manifests:

            self._validate_dependencies(
                manifest,
                [],
            )

        return True


    def _validate_dependencies(
        self,
        manifest: ModuleManifest,
        chain: List[str],
    ):
        """
        Validate a single module dependency tree.
        """

        identifier = manifest.identifier

        if identifier in chain:

            dependency_chain = (
                " -> ".join(
                    chain + [identifier]
                )
            )

            raise ValueError(
                "Circular module dependency detected: "
                f"{dependency_chain}"
            )


        chain.append(
            identifier
        )


        for dependency in manifest.dependencies:

            dependency_code = (
                dependency.upper()
            )


            if dependency_code not in self.module_map:

                raise ValueError(
                    f"Module {identifier} requires "
                    f"missing module "
                    f"{dependency_code}"
                )


            dependency_module = (
                self.module_map[
                    dependency_code
                ]
            )


            if not dependency_module.enabled:

                raise ValueError(
                    f"Module {identifier} requires "
                    f"disabled module "
                    f"{dependency_code}"
                )


            self._validate_dependencies(
                dependency_module,
                chain.copy(),
            )


    def dependency_order(self):
        """
        Return modules in dependency order.

        Uses a simple topological ordering
        suitable for enterprise startup.
        """

        ordered = []

        visited: Set[str] = set()


        def visit(
            manifest: ModuleManifest,
        ):

            identifier = (
                manifest.identifier
            )

            if identifier in visited:
                return


            for dependency in (
                manifest.dependencies
            ):

                dependency_manifest = (
                    self.module_map[
                        dependency.upper()
                    ]
                )

                visit(
                    dependency_manifest
                )


            visited.add(
                identifier
            )

            ordered.append(
                manifest
            )


        for manifest in self.manifests:

            visit(
                manifest
            )


        return ordered
