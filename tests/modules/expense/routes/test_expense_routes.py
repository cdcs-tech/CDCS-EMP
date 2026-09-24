"""
CDCS Enterprise Management Platform (CDCS-EMP)

Expense Management Module

Expense operational route tests.
"""

import pytest
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


def test_submit_expense_dispatches_command(
    app,
    authenticated_client,
    monkeypatch,
):
    _allow_permissions(monkeypatch)

    captured = {}

    class FakeSubmitExpenseCommand:
        def __init__(self, expense_id):
            captured["expense_id"] = expense_id

    class FakeDispatcher:
        def dispatch(self, command, context):
            captured["command"] = command
            captured["context"] = context

            return SimpleNamespace(
                success=True,
                message="Expense submitted successfully.",
            )

    monkeypatch.setattr(
        expense_routes,
        "SubmitExpenseCommand",
        FakeSubmitExpenseCommand,
    )

    app.extensions["command_dispatcher"] = FakeDispatcher()

    response = authenticated_client.post(
        "/expense/expenses/1/submit"
    )

    assert response.status_code == 302
    assert response.headers["Location"].endswith(
        "/expense/expenses/1"
    )
    assert captured["expense_id"] == 1
    assert captured["context"].module_name == "EXPENSE"
    assert captured["context"].operation == "expense.submit"


def test_approve_expense_dispatches_command(
    app,
    authenticated_client,
    monkeypatch,
):
    _allow_permissions(monkeypatch)

    captured = {}

    class FakeApproveExpenseCommand:
        def __init__(self, expense_id):
            captured["expense_id"] = expense_id

    class FakeDispatcher:
        def dispatch(self, command, context):
            captured["command"] = command
            captured["context"] = context

            return SimpleNamespace(
                success=True,
                message="Expense approved successfully.",
            )

    monkeypatch.setattr(
        expense_routes,
        "ApproveExpenseCommand",
        FakeApproveExpenseCommand,
    )

    app.extensions["command_dispatcher"] = FakeDispatcher()

    response = authenticated_client.post(
        "/expense/expenses/1/approve"
    )

    assert response.status_code == 302
    assert response.headers["Location"].endswith(
        "/expense/expenses/1"
    )
    assert captured["expense_id"] == 1
    assert captured["context"].module_name == "EXPENSE"
    assert captured["context"].operation == "expense.approve"


def test_reject_expense_dispatches_command(
    app,
    authenticated_client,
    monkeypatch,
):
    _allow_permissions(monkeypatch)

    captured = {}

    class FakeRejectExpenseCommand:
        def __init__(self, expense_id):
            captured["expense_id"] = expense_id

    class FakeDispatcher:
        def dispatch(self, command, context):
            captured["command"] = command
            captured["context"] = context

            return SimpleNamespace(
                success=True,
                message="Expense rejected successfully.",
            )

    monkeypatch.setattr(
        expense_routes,
        "RejectExpenseCommand",
        FakeRejectExpenseCommand,
    )

    app.extensions["command_dispatcher"] = FakeDispatcher()

    response = authenticated_client.post(
        "/expense/expenses/1/reject"
    )

    assert response.status_code == 302
    assert response.headers["Location"].endswith(
        "/expense/expenses/1"
    )
    assert captured["expense_id"] == 1
    assert captured["context"].module_name == "EXPENSE"
    assert captured["context"].operation == "expense.reject"


def test_return_expense_dispatches_command(
    app,
    authenticated_client,
    monkeypatch,
):
    _allow_permissions(monkeypatch)

    captured = {}

    class FakeReturnExpenseCommand:
        def __init__(self, expense_id):
            captured["expense_id"] = expense_id

    class FakeDispatcher:
        def dispatch(self, command, context):
            captured["command"] = command
            captured["context"] = context

            return SimpleNamespace(
                success=True,
                message="Expense returned successfully.",
            )

    monkeypatch.setattr(
        expense_routes,
        "ReturnExpenseCommand",
        FakeReturnExpenseCommand,
    )

    app.extensions["command_dispatcher"] = FakeDispatcher()

    response = authenticated_client.post(
        "/expense/expenses/1/return"
    )

    assert response.status_code == 302
    assert response.headers["Location"].endswith(
        "/expense/expenses/1"
    )
    assert captured["expense_id"] == 1
    assert captured["context"].module_name == "EXPENSE"
    assert captured["context"].operation == "expense.return"


