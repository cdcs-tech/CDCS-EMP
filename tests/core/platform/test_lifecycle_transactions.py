import pytest
from flask import Blueprint, Flask

from app.core.platform.lifecycle import ApplicationLifecycle


class FakeTransactionManager:
    def __init__(self):
        self.active = False
        self.begin_count = 0
        self.commit_count = 0
        self.rollback_count = 0

    def begin(self):
        self.begin_count += 1
        self.active = True

    def commit(self):
        self.commit_count += 1
        self.active = False

    def rollback(self):
        self.rollback_count += 1
        self.active = False


@pytest.fixture
def lifecycle_app(monkeypatch):
    app = Flask(__name__)
    app.secret_key = "test-secret"

    lifecycle = ApplicationLifecycle()
    lifecycle.register_request_lifecycle(app)

    transaction_managers = []

    def fake_transaction_manager():
        manager = FakeTransactionManager()
        transaction_managers.append(manager)
        return manager

    monkeypatch.setattr(
        "app.core.platform.lifecycle.SQLAlchemyTransactionManager",
        fake_transaction_manager,
    )

    return app, transaction_managers


def _register_route(
    app,
    blueprint_name,
    endpoint_name,
    method,
    status_code,
):
    blueprint = Blueprint(
        blueprint_name,
        __name__,
        url_prefix=f"/{blueprint_name}",
    )

    def handler():
        return ("ok", status_code)

    handler.__name__ = endpoint_name

    blueprint.add_url_rule(
        "/operation",
        endpoint=endpoint_name,
        view_func=handler,
        methods=[method],
    )

    app.register_blueprint(blueprint)


def test_procurement_post_starts_application_transaction(
    lifecycle_app,
):
    app, transaction_managers = lifecycle_app

    _register_route(
        app,
        "procurement",
        "create",
        "POST",
        200,
    )

    with app.test_client() as client:
        response = client.post(
            "/procurement/operation",
        )

    assert response.status_code == 200
    assert len(transaction_managers) == 1
    assert transaction_managers[0].begin_count == 1
    assert transaction_managers[0].commit_count == 1
    assert transaction_managers[0].rollback_count == 0


def test_procurement_failed_mutation_rolls_back(
    lifecycle_app,
):
    app, transaction_managers = lifecycle_app

    _register_route(
        app,
        "procurement",
        "delete",
        "DELETE",
        400,
    )

    with app.test_client() as client:
        response = client.delete(
            "/procurement/operation",
        )

    assert response.status_code == 400
    assert len(transaction_managers) == 1
    assert transaction_managers[0].begin_count == 1
    assert transaction_managers[0].commit_count == 0
    assert transaction_managers[0].rollback_count == 1


def test_procurement_get_does_not_start_application_transaction(
    lifecycle_app,
):
    app, transaction_managers = lifecycle_app

    _register_route(
        app,
        "procurement",
        "list",
        "GET",
        200,
    )

    with app.test_client() as client:
        response = client.get(
            "/procurement/operation",
        )

    assert response.status_code == 200
    assert transaction_managers == []


@pytest.mark.parametrize(
    ("blueprint", "endpoint", "method"),
    [
        ("catering", "post_movement", "POST"),
        ("catering", "post_transfer", "POST"),
    ],
)
def test_explicit_catering_transactions_remain_excluded(
    lifecycle_app,
    blueprint,
    endpoint,
    method,
):
    app, transaction_managers = lifecycle_app

    _register_route(
        app,
        blueprint,
        endpoint,
        method,
        200,
    )

    with app.test_client() as client:
        response = client.open(
            f"/{blueprint}/operation",
            method=method,
        )

    assert response.status_code == 200
    assert transaction_managers == []


@pytest.mark.parametrize(
    ("blueprint", "method"),
    [
        ("auth", "POST"),
        ("admin", "POST"),
        ("reporting", "DELETE"),
    ],
)
def test_non_business_requests_remain_outside_application_transaction(
    lifecycle_app,
    blueprint,
    method,
):
    app, transaction_managers = lifecycle_app

    _register_route(
        app,
        blueprint,
        "operation",
        method,
        200,
    )

    with app.test_client() as client:
        response = client.open(
            f"/{blueprint}/operation",
            method=method,
        )

    assert response.status_code == 200
    assert transaction_managers == []


def test_request_without_blueprint_remains_outside_application_transaction():
    app = Flask(__name__)
    app.secret_key = "test-secret"

    lifecycle = ApplicationLifecycle()

    with app.test_request_context(
        "/operation",
        method="POST",
    ):
        assert (
            lifecycle._request_requires_application_transaction()
            is False
        )


def test_business_module_blueprints_are_application_transaction_blueprints():
    lifecycle = ApplicationLifecycle()

    assert "catering" in lifecycle.APPLICATION_TRANSACTION_BLUEPRINTS
    assert "procurement" in lifecycle.APPLICATION_TRANSACTION_BLUEPRINTS
    assert "expense" in lifecycle.APPLICATION_TRANSACTION_BLUEPRINTS
