"""
CDCS Enterprise Management Platform (CDCS-EMP)

Enterprise Module Base Class

Provides the standard foundation that all
enterprise modules must inherit from.
"""


from abc import ABC, abstractmethod

from app.core.modules.metadata import ModuleMetadata


class BaseModule(ABC):
    """
    Abstract base class for CDCS-EMP modules.
    """


    def __init__(self):
        """
        Initialize module instance.
        """

        self.metadata = self.get_metadata()

        self.crud_config = (
            self.get_crud_config()
        )

        self.initialized = False


    @abstractmethod
    def get_metadata(self) -> ModuleMetadata:
        """
        Return module metadata.

        Every module must implement this.
        """

        raise NotImplementedError


    def get_crud_config(self):
        """
        Return optional CRUD configuration.

        Modules that expose CRUD entities
        can override this method.

        Non-CRUD modules return None.
        """

        return None


    def initialize(self, app):
        """
        Initialize module.

        This method is executed by the
        ModuleManager during application startup.
        """

        self.register_blueprints(app)

        self.register_services(app)

        self.register_repositories(app)

        self.register_crud(app)

        self.register_permissions(app)

        self.initialized = True


    def register_blueprints(self, app):
        """
        Register Flask blueprints.

        Modules override this method
        when they expose web routes.
        """

        return None


    def register_services(self, app):
        """
        Register application services.

        Reserved for future service layer integration.
        """

        return None


    def register_repositories(self, app):
        """
        Register data repositories.

        Reserved for future repository pattern integration.
        """

        return None


    def register_crud(self, app):
        """
        Register CRUD capabilities.

        Modules override this method when
        exposing CRUD functionality.
        """

        return None


    def register_permissions(self, app):
        """
        Register RBAC permissions.

        Reserved for future permission discovery.
        """

        return None


    def get_navigation(self):
        """
        Return module navigation definition.

        Modules can override this method.
        """

        return None


    def get_dashboard_widgets(self):
        """
        Return dashboard widgets.

        Modules can override this method.
        """

        return []


    def has_crud(self):
        """
        Check whether module exposes CRUD.
        """

        return (
            self.crud_config is not None
        )


    def is_active(self):
        """
        Check whether module is enabled.
        """

        return self.metadata.active


    def __repr__(self):
        """
        Developer-friendly representation.
        """

        return (
            f"<Module "
            f"{self.metadata.identifier} "
            f"v{self.metadata.version}>"
        )