def test_resubmit_expense_dispatches_command(
    app,
    authenticated_client,
    monkeypatch,
):
    _allow_permissions(monkeypatch)

    captured = {}

    class FakeResubmitExpenseCommand:
        def __init__(self, expense_id):
            captured["expense_id"] = expense_id

    class FakeDispatcher:
        def dispatch(self, command, context):
            captured["command"] = command
            captured["context"] = context

            return SimpleNamespace(
                success=True,
                message="Expense resubmitted successfully.",
            )

    monkeypatch.setattr(
        expense_routes,
        "ResubmitExpenseCommand",
        FakeResubmitExpenseCommand,
    )

    app.extensions["command_dispatcher"] = FakeDispatcher()

    response = authenticated_client.post(
        "/expense/expenses/1/resubmit"
    )

    assert response.status_code == 302
    assert response.headers["Location"].endswith(
        "/expense/expenses/1"
    )
    assert captured["expense_id"] == 1
    assert captured["context"].module_name == "EXPENSE"
    assert captured["context"].operation == "expense.resubmit"


def test_close_expense_dispatches_command(
    app,
    authenticated_client,
    monkeypatch,
):
    _allow_permissions(monkeypatch)

    captured = {}

    class FakeCloseExpenseCommand:
        def __init__(self, expense_id):
            captured["expense_id"] = expense_id

    class FakeDispatcher:
        def dispatch(self, command, context):
            captured["command"] = command
            captured["context"] = context

            return SimpleNamespace(
                success=True,
                message="Expense closed successfully.",
            )

    monkeypatch.setattr(
        expense_routes,
        "CloseExpenseCommand",
        FakeCloseExpenseCommand,
    )

    app.extensions["command_dispatcher"] = FakeDispatcher()

    response = authenticated_client.post(
        "/expense/expenses/1/close"
    )

    assert response.status_code == 302
    assert response.headers["Location"].endswith(
        "/expense/expenses/1"
    )
    assert captured["expense_id"] == 1
    assert captured["context"].module_name == "EXPENSE"
    assert captured["context"].operation == "expense.close"


@pytest.mark.parametrize(
    (
        "status",
        "expected_actions",
        "unexpected_actions",
    ),
    [
        (
            "DRAFT",
            ["Submit Expense"],
            [
                "Approve Expense",
                "Reject Expense",
                "Return Expense",
                "Resubmit Expense",
                "Close Expense",
            ],
        ),
        (
            "SUBMITTED",
            [
                "Approve Expense",
                "Reject Expense",
                "Return Expense",
            ],
            [
                "Submit Expense",
                "Resubmit Expense",
                "Close Expense",
            ],
        ),
        (
            "RETURNED",
            ["Resubmit Expense"],
            [
                "Submit Expense",
                "Approve Expense",
                "Reject Expense",
                "Return Expense",
                "Close Expense",
            ],
        ),
        (
            "APPROVED",
            ["Close Expense"],
            [
                "Submit Expense",
                "Approve Expense",
                "Reject Expense",
                "Return Expense",
                "Resubmit Expense",
            ],
        ),
        (
            "REJECTED",
            [],
            [
                "Submit Expense",
                "Approve Expense",
                "Reject Expense",
                "Return Expense",
                "Resubmit Expense",
                "Close Expense",
            ],
        ),
        (
            "CLOSED",
            [],
            [
                "Submit Expense",
                "Approve Expense",
                "Reject Expense",
                "Return Expense",
                "Resubmit Expense",
                "Close Expense",
            ],
        ),
    ],
)
def test_view_expense_renders_state_specific_workflow_actions(
    authenticated_client,
    monkeypatch,
    status,
    expected_actions,
    unexpected_actions,
):
    _allow_permissions(monkeypatch)

    expense = SimpleNamespace(
        id=1,
        classification=SimpleNamespace(
            name="Office Supplies",
        ),
        description="Printer paper",
        amount=125.50,
        expense_date=date(2026, 9, 20),
        status=status,
    )

    class FakeExpenseService:
        def get(self, entity_id):
            return expense

    monkeypatch.setattr(
        expense_routes,
        "ExpenseService",
        FakeExpenseService,
    )

    response = authenticated_client.get(
        "/expense/expenses/1"
    )

    assert response.status_code == 200

    for action in expected_actions:
        assert action in response.text

    for action in unexpected_actions:
        assert action not in response.text

    assert status in response.text


def test_view_expense_preserves_common_controls_and_csrf(
    authenticated_client,
    monkeypatch,
):
    _allow_permissions(monkeypatch)

    expense = SimpleNamespace(
        id=1,
        classification=SimpleNamespace(
            name="Office Supplies",
        ),
        description="Printer paper",
        amount=125.50,
        expense_date=date(2026, 9, 20),
        status="DRAFT",
    )

    class FakeExpenseService:
        def get(self, entity_id):
            return expense

    monkeypatch.setattr(
        expense_routes,
        "ExpenseService",
        FakeExpenseService,
    )

    response = authenticated_client.get(
        "/expense/expenses/1"
    )

    assert response.status_code == 200

    assert "Edit Expense" in response.text
    assert "Delete Expense" in response.text
    assert "Back to Expenses" in response.text

    assert (
        'name="csrf_token"'
        in response.text
    )

    assert (
        'action="/expense/expenses/1/submit"'
        in response.text
    )
