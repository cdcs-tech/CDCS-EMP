"""
CDCS Enterprise Management Platform (CDCS-EMP)

Platform Infrastructure

Application Lifecycle.

Provides centralized orchestration for application
startup, readiness, request lifecycle, and shutdown.
"""

from __future__ import annotations

from enum import Enum
from typing import Any, Callable, Optional

from flask import (
    Flask,
    g,
    request,
)

from app.core.platform.context import (
    RequestContext,
)

from app.core.startup import (
    initialize_modules,
)

from app.core.services import (
    service_container,
)


class ApplicationLifecycleException(
    RuntimeError
):
    """
    Raised when an application lifecycle operation
    cannot be completed.
    """


class ApplicationLifecycleState(
    str,
    Enum,
):
    """
    Supported application lifecycle states.
    """

    CREATED = "created"
    STARTING = "starting"
    READY = "ready"
    STOPPING = "stopping"
    STOPPED = "stopped"
    FAILED = "failed"


class ApplicationLifecycle:
    """
    Coordinates the lifecycle of a CDCS-EMP application.

    The lifecycle delegates enterprise module startup
    to the existing startup framework while providing
    a single application-level lifecycle boundary.

    It also integrates the platform RequestContext with
    Flask's request lifecycle without making the
    RequestContext itself Flask-dependent.
    """

    EXTENSION_KEY = "application_lifecycle"

    REQUEST_CONTEXT_G_KEY = (
        "cdcs_request_context"
    )

    REQUEST_ID_HEADER = "X-Request-ID"

    CORRELATION_ID_HEADER = (
        "X-Correlation-ID"
    )

    TRACE_ID_HEADER = "X-Trace-ID"

    def __init__(
        self,
        module_initializer: Optional[
            Callable[[Flask], Any]
        ] = None,
    ) -> None:
        """
        Initialize the application lifecycle.

        Args:
            module_initializer:
                Callable responsible for initializing the
                Enterprise Module Framework.
        """

        self.module_initializer = (
            module_initializer
            or initialize_modules
        )

        self.state = (
            ApplicationLifecycleState.CREATED
        )

        self._module_manager: Any = None

        self._request_lifecycle_registered = False

    @property
    def is_ready(self) -> bool:
        """
        Determine whether the application is ready.
        """

        return (
            self.state
            == ApplicationLifecycleState.READY
        )

    @property
    def is_stopped(self) -> bool:
        """
        Determine whether the application has stopped.
        """

        return (
            self.state
            == ApplicationLifecycleState.STOPPED
        )

    @property
    def module_manager(self) -> Any:
        """
        Return the initialized module manager.
        """

        return self._module_manager

    @property
    def request_context(
        self,
    ) -> RequestContext | None:
        """
        Return the current request context.

        Returns:
            The active RequestContext when called during
            a Flask request, otherwise None.
        """

        try:
            return getattr(
                g,
                self.REQUEST_CONTEXT_G_KEY,
                None,
            )

        except RuntimeError:
            return None

    def start(
        self,
        app: Flask,
    ) -> Any:
        """
        Start the application lifecycle.

        The existing enterprise module startup pipeline
        remains the authoritative module initialization
        mechanism.

        Args:
            app:
                Flask application instance.

        Returns:
            Initialized module manager.

        Raises:
            ApplicationLifecycleException:
                When startup fails or an invalid lifecycle
                transition is requested.
        """

        self._validate_application(
            app
        )

        if self.state == (
            ApplicationLifecycleState.READY
        ):
            return self._module_manager

        if self.state == (
            ApplicationLifecycleState.STOPPED
        ):
            raise ApplicationLifecycleException(
                "A stopped application lifecycle "
                "cannot be started again."
            )

        if self.state == (
            ApplicationLifecycleState.STARTING
        ):
            raise ApplicationLifecycleException(
                "Application lifecycle startup "
                "is already in progress."
            )

        self.state = (
            ApplicationLifecycleState.STARTING
        )

        try:
            service_container.register_with_app(
                app
            )

            self._module_manager = (
                self.module_initializer(app)
            )

            self.register_request_lifecycle(
                app
            )

            app.extensions[
                self.EXTENSION_KEY
            ] = self

            self.state = (
                ApplicationLifecycleState.READY
            )

            return self._module_manager

        except Exception as exc:
            self.state = (
                ApplicationLifecycleState.FAILED
            )

            raise ApplicationLifecycleException(
                "Application startup failed."
            ) from exc

    def register_request_lifecycle(
        self,
        app: Flask,
    ) -> None:
        """
        Register Flask request lifecycle integration.

        The registration is idempotent for a given
        ApplicationLifecycle instance.

        The lifecycle creates a RequestContext before
        each request, exposes its identifiers on the
        response, and cleans request-local state during
        teardown.
        """

        self._validate_application(
            app
        )

        if self._request_lifecycle_registered:
            return

        @app.before_request
        def create_request_context():
            """
            Create the platform RequestContext.
            """

            context = (
                self._create_request_context()
            )

            setattr(
                g,
                self.REQUEST_CONTEXT_G_KEY,
                context,
            )

        @app.after_request
        def finalize_request_context(
            response,
        ):
            """
            Propagate request identity to the response.
            """

            context = self.request_context

            if context is None:
                return response

            response.headers[
                self.REQUEST_ID_HEADER
            ] = context.request_id

            response.headers[
                self.CORRELATION_ID_HEADER
            ] = context.correlation_id

            response.headers[
                self.TRACE_ID_HEADER
            ] = context.trace_id

            return response

        @app.teardown_request
        def teardown_request_context(
            exception,
        ):
            """
            Remove request-local platform context.

            The original request exception is deliberately
            not modified or suppressed.
            """

            try:
                if hasattr(
                    g,
                    self.REQUEST_CONTEXT_G_KEY,
                ):
                    delattr(
                        g,
                        self.REQUEST_CONTEXT_G_KEY,
                    )

            except RuntimeError:
                pass

        self._request_lifecycle_registered = True

    def get_request_context(
        self,
    ) -> RequestContext:
        """
        Return the active request context.

        Raises:
            ApplicationLifecycleException:
                When called outside an active request or
                when no RequestContext has been established.
        """

        context = self.request_context

        if context is None:
            raise ApplicationLifecycleException(
                "No active request context is available."
            )

        return context

    def _create_request_context(
        self,
    ) -> RequestContext:
        """
        Create a RequestContext for the current Flask
        request.

        Only infrastructure-level HTTP metadata is
        established here. Business, tenant, organization,
        module, operation, resource, and authorization
        resolution remain outside the application lifecycle.
        """

        user_id = None
        username = None

        try:
            from flask_login import (
                current_user,
            )

            if current_user.is_authenticated:
                user_id = str(
                    current_user.id
                )

                username = (
                    current_user.username
                )

        except (
            ImportError,
            AttributeError,
            RuntimeError,
        ):
            pass

        metadata = {
            "http_method": request.method,
            "path": request.path,
            "endpoint": request.endpoint,
            "remote_addr": request.remote_addr,
            "user_agent": (
                request.user_agent.string
                if request.user_agent
                else None
            ),
        }

        return RequestContext(
            user_id=user_id,
            username=username,
            source="web",
            metadata=metadata,
        )

    @classmethod
    def from_app(
        cls,
        app: Flask,
    ) -> "ApplicationLifecycle":
        """
        Retrieve the lifecycle associated with an application.

        Args:
            app:
                Flask application instance.

        Returns:
            ApplicationLifecycle instance.

        Raises:
            ApplicationLifecycleException:
                When no lifecycle is registered.
        """

        lifecycle = app.extensions.get(
            cls.EXTENSION_KEY
        )

        if lifecycle is None:
            raise ApplicationLifecycleException(
                "Application lifecycle is not registered."
            )

        if not isinstance(
            lifecycle,
            cls,
        ):
            raise ApplicationLifecycleException(
                "Registered application lifecycle "
                "has an invalid type."
            )

        return lifecycle

    @staticmethod
    def _validate_application(
        app: Flask,
    ) -> None:
        """
        Validate the Flask application instance.
        """

        if not isinstance(
            app,
            Flask,
        ):
            raise ApplicationLifecycleException(
                "A Flask application instance is required."
            )

    def shutdown(
        self,
        app: Flask,
    ) -> None:
        """
        Shut down the application lifecycle.

        Shutdown is intentionally explicit. It does not
        use Flask application-context teardown because
        application-context teardown is not equivalent
        to application shutdown.

        Application-scoped enterprise services are cleared
        from the shared service container so that a subsequent
        application instance can initialize cleanly.

        Args:
            app:
                Flask application instance.

        Raises:
            ApplicationLifecycleException:
                When shutdown cannot be performed.
        """

        self._validate_application(
            app
        )

        if self.state == (
            ApplicationLifecycleState.STOPPED
        ):
            return

        if self.state not in (
            ApplicationLifecycleState.READY,
            ApplicationLifecycleState.FAILED,
        ):
            raise ApplicationLifecycleException(
                "Application lifecycle is not "
                "in a state that can be stopped."
            )

        self.state = (
            ApplicationLifecycleState.STOPPING
        )

        try:
            service_container.clear()

            self._module_manager = None

            self.state = (
                ApplicationLifecycleState.STOPPED
            )

        except Exception as exc:
            self.state = (
                ApplicationLifecycleState.FAILED
            )

            raise ApplicationLifecycleException(
                "Application shutdown failed."
            ) from exc

    def __repr__(
        self,
    ) -> str:
        """
        Developer-friendly representation.
        """

        return (
            f"<ApplicationLifecycle "
            f"state={self.state.value!r}>"
        )


application_lifecycle = (
    ApplicationLifecycle()
)


__all__ = [
    "ApplicationLifecycleException",
    "ApplicationLifecycleState",
    "ApplicationLifecycle",
    "application_lifecycle",
]
