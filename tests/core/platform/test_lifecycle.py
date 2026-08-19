"""
CDCS Enterprise Management Platform (CDCS-EMP)

Platform Infrastructure Tests

Application lifecycle tests.
"""

import pytest
from flask import Flask

from app.core.platform import (
    ApplicationLifecycle,
    ApplicationLifecycleException,
    ApplicationLifecycleState,
    RequestContext,
)


class ExampleModuleManager:
    """
    Test module manager.
    """


def create_application():
    return Flask(
        "test_application"
    )


def test_lifecycle_initial_state():

    lifecycle = ApplicationLifecycle()

    assert (
        lifecycle.state
        == ApplicationLifecycleState.CREATED
    )

    assert lifecycle.is_ready is False
    assert lifecycle.is_stopped is False


def test_lifecycle_start():

    app = create_application()

    manager = ExampleModuleManager()

    def initializer(application):

        assert application is app

        return manager

    lifecycle = ApplicationLifecycle(
        module_initializer=initializer
    )

    result = lifecycle.start(
        app
    )

    assert result is manager

    assert (
        lifecycle.state
        == ApplicationLifecycleState.READY
    )

    assert lifecycle.is_ready is True

    assert (
        lifecycle.module_manager
        is manager
    )


def test_lifecycle_registers_on_application():

    app = create_application()

    lifecycle = ApplicationLifecycle(
        module_initializer=lambda _: None
    )

    lifecycle.start(
        app
    )

    assert (
        app.extensions[
            "application_lifecycle"
        ]
        is lifecycle
    )


def test_lifecycle_can_be_resolved_from_application():

    app = create_application()

    lifecycle = ApplicationLifecycle(
        module_initializer=lambda _: None
    )

    lifecycle.start(
        app
    )

    resolved = (
        ApplicationLifecycle.from_app(
            app
        )
    )

    assert resolved is lifecycle


def test_missing_application_lifecycle_fails():

    app = create_application()

    with pytest.raises(
        ApplicationLifecycleException
    ):

        ApplicationLifecycle.from_app(
            app
        )


def test_startup_failure_changes_state():

    app = create_application()

    def initializer(_):

        raise RuntimeError(
            "startup failure"
        )

    lifecycle = ApplicationLifecycle(
        module_initializer=initializer
    )

    with pytest.raises(
        ApplicationLifecycleException
    ):

        lifecycle.start(
            app
        )

    assert (
        lifecycle.state
        == ApplicationLifecycleState.FAILED
    )


def test_start_is_idempotent_when_ready():

    app = create_application()

    calls = []

    manager = ExampleModuleManager()

    def initializer(_):

        calls.append(
            "initialized"
        )

        return manager

    lifecycle = ApplicationLifecycle(
        module_initializer=initializer
    )

    first = lifecycle.start(
        app
    )

    second = lifecycle.start(
        app
    )

    assert first is manager
    assert second is manager

    assert calls == [
        "initialized"
    ]


def test_starting_lifecycle_cannot_be_started_again():

    app = create_application()

    lifecycle = ApplicationLifecycle(
        module_initializer=lambda _: None
    )

    lifecycle.state = (
        ApplicationLifecycleState.STARTING
    )

    with pytest.raises(
        ApplicationLifecycleException
    ):

        lifecycle.start(
            app
        )


def test_shutdown():

    app = create_application()

    manager = ExampleModuleManager()

    lifecycle = ApplicationLifecycle(
        module_initializer=lambda _: manager
    )

    lifecycle.start(
        app
    )

    lifecycle.shutdown(
        app
    )

    assert (
        lifecycle.state
        == ApplicationLifecycleState.STOPPED
    )

    assert lifecycle.is_stopped is True
    assert lifecycle.module_manager is None


def test_shutdown_is_idempotent():

    app = create_application()

    lifecycle = ApplicationLifecycle(
        module_initializer=lambda _: None
    )

    lifecycle.start(
        app
    )

    lifecycle.shutdown(
        app
    )

    lifecycle.shutdown(
        app
    )

    assert (
        lifecycle.state
        == ApplicationLifecycleState.STOPPED
    )


def test_stopped_lifecycle_cannot_restart():

    app = create_application()

    lifecycle = ApplicationLifecycle(
        module_initializer=lambda _: None
    )

    lifecycle.start(
        app
    )

    lifecycle.shutdown(
        app
    )

    with pytest.raises(
        ApplicationLifecycleException
    ):

        lifecycle.start(
            app
        )

def test_shutdown_clears_service_container():

    from app.core.services import (
        ServiceContainer,
    )

    app = create_application()

    lifecycle = ApplicationLifecycle(
        module_initializer=lambda _: None
    )

    lifecycle.start(
        app
    )

    container = (
        ServiceContainer.from_app(
            app
        )
    )

    container.register(
        "test_service",
        object(),
    )

    assert container.has(
        "test_service"
    )

    lifecycle.shutdown(
        app
    )

    assert container.count() == 0


def test_invalid_application_fails():

    lifecycle = ApplicationLifecycle()

    with pytest.raises(
        ApplicationLifecycleException
    ):

        lifecycle.start(
            None
        )


def test_lifecycle_representation():

    lifecycle = ApplicationLifecycle()

    representation = repr(
        lifecycle
    )

    assert (
        "ApplicationLifecycle"
        in representation
    )

    assert (
        "created"
        in representation
    )


def test_lifecycle_registers_service_container():

    from app.core.services import (
        ServiceContainer,
    )

    app = create_application()

    lifecycle = ApplicationLifecycle(
        module_initializer=lambda _: None
    )

    lifecycle.start(
        app
    )

    container = (
        ServiceContainer.from_app(
            app
        )
    )

    assert container is not None

    assert (
        app.extensions[
            "service_container"
        ]
        is container
    )


