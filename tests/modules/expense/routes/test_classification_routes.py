"""
CDCS Enterprise Management Platform (CDCS-EMP)

Expense Management Module

Expense Classification route tests.
"""

from types import SimpleNamespace

from app.models.user import User

import app.modules.expense.routes.routes as expense_routes


def _allow_permissions(monkeypatch):
    """
    Explicitly authorize successful route-path tests.

    Dedicated authorization tests separately verify that missing
    permissions are rejected with HTTP 403.
    """
    monkeypatch.setattr(
        User,
        "has_permission",
        lambda self, permission: True,
    )


def test_classifications_requires_authentication(client):
    response = client.get(
        "/expense/classifications/"
    )

    assert response.status_code == 302
    assert "/auth/login" in response.headers["Location"]


def test_classifications_requires_read_permission(
    authenticated_client,
    monkeypatch,
):
    monkeypatch.setattr(
        User,
        "has_permission",
        lambda self, permission: False,
    )

    response = authenticated_client.get(
        "/expense/classifications/"
    )

    assert response.status_code == 403


def test_classifications_list_delegates_to_service(
    authenticated_client,
    monkeypatch,
):
    _allow_permissions(monkeypatch)

    result = SimpleNamespace(
        items=["classification-1"],
    )

    captured = {}

    class FakeExpenseClassificationService:
        def paginate(self, options):
            assert options.page == 1
            assert options.page_size == 25
            assert options.sort_by == "name"
            assert options.sort_direction == "asc"
            assert options.search is None
            assert options.filters == {}
            assert options.include_inactive is True

            return result

    def fake_render_template(template, **context):
        captured["template"] = template
        captured["context"] = context
        return "rendered"

    monkeypatch.setattr(
        expense_routes,
        "ExpenseClassificationService",
        FakeExpenseClassificationService,
    )

    monkeypatch.setattr(
        expense_routes,
        "render_template",
        fake_render_template,
    )

    response = authenticated_client.get(
        "/expense/classifications/"
    )

    assert response.status_code == 200
    assert response.text == "rendered"

    assert captured["template"] == (
        "modules/expense/classifications/index.html"
    )

    assert captured["context"]["classifications"] is result
    assert captured["context"]["search"] == ""
    assert captured["context"]["active"] == ""
    assert captured["context"]["sort_by"] == "name"
    assert captured["context"]["sort_direction"] == "asc"
    assert captured["context"]["page_size"] == 25
    assert captured["context"]["page_sizes"] == (
        10,
        25,
        50,
        100,
    )


def test_classifications_supports_controlled_query_options(
    authenticated_client,
    monkeypatch,
):
    _allow_permissions(monkeypatch)

    captured = {}

    class FakeExpenseClassificationService:
        def paginate(self, options):
            captured["options"] = options

            return SimpleNamespace(
                items=[],
            )

    monkeypatch.setattr(
        expense_routes,
        "ExpenseClassificationService",
        FakeExpenseClassificationService,
    )

    monkeypatch.setattr(
        expense_routes,
        "render_template",
        lambda template, **context: "rendered",
    )

    response = authenticated_client.get(
        "/expense/classifications/"
        "?page=2"
        "&page_size=50"
        "&sort=code"
        "&direction=desc"
        "&search=food"
        "&active=active"
    )

    assert response.status_code == 200

    options = captured["options"]

    assert options.page == 2
    assert options.page_size == 50
    assert options.sort_by == "code"
    assert options.sort_direction == "desc"
    assert options.search == "food"
    assert options.filters == {
        "is_active": True,
    }
    assert options.include_inactive is True


def test_classifications_rejects_unsupported_sort_field(
    authenticated_client,
    monkeypatch,
):
    _allow_permissions(monkeypatch)

    captured = {}

    class FakeExpenseClassificationService:
        def paginate(self, options):
            captured["options"] = options

            return SimpleNamespace(
                items=[],
            )

    monkeypatch.setattr(
        expense_routes,
        "ExpenseClassificationService",
        FakeExpenseClassificationService,
    )

    monkeypatch.setattr(
        expense_routes,
        "render_template",
        lambda template, **context: "rendered",
    )

    response = authenticated_client.get(
        "/expense/classifications/"
        "?sort=invalid_field"
    )

    assert response.status_code == 200

    assert captured["options"].sort_by == "name"


def test_create_classification_requires_create_permission(
    authenticated_client,
    monkeypatch,
):
    monkeypatch.setattr(
        User,
        "has_permission",
        lambda self, permission: False,
    )

    response = authenticated_client.get(
        "/expense/classifications/create"
    )

    assert response.status_code == 403


def test_create_classification_delegates_to_service(
    authenticated_client,
    monkeypatch,
):
    _allow_permissions(monkeypatch)

    captured = {}

    class FakeExpenseClassificationService:
        def create(self, entity):
            captured["entity"] = entity
            return entity

    monkeypatch.setattr(
        expense_routes,
        "ExpenseClassificationService",
        FakeExpenseClassificationService,
    )

    response = authenticated_client.post(
        "/expense/classifications/create",
        data={
            "name": "Food",
            "code": "FOOD",
            "description": "Food-related expenses",
        },
    )

    assert response.status_code == 302
    assert response.headers["Location"].endswith(
        "/expense/classifications/"
    )

    entity = captured["entity"]

    assert entity.name == "Food"
    assert entity.code == "FOOD"
    assert entity.description == "Food-related expenses"


