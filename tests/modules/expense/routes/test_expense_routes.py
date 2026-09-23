"""
CDCS Enterprise Management Platform (CDCS-EMP)

Expense Management Module

Expense operational route tests.
"""

from datetime import date
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


def test_expenses_requires_authentication(client):
    response = client.get(
        "/expense/expenses/"
    )

    assert response.status_code == 302
    assert "/auth/login" in response.headers["Location"]


def test_expenses_requires_read_permission(
    authenticated_client,
    monkeypatch,
):
    monkeypatch.setattr(
        User,
        "has_permission",
        lambda self, permission: False,
    )

    response = authenticated_client.get(
        "/expense/expenses/"
    )

    assert response.status_code == 403


def test_expenses_list_delegates_to_service(
    authenticated_client,
    monkeypatch,
):
    _allow_permissions(monkeypatch)

    result = SimpleNamespace(
        items=["expense-1"],
    )

    captured = {}

    class FakeExpenseService:
        def paginate(self, options):
            assert options.page == 1
            assert options.page_size == 25
            assert options.sort_by == "expense_date"
            assert options.sort_direction == "asc"
            assert options.search is None
            assert options.filters == {}
            assert options.include_inactive is False

            return result

    def fake_render_template(template, **context):
        captured["template"] = template
        captured["context"] = context
        return "rendered"

    monkeypatch.setattr(
        expense_routes,
        "ExpenseService",
        FakeExpenseService,
    )

    monkeypatch.setattr(
        expense_routes,
        "render_template",
        fake_render_template,
    )

    response = authenticated_client.get(
        "/expense/expenses/"
    )

    assert response.status_code == 200
    assert response.text == "rendered"

    assert captured["template"] == (
        "modules/expense/expenses/index.html"
    )

    assert captured["context"]["expenses"] is result
    assert captured["context"]["search"] == ""
    assert captured["context"]["sort_by"] == "expense_date"
    assert captured["context"]["sort_direction"] == "asc"
    assert captured["context"]["page_size"] == 25
    assert captured["context"]["page_sizes"] == (
        10,
        25,
        50,
        100,
    )


def test_expenses_supports_controlled_query_options(
    authenticated_client,
    monkeypatch,
):
    _allow_permissions(monkeypatch)

    captured = {}

    class FakeExpenseService:
        def paginate(self, options):
            captured["options"] = options

            return SimpleNamespace(
                items=[],
            )

    monkeypatch.setattr(
        expense_routes,
        "ExpenseService",
        FakeExpenseService,
    )

    monkeypatch.setattr(
        expense_routes,
        "render_template",
        lambda template, **context: "rendered",
    )

    response = authenticated_client.get(
        "/expense/expenses/"
        "?page=2"
        "&page_size=50"
        "&sort=amount"
        "&direction=desc"
        "&search=stationery"
    )

    assert response.status_code == 200

    options = captured["options"]

    assert options.page == 2
    assert options.page_size == 50
    assert options.sort_by == "amount"
    assert options.sort_direction == "desc"
    assert options.search == "stationery"
    assert options.filters == {}
    assert options.include_inactive is False


def test_expenses_rejects_unsupported_sort_field(
    authenticated_client,
    monkeypatch,
):
    _allow_permissions(monkeypatch)

    captured = {}

    class FakeExpenseService:
        def paginate(self, options):
            captured["options"] = options

            return SimpleNamespace(
                items=[],
            )

    monkeypatch.setattr(
        expense_routes,
        "ExpenseService",
        FakeExpenseService,
    )

    monkeypatch.setattr(
        expense_routes,
        "render_template",
        lambda template, **context: "rendered",
    )

    response = authenticated_client.get(
        "/expense/expenses/"
        "?sort=invalid_field"
    )

    assert response.status_code == 200

    assert captured["options"].sort_by == "expense_date"


def test_create_expense_requires_create_permission(
    authenticated_client,
    monkeypatch,
):
    monkeypatch.setattr(
        User,
        "has_permission",
        lambda self, permission: False,
    )

    response = authenticated_client.get(
        "/expense/expenses/create"
    )

    assert response.status_code == 403


def test_create_expense_loads_active_classification_choices(
    authenticated_client,
    monkeypatch,
):
    _allow_permissions(monkeypatch)

    captured = {}

    classifications = SimpleNamespace(
        items=[
            SimpleNamespace(
                id=2,
                name="Food",
            ),
            SimpleNamespace(
                id=1,
                name="Office Supplies",
            ),
        ],
    )

    class FakeExpenseClassificationService:
        def paginate(self, options):
            captured["options"] = options
            return classifications

    class FakeExpenseService:
        def create(self, entity):
            captured["entity"] = entity
            return entity

    monkeypatch.setattr(
        expense_routes,
        "ExpenseClassificationService",
        FakeExpenseClassificationService,
    )

    monkeypatch.setattr(
        expense_routes,
        "ExpenseService",
        FakeExpenseService,
    )

    response = authenticated_client.post(
        "/expense/expenses/create",
        data={
            "classification_id": "1",
            "description": "Printer paper",
            "amount": "125.50",
            "expense_date": "2026-09-20",
        },
    )

    assert response.status_code == 302
    assert response.headers["Location"].endswith(
        "/expense/expenses/"
    )

    options = captured["options"]

    assert options.page == 1
    assert options.page_size == 1000
    assert options.sort_by == "name"
    assert options.sort_direction == "asc"
    assert options.filters == {
        "is_active": True,
    }
    assert options.include_inactive is False

    entity = captured["entity"]

    assert entity.classification_id == 1
    assert entity.description == "Printer paper"
    assert entity.amount == 125.50
    assert entity.expense_date == date(2026, 9, 20)


