"""Route tests for Catering Expense Cost Associations."""

from types import SimpleNamespace

import app.modules.catering.routes.routes as catering_routes
from app.models.user import User


def _allow_permissions(monkeypatch):
    """Authorize successful route-path tests."""
    monkeypatch.setattr(
        User,
        "has_permission",
        lambda self, permission: True,
    )


def _fake_event(event_id=7):
    return SimpleNamespace(id=event_id, status="CONFIRMED")


def _fake_association(
    *,
    expense_id,
    context_type="CATERING_EVENT",
    context_reference="EVENT-7",
):
    return SimpleNamespace(
        expense_id=expense_id,
        catering_context_type=context_type,
        catering_context_reference=context_reference,
    )


def _install_form(monkeypatch, *, valid, expense_id=12):
    """Replace form validation and template rendering for isolated route tests."""

    class FakeForm:
        def __init__(self):
            self.expense_id = SimpleNamespace(data=expense_id)

        def validate_on_submit(self):
            return valid

    monkeypatch.setattr(
        catering_routes,
        "CateringExpenseCostAssociationForm",
        FakeForm,
    )
    monkeypatch.setattr(
        catering_routes,
        "render_template",
        lambda *args, **kwargs: "association form",
    )


def _install_repositories(
    monkeypatch,
    *,
    event=None,
    expense=None,
    associations=None,
):
    """Install isolated fake repositories for route tests."""
    associations = list(associations or [])

    class FakeEventRepository:
        def get_by_id(self, event_id):
            return event

    class FakeExpenseRepository:
        def get_by_id(self, expense_id):
            return expense

    class FakeAssociationRepository:
        def get_all(self):
            return associations

    monkeypatch.setattr(
        catering_routes,
        "CateringEventRepository",
        FakeEventRepository,
    )
    monkeypatch.setattr(
        catering_routes,
        "ExpenseRepository",
        FakeExpenseRepository,
    )
    monkeypatch.setattr(
        catering_routes,
        "CateringExpenseCostAssociationRepository",
        FakeAssociationRepository,
    )

    return associations


def _flashed_messages(authenticated_client):
    """Return flashed message text from the current session."""
    with authenticated_client.session_transaction() as session:
        return [
            message
            for category, message in session.get("_flashes", [])
        ]


def test_create_association_rejects_missing_event(
    authenticated_client,
    monkeypatch,
):
    _allow_permissions(monkeypatch)
    _install_form(monkeypatch, valid=False)
    _install_repositories(monkeypatch, event=None)

    response = authenticated_client.get(
        "/catering/events/7/expense-cost-associations/create",
        follow_redirects=False,
    )

    assert response.status_code == 302
    assert response.headers["Location"].rstrip("/").endswith("/catering/events")
    assert "Catering Event not found." in _flashed_messages(
        authenticated_client
    )


def test_create_association_rejects_missing_expense(
    authenticated_client,
    monkeypatch,
):
    _allow_permissions(monkeypatch)
    _install_form(monkeypatch, valid=True, expense_id=12)
    _install_repositories(
        monkeypatch,
        event=_fake_event(7),
        expense=None,
    )

    response = authenticated_client.post(
        "/catering/events/7/expense-cost-associations/create",
        follow_redirects=False,
    )

    assert response.status_code == 200
    assert "Expense not found." in _flashed_messages(
        authenticated_client
    )


def test_create_association_rejects_duplicate_for_same_event(
    authenticated_client,
    monkeypatch,
):
    _allow_permissions(monkeypatch)
    _install_form(monkeypatch, valid=True, expense_id=12)
    associations = _install_repositories(
        monkeypatch,
        event=_fake_event(7),
        expense=SimpleNamespace(id=12),
        associations=[
            _fake_association(
                expense_id=12,
                context_reference="EVENT-7",
            )
        ],
    )

    class UnexpectedAssociationService:
        def __init__(self, **kwargs):
            raise AssertionError(
                "Service must not be created for a duplicate association."
            )

    monkeypatch.setattr(
        catering_routes,
        "CateringExpenseCostAssociationService",
        UnexpectedAssociationService,
    )

    response = authenticated_client.post(
        "/catering/events/7/expense-cost-associations/create",
        follow_redirects=False,
    )

    assert response.status_code == 200
    assert len(associations) == 1
    assert (
        "This Expense is already associated with this Catering Event."
        in _flashed_messages(authenticated_client)
    )


def test_create_association_allows_same_expense_for_different_event(
    authenticated_client,
    monkeypatch,
):
    _allow_permissions(monkeypatch)
    _install_form(monkeypatch, valid=True, expense_id=12)
    _install_repositories(
        monkeypatch,
        event=_fake_event(8),
        expense=SimpleNamespace(id=12),
        associations=[
            _fake_association(
                expense_id=12,
                context_reference="EVENT-7",
            )
        ],
    )

    captured = {}

    class FakeAssociationService:
        def __init__(self, **kwargs):
            captured["authorization_adapter"] = (
                kwargs["authorization_adapter"]
            )

        def create(self, association, *, subject):
            captured["association"] = association
            captured["subject"] = subject

    monkeypatch.setattr(
        catering_routes,
        "CateringExpenseCostAssociationService",
        FakeAssociationService,
    )

    response = authenticated_client.post(
        "/catering/events/8/expense-cost-associations/create",
        follow_redirects=False,
    )

    assert response.headers["Location"].endswith("/catering/events/8")

    association = captured["association"]
    assert association.expense_id == 12
    assert association.catering_context_type == "CATERING_EVENT"
    assert association.catering_context_reference == "EVENT-8"
    assert association.status == "ELIGIBLE"
    assert association.contribution_id == (
        "expense:12:catering:event:8:consume_approved_expense"
    )
    assert captured["subject"] is not None
    assert captured["authorization_adapter"] is not None


def test_create_association_permission_is_enforced(
    authenticated_client,
    monkeypatch,
):
    monkeypatch.setattr(
        User,
        "has_permission",
        lambda self, permission: False,
    )

    def unexpected_repository():
        raise AssertionError(
            "The route must be denied before repository access."
        )

    monkeypatch.setattr(
        catering_routes,
        "CateringEventRepository",
        unexpected_repository,
    )

    response = authenticated_client.get(
        "/catering/events/7/expense-cost-associations/create",
        follow_redirects=False,
    )

    assert response.status_code in (302, 403)