def test_view_classification_requires_read_permission(
    authenticated_client,
    monkeypatch,
):
    monkeypatch.setattr(
        User,
        "has_permission",
        lambda self, permission: False,
    )

    response = authenticated_client.get(
        "/expense/classifications/1"
    )

    assert response.status_code == 403


def test_view_classification_delegates_to_service(
    authenticated_client,
    monkeypatch,
):
    _allow_permissions(monkeypatch)

    classification = SimpleNamespace(
        id=1,
        name="Food",
        code="FOOD",
        description="Food-related expenses",
    )

    captured = {}

    class FakeExpenseClassificationService:
        def get(self, entity_id):
            captured["entity_id"] = entity_id
            return classification

    def fake_render_template(template, **context):
        captured["template"] = template
        captured["context"] = context
        return "rendered"

    monkeypatch.setattr(
        expense_routes,
        "ExpenseClassificationService",
        FakeExpenseClassificationService,
    )

    monkeypatch.setattr(
        expense_routes,
        "render_template",
        fake_render_template,
    )

    response = authenticated_client.get(
        "/expense/classifications/1"
    )

    assert response.status_code == 200
    assert response.text == "rendered"

    assert captured["entity_id"] == 1
    assert captured["template"] == (
        "modules/expense/classifications/view.html"
    )
    assert captured["context"]["classification"] is classification


def test_edit_classification_requires_update_permission(
    authenticated_client,
    monkeypatch,
):
    monkeypatch.setattr(
        User,
        "has_permission",
        lambda self, permission: False,
    )

    response = authenticated_client.get(
        "/expense/classifications/1/edit"
    )

    assert response.status_code == 403


def test_edit_classification_delegates_to_service(
    authenticated_client,
    monkeypatch,
):
    _allow_permissions(monkeypatch)

    classification = SimpleNamespace(
        id=1,
        name="Food",
        code="FOOD",
        description="Food-related expenses",
    )

    captured = {}

    class FakeExpenseClassificationService:
        def get(self, entity_id):
            captured["get_id"] = entity_id
            return classification

        def update(self, entity):
            captured["updated"] = entity
            return entity

    monkeypatch.setattr(
        expense_routes,
        "ExpenseClassificationService",
        FakeExpenseClassificationService,
    )

    response = authenticated_client.post(
        "/expense/classifications/1/edit",
        data={
            "name": "Catering Food",
            "code": "CAT-FOOD",
            "description": "Catering-related food expenses",
        },
    )

    assert response.status_code == 302
    assert response.headers["Location"].endswith(
        "/expense/classifications/1"
    )

    assert captured["get_id"] == 1
    assert captured["updated"] is classification
    assert classification.name == "Catering Food"
    assert classification.code == "CAT-FOOD"
    assert classification.description == (
        "Catering-related food expenses"
    )


def test_delete_classification_requires_delete_permission(
    authenticated_client,
    monkeypatch,
):
    monkeypatch.setattr(
        User,
        "has_permission",
        lambda self, permission: False,
    )

    response = authenticated_client.post(
        "/expense/classifications/1/delete"
    )

    assert response.status_code == 403


def test_delete_classification_delegates_to_service(
    authenticated_client,
    monkeypatch,
):
    _allow_permissions(monkeypatch)

    captured = {}

    class FakeExpenseClassificationService:
        def delete(self, entity_id):
            captured["entity_id"] = entity_id

    monkeypatch.setattr(
        expense_routes,
        "ExpenseClassificationService",
        FakeExpenseClassificationService,
    )

    response = authenticated_client.post(
        "/expense/classifications/1/delete"
    )

    assert response.status_code == 302
    assert response.headers["Location"].endswith(
        "/expense/classifications/"
    )
    assert captured["entity_id"] == 1


def test_activate_classification_requires_update_permission(
    authenticated_client,
    monkeypatch,
):
    monkeypatch.setattr(
        User,
        "has_permission",
        lambda self, permission: False,
    )

    response = authenticated_client.post(
        "/expense/classifications/1/activate"
    )

    assert response.status_code == 403


def test_activate_classification_delegates_to_service(
    authenticated_client,
    monkeypatch,
):
    _allow_permissions(monkeypatch)

    captured = {}

    class FakeExpenseClassificationService:
        def activate(self, entity_id):
            captured["entity_id"] = entity_id

    monkeypatch.setattr(
        expense_routes,
        "ExpenseClassificationService",
        FakeExpenseClassificationService,
    )

    response = authenticated_client.post(
        "/expense/classifications/1/activate"
    )

    assert response.status_code == 302
    assert response.headers["Location"].endswith(
        "/expense/classifications/"
    )
    assert captured["entity_id"] == 1


def test_deactivate_classification_requires_update_permission(
    authenticated_client,
    monkeypatch,
):
    monkeypatch.setattr(
        User,
        "has_permission",
        lambda self, permission: False,
    )

    response = authenticated_client.post(
        "/expense/classifications/1/deactivate"
    )

    assert response.status_code == 403


def test_deactivate_classification_delegates_to_service(
    authenticated_client,
    monkeypatch,
):
    _allow_permissions(monkeypatch)

    captured = {}

    class FakeExpenseClassificationService:
        def deactivate(self, entity_id):
            captured["entity_id"] = entity_id

    monkeypatch.setattr(
        expense_routes,
        "ExpenseClassificationService",
        FakeExpenseClassificationService,
    )

    response = authenticated_client.post(
        "/expense/classifications/1/deactivate"
    )

    assert response.status_code == 302
    assert response.headers["Location"].endswith(
        "/expense/classifications/"
    )
    assert captured["entity_id"] == 1