def test_view_expense_requires_read_permission(
    authenticated_client,
    monkeypatch,
):
    monkeypatch.setattr(
        User,
        "has_permission",
        lambda self, permission: False,
    )

    response = authenticated_client.get(
        "/expense/expenses/1"
    )

    assert response.status_code == 403


def test_view_expense_delegates_to_service(
    authenticated_client,
    monkeypatch,
):
    _allow_permissions(monkeypatch)

    expense = SimpleNamespace(
        id=1,
        classification_id=1,
        description="Printer paper",
        amount=125.50,
        expense_date=date(2026, 9, 20),
    )

    captured = {}

    class FakeExpenseService:
        def get(self, entity_id):
            captured["entity_id"] = entity_id
            return expense

    def fake_render_template(template, **context):
        captured["template"] = template
        captured["context"] = context
        return "rendered"

    monkeypatch.setattr(
        expense_routes,
        "ExpenseService",
        FakeExpenseService,
    )

    monkeypatch.setattr(
        expense_routes,
        "render_template",
        fake_render_template,
    )

    response = authenticated_client.get(
        "/expense/expenses/1"
    )

    assert response.status_code == 200
    assert response.text == "rendered"

    assert captured["entity_id"] == 1
    assert captured["template"] == (
        "modules/expense/expenses/view.html"
    )
    assert captured["context"]["expense"] is expense


def test_edit_expense_requires_update_permission(
    authenticated_client,
    monkeypatch,
):
    monkeypatch.setattr(
        User,
        "has_permission",
        lambda self, permission: False,
    )

    response = authenticated_client.get(
        "/expense/expenses/1/edit"
    )

    assert response.status_code == 403


def test_edit_expense_delegates_to_service(
    authenticated_client,
    monkeypatch,
):
    _allow_permissions(monkeypatch)

    expense = SimpleNamespace(
        id=1,
        classification_id=1,
        description="Printer paper",
        amount=125.50,
        expense_date=date(2026, 9, 20),
    )

    classifications = SimpleNamespace(
        items=[
            SimpleNamespace(
                id=1,
                name="Office Supplies",
            ),
        ],
    )

    captured = {}

    class FakeExpenseClassificationService:
        def paginate(self, options):
            captured["classification_options"] = options
            return classifications

    class FakeExpenseService:
        def get(self, entity_id):
            captured["get_id"] = entity_id
            return expense

        def update(self, entity):
            captured["updated"] = entity
            return entity

    monkeypatch.setattr(
        expense_routes,
        "ExpenseClassificationService",
        FakeExpenseClassificationService,
    )

    monkeypatch.setattr(
        expense_routes,
        "ExpenseService",
        FakeExpenseService,
    )

    response = authenticated_client.post(
        "/expense/expenses/1/edit",
        data={
            "classification_id": "1",
            "description": "Printer paper and toner",
            "amount": "175.75",
            "expense_date": "2026-09-21",
        },
    )

    assert response.status_code == 302
    assert response.headers["Location"].endswith(
        "/expense/expenses/1"
    )

    assert captured["get_id"] == 1

    classification_options = captured[
        "classification_options"
    ]

    assert classification_options.page == 1
    assert classification_options.page_size == 1000
    assert classification_options.sort_by == "name"
    assert classification_options.sort_direction == "asc"
    assert classification_options.filters == {
        "is_active": True,
    }
    assert classification_options.include_inactive is False

    assert captured["updated"] is expense

    assert expense.classification_id == 1
    assert expense.description == "Printer paper and toner"
    assert expense.amount == 175.75
    assert expense.expense_date == date(2026, 9, 21)


def test_delete_expense_requires_delete_permission(
    authenticated_client,
    monkeypatch,
):
    monkeypatch.setattr(
        User,
        "has_permission",
        lambda self, permission: False,
    )

    response = authenticated_client.post(
        "/expense/expenses/1/delete"
    )

    assert response.status_code == 403


def test_delete_expense_delegates_to_service(
    authenticated_client,
    monkeypatch,
):
    _allow_permissions(monkeypatch)

    captured = {}

    class FakeExpenseService:
        def delete(self, entity_id):
            captured["entity_id"] = entity_id

    monkeypatch.setattr(
        expense_routes,
        "ExpenseService",
        FakeExpenseService,
    )

    response = authenticated_client.post(
        "/expense/expenses/1/delete"
    )

    assert response.status_code == 302
    assert response.headers["Location"].endswith(
        "/expense/expenses/"
    )

    assert captured["entity_id"] == 1