# ---------------------------------------------------------
# Request Lifecycle Integration
# ---------------------------------------------------------


def test_request_context_created_before_request():

    app = Flask(
    __name__
    )

    app.testing = True

    lifecycle = ApplicationLifecycle(
        module_initializer=lambda app: None
    )

    lifecycle.register_request_lifecycle(
        app
    )

    @app.route("/context")
    def context_route():

        context = lifecycle.get_request_context()

        assert isinstance(
            context,
            RequestContext,
        )

        return "ok"

    client = app.test_client()

    response = client.get(
        "/context"
    )

    assert response.status_code == 200


def test_request_context_has_request_identity():

    app = Flask(
        __name__
    )

    lifecycle = ApplicationLifecycle(
        module_initializer=lambda app: None
    )

    lifecycle.register_request_lifecycle(
        app
    )

    captured = {}

    @app.route("/identity")
    def identity_route():

        context = (
            lifecycle.get_request_context()
        )

        captured[
            "request_id"
        ] = context.request_id

        captured[
            "correlation_id"
        ] = context.correlation_id

        captured[
            "trace_id"
        ] = context.trace_id

        return "ok"

    client = app.test_client()

    response = client.get(
        "/identity"
    )

    assert response.status_code == 200

    assert captured[
        "request_id"
    ]

    assert captured[
        "correlation_id"
    ]

    assert captured[
        "trace_id"
    ]


def test_request_identity_headers_are_added():

    app = Flask(
        __name__
    )

    lifecycle = ApplicationLifecycle(
        module_initializer=lambda app: None
    )

    lifecycle.register_request_lifecycle(
        app
    )

    captured = {}

    @app.route("/headers")
    def headers_route():

        context = (
            lifecycle.get_request_context()
        )

        captured[
            "request_id"
        ] = context.request_id

        captured[
            "correlation_id"
        ] = context.correlation_id

        captured[
            "trace_id"
        ] = context.trace_id

        return "ok"

    client = app.test_client()

    response = client.get(
        "/headers"
    )

    assert (
        response.headers["X-Request-ID"]
        == captured["request_id"]
    )

    assert (
        response.headers["X-Correlation-ID"]
        == captured["correlation_id"]
    )

    assert (
        response.headers["X-Trace-ID"]
        == captured["trace_id"]
    )


def test_request_context_contains_http_metadata():

    app = Flask(
        __name__
    )

    lifecycle = ApplicationLifecycle(
        module_initializer=lambda app: None
    )

    lifecycle.register_request_lifecycle(
        app
    )

    @app.route("/metadata")
    def metadata_route():

        context = (
            lifecycle.get_request_context()
        )

        assert (
            context.metadata["http_method"]
            == "GET"
        )

        assert (
            context.metadata["path"]
            == "/metadata"
        )

        assert (
            context.metadata["endpoint"]
            == "metadata_route"
        )

        assert (
            context.source
            == "web"
        )

        return "ok"

    client = app.test_client()

    response = client.get(
        "/metadata"
    )

    assert response.status_code == 200


def test_each_request_receives_independent_context():

    app = Flask(
        __name__
    )

    lifecycle = ApplicationLifecycle(
        module_initializer=lambda app: None
    )

    lifecycle.register_request_lifecycle(
        app
    )

    request_ids = []

    @app.route("/isolated")
    def isolated_route():

        request_ids.append(
            lifecycle.get_request_context().request_id
        )

        return "ok"

    client = app.test_client()

    client.get(
        "/isolated"
    )

    client.get(
        "/isolated"
    )

    assert len(
        request_ids
    ) == 2

    assert (
        request_ids[0]
        != request_ids[1]
    )


def test_request_context_is_cleaned_up():

    app = Flask(
        __name__
    )

    lifecycle = ApplicationLifecycle(
        module_initializer=lambda app: None
    )

    lifecycle.register_request_lifecycle(
        app
    )

    @app.route("/cleanup")
    def cleanup_route():

        assert (
            lifecycle.request_context
            is not None
        )

        return "ok"

    client = app.test_client()

    with client:

        response = client.get(
            "/cleanup"
        )

        assert response.status_code == 200

    with app.test_request_context():

        assert (
            lifecycle.request_context
            is None
        )


def test_request_context_cleanup_after_exception():

    app = Flask(
        __name__
    )

    lifecycle = ApplicationLifecycle(
        module_initializer=lambda app: None
    )

    lifecycle.register_request_lifecycle(
        app
    )

    @app.route("/failure")
    def failure_route():

        raise RuntimeError(
            "expected failure"
        )

    client = app.test_client()

    response = client.get(
        "/failure"
    )

    assert response.status_code == 500

    with app.test_request_context():

        assert (
            lifecycle.request_context
            is None
        )


def test_request_lifecycle_registration_is_idempotent():

    app = Flask(
        __name__
    )

    lifecycle = ApplicationLifecycle(
        module_initializer=lambda app: None
    )

    lifecycle.register_request_lifecycle(
        app
    )

    lifecycle.register_request_lifecycle(
        app
    )

    assert (
        lifecycle._request_lifecycle_registered
        is True
    )


def test_request_context_accessor_requires_active_context():

    app = Flask(
        __name__
    )

    lifecycle = ApplicationLifecycle(
        module_initializer=lambda app: None
    )

    with app.app_context():

        with pytest.raises(
            ApplicationLifecycleException
        ):

            lifecycle.get_request_context()
