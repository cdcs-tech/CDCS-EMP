"""
CDCS Enterprise Management Platform (CDCS-EMP)

Enterprise Module Base Class

Provides the standard foundation that all
enterprise modules must inherit from.
"""

from abc import ABC, abstractmethod

from app.core.modules.metadata import ModuleMetadata

from app.core.services import (
    ServiceDefinition,
    service_registry,
    service_container,
)

from app.core.validation import (
    BaseValidator,
)

from app.core.workflow import (
    WorkflowDefinition,
    workflow_registry,
)

from app.core.security import (
    Permission,
    permission_registry,
)

from app.core.events import (
    BaseEvent,
    BaseEventHandler,
    event_registry,
)


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

        self.services = (
            self.get_service_definitions()
        )

        self.validators = (
            self.get_validators()
        )

        self.workflows = (
            self.get_workflows()
        )

        self.permissions = (
            self.get_permissions()
        )

        self.events = (
            self.get_events()
        )

        self.event_handlers = (
            self.get_event_handlers()
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

    def get_service_definitions(self):
        """
        Return optional service definitions.

        Modules override this method when
        they expose business services.
        """

        return []

    def get_validators(self):
        """
        Return module validators.

        Modules override this method to expose
        enterprise validation logic.
        """

        return []

    def get_workflows(self):
        """
        Return module workflow definitions.

        Modules override this method to expose
        enterprise workflows.
        """

        return []

    def get_permissions(self):
        """
        Return module permissions.

        Modules override this method to expose
        enterprise security permissions.
        """

        return []

    def get_events(self):
        """
        Return module event definitions.

        Modules override this method to expose
        enterprise domain events.
        """

        return []

    def get_event_handlers(self):
        """
        Return module event handlers.

        Modules override this method to expose
        handlers for enterprise domain events.

        Expected format:

            [
                (EventClass, HandlerInstance),
            ]
        """

        return []

    def register_models(self, app):
        """
        Register module models.

        Modules override this method when
        they expose SQLAlchemy models.
        """

        return None

    def initialize(self, app):
        """
        Initialize module.

        This method is executed by the
        ModuleManager during application startup.
        """

        self.register_models(app)

        self.register_blueprints(app)

        self.register_services(app)

        self.register_validation(app)

        self.register_workflows(app)

        self.register_repositories(app)

        self.register_crud(app)

        self.register_permissions(app)

        self.register_events(app)

        self.register_event_handlers(app)

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

        Services are registered into:
        - Service Registry
        - Dependency Container
        """

        for service_definition in self.services:

            if not isinstance(
                service_definition,
                ServiceDefinition,
            ):
                continue

            service_registry.register(
                service_definition
            )

            if service_definition.instance:

                service_container.register(
                    (
                        f"{service_definition.module_name}."
                        f"{service_definition.service_name}"
                    ),
                    service_definition.instance,
                )

    def register_validation(self, app):
        """
        Register module validators.

        Reserved for enterprise validation
        integration.
        """

        for validator in self.validators:

            if not isinstance(
                validator,
                BaseValidator,
            ):
                continue

        return None

    def register_workflows(self, app):
        """
        Register enterprise workflows.
        """

        for workflow in self.workflows:

            if not isinstance(
                workflow,
                WorkflowDefinition,
            ):
                continue

            workflow_registry.register(
                workflow
            )

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
        Register module permissions.

        Permissions are registered into the
        global permission registry.
        """

        for permission in self.permissions:

            if not isinstance(
                permission,
                Permission,
            ):
                continue

            permission_registry.register(
                permission
            )

        return None

    def register_events(self, app):
        """
        Register module event definitions.

        Events are registered into the
        global event registry.
        """

        for event in self.events:

            if not isinstance(
                event,
                type,
            ):
                continue

            if not issubclass(
                event,
                BaseEvent,
            ):
                continue

            event_registry.register(
                event
            )

        return None

    def register_event_handlers(self, app):
        """
        Register module event handlers.

        Handlers are registered into the
        global event registry.

        Expected format:

            [
                (EventClass, HandlerInstance),
            ]
        """

        for event_class, handler in (
            self.event_handlers
        ):

            if not isinstance(
                event_class,
                type,
            ):
                continue

            if not issubclass(
                event_class,
                BaseEvent,
            ):
                continue

            if not isinstance(
                handler,
                BaseEventHandler,
            ):
                continue

            event_registry.register_handler(
                event_class,
                handler,
            )

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

    def has_services(self):
        """
        Check whether module exposes services.
        """

        return bool(
            self.services
        )

    def has_validators(self):
        """
        Check whether module exposes validators.
        """

        return bool(
            self.validators
        )

    def has_workflows(self):
        """
        Check whether module exposes workflows.
        """

        return bool(
            self.workflows
        )

    def has_permissions(self):
        """
        Check whether module exposes permissions.
        """

        return bool(
            self.permissions
        )

    def has_events(self):
        """
        Check whether module exposes events.
        """

        return bool(
            self.events
        )

    def has_event_handlers(self):
        """
        Check whether module exposes event handlers.
        """

        return bool(
            self.event_handlers
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

