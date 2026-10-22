"""Route tests for Catering Expense Cost Associations."""

from datetime import datetime, timezone
from types import SimpleNamespace

import pytest

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


def _fake_expense(
    expense_id=12,
    *,
    status="APPROVED",
    approved_at="__AUTO__",
):
    if approved_at == "__AUTO__":
        approved_at = (
            datetime.now(timezone.utc)
            if status == "APPROVED"
            else None
        )

    return SimpleNamespace(
        id=expense_id,
        status=status,
        approved_at=approved_at,
    )


def _fake_association(
    *,
    expense_id,
    association_id=21,
    status="ELIGIBLE",
    context_type="CATERING_EVENT",
    context_reference="EVENT-7",
    contribution_id=None,
):
    event_reference = context_reference.removeprefix("EVENT-")

    return SimpleNamespace(
        id=association_id,
        expense_id=expense_id,
        status=status,
        contribution_id=contribution_id
        or (
            f"expense:{expense_id}:catering:event:"
            f"{event_reference}:consume_approved_expense"
        ),
        catering_context_type=context_type,
        catering_context_reference=context_reference,
        consumed_at=None,
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
            return event if event is not None and event.id == event_id else None

    class FakeExpenseRepository:
        def get_by_id(self, expense_id):
            if expense is None:
                return None
            return expense if expense.id == expense_id else None

    class FakeAssociationRepository:
        def get_all(self):
            return associations

        def get_by_catering_context(
            self,
            context_type,
            context_reference,
        ):
            return [
                association
                for association in associations
                if (
                    association.catering_context_type == context_type
                    and association.catering_context_reference
                    == context_reference
                )
            ]

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


# ---------------------------------------------------------------------------
# Association creation
# ---------------------------------------------------------------------------


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


@pytest.mark.parametrize(
    ("expense_status", "approved_at"),
    [
        ("DRAFT", None),
        ("SUBMITTED", None),
        ("APPROVED", None),
    ],
    ids=[
        "draft-expense",
        "submitted-expense",
        "approved-without-timestamp",
    ],
)
def test_create_association_rejects_unapproved_expense(
    authenticated_client,
    monkeypatch,
    expense_status,
    approved_at,
):
    _allow_permissions(monkeypatch)
    _install_form(monkeypatch, valid=True, expense_id=12)
    _install_repositories(
        monkeypatch,
        event=_fake_event(7),
        expense=_fake_expense(
            status=expense_status,
            approved_at=approved_at,
        ),
    )

    class UnexpectedAssociationService:
        def __init__(self, **kwargs):
            raise AssertionError(
                "Association service must not be created "
                "for an ineligible Expense."
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
    assert (
        "Only approved Expenses with an approval timestamp "
        "can be associated with a Catering Event."
        in _flashed_messages(authenticated_client)
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
        expense=_fake_expense(),
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
        expense=_fake_expense(),
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

    class FakeExpenseCateringPostCommitExecutor:
        def deliver_association(
            self,
            *,
            expense,
            association,
            approved_at,
        ):
            captured["delivered_expense"] = expense
            captured["delivered_association"] = association
            captured["approved_at"] = approved_at

    monkeypatch.setattr(
        catering_routes,
        "ExpenseCateringPostCommitExecutor",
        FakeExpenseCateringPostCommitExecutor,
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
    assert captured["delivered_expense"].id == 12
    assert captured["delivered_association"] is association
    assert captured["approved_at"] is not None
    assert (
        "Expense associated with Catering Event and cost contribution "
        "delivered successfully."
        in _flashed_messages(authenticated_client)
    )


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


# ---------------------------------------------------------------------------
# Association delivery retry
# ---------------------------------------------------------------------------


def test_retry_association_delivers_existing_eligible_contribution(
    authenticated_client,
    monkeypatch,
):
    _allow_permissions(monkeypatch)
    expense = _fake_expense()
    association = _fake_association(expense_id=expense.id)

    _install_repositories(
        monkeypatch,
        event=_fake_event(7),
        expense=expense,
        associations=[association],
    )

    captured = {}

    class FakeExecutor:
        def deliver_association(self, **kwargs):
            captured.update(kwargs)

    monkeypatch.setattr(
        catering_routes,
        "ExpenseCateringPostCommitExecutor",
        FakeExecutor,
    )

    response = authenticated_client.post(
        "/catering/events/7/expense-cost-associations/21/retry",
        follow_redirects=False,
    )

    assert response.status_code == 302
    assert response.headers["Location"].endswith("/catering/events/7")
    assert captured == {
        "expense": expense,
        "association": association,
        "approved_at": expense.approved_at,
    }
    assert (
        "Catering cost contribution delivered successfully."
        in _flashed_messages(authenticated_client)
    )


def test_retry_association_reports_delivery_failure_without_duplicate(
    authenticated_client,
    monkeypatch,
):
    _allow_permissions(monkeypatch)
    expense = _fake_expense()
    association = _fake_association(expense_id=expense.id)

    associations = _install_repositories(
        monkeypatch,
        event=_fake_event(7),
        expense=expense,
        associations=[association],
    )

    class FailingExecutor:
        def deliver_association(self, **kwargs):
            raise RuntimeError("simulated provider failure")

    monkeypatch.setattr(
        catering_routes,
        "ExpenseCateringPostCommitExecutor",
        FailingExecutor,
    )

    response = authenticated_client.post(
        "/catering/events/7/expense-cost-associations/21/retry",
        follow_redirects=False,
    )

    assert response.status_code == 302
    assert len(associations) == 1
    assert association.status == "ELIGIBLE"
    assert (
        "Catering delivery failed again. The association remains "
        "eligible for another retry."
        in _flashed_messages(authenticated_client)
    )


@pytest.mark.parametrize(
    ("association_status", "association_event", "expected_message"),
    [
        (
            "CONSUMED",
            "EVENT-7",
            "Only eligible Expense Cost Associations can be retried.",
        ),
        (
            "ELIGIBLE",
            "EVENT-8",
            "Expense Cost Association not found for this Catering Event.",
        ),
    ],
    ids=["already-consumed", "belongs-to-another-event"],
)
def test_retry_rejects_ineligible_or_other_event_association(
    authenticated_client,
    monkeypatch,
    association_status,
    association_event,
    expected_message,
):
    _allow_permissions(monkeypatch)
    association = _fake_association(
        expense_id=12,
        status=association_status,
        context_reference=association_event,
    )

    _install_repositories(
        monkeypatch,
        event=_fake_event(7),
        expense=_fake_expense(),
        associations=[association],
    )

    class UnexpectedExecutor:
        def deliver_association(self, **kwargs):
            raise AssertionError(
                "An invalid association must not be delivered."
            )

    monkeypatch.setattr(
        catering_routes,
        "ExpenseCateringPostCommitExecutor",
        UnexpectedExecutor,
    )

    response = authenticated_client.post(
        "/catering/events/7/expense-cost-associations/21/retry",
        follow_redirects=False,
    )

    assert response.status_code == 302
    assert expected_message in _flashed_messages(authenticated_client)


def test_retry_rejects_missing_event(
    authenticated_client,
    monkeypatch,
):
    _allow_permissions(monkeypatch)
    _install_repositories(monkeypatch, event=None)

    response = authenticated_client.post(
        "/catering/events/7/expense-cost-associations/21/retry",
        follow_redirects=False,
    )

    assert response.status_code == 302
    assert "Catering Event not found." in _flashed_messages(
        authenticated_client
    )


def test_retry_rejects_missing_expense(
    authenticated_client,
    monkeypatch,
):
    _allow_permissions(monkeypatch)
    association = _fake_association(expense_id=12)

    _install_repositories(
        monkeypatch,
        event=_fake_event(7),
        expense=None,
        associations=[association],
    )

    class UnexpectedExecutor:
        def deliver_association(self, **kwargs):
            raise AssertionError(
                "A missing Expense must not be delivered."
            )

    monkeypatch.setattr(
        catering_routes,
        "ExpenseCateringPostCommitExecutor",
        UnexpectedExecutor,
    )

    response = authenticated_client.post(
        "/catering/events/7/expense-cost-associations/21/retry",
        follow_redirects=False,
    )

    assert response.status_code == 302
    assert (
        "The associated Expense must still be approved and have "
        "an approval timestamp before delivery can be retried."
        in _flashed_messages(authenticated_client)
    )


@pytest.mark.parametrize(
    ("expense_status", "approved_at"),
    [
        ("DRAFT", None),
        ("SUBMITTED", None),
        ("APPROVED", None),
    ],
    ids=[
        "draft-expense",
        "submitted-expense",
        "approved-without-timestamp",
    ],
)
def test_retry_rejects_expense_without_valid_approval(
    authenticated_client,
    monkeypatch,
    expense_status,
    approved_at,
):
    _allow_permissions(monkeypatch)
    association = _fake_association(expense_id=12)

    _install_repositories(
        monkeypatch,
        event=_fake_event(7),
        expense=_fake_expense(
            status=expense_status,
            approved_at=approved_at,
        ),
        associations=[association],
    )

    class UnexpectedExecutor:
        def deliver_association(self, **kwargs):
            raise AssertionError(
                "An Expense without valid approval must not be delivered."
            )

    monkeypatch.setattr(
        catering_routes,
        "ExpenseCateringPostCommitExecutor",
        UnexpectedExecutor,
    )

    response = authenticated_client.post(
        "/catering/events/7/expense-cost-associations/21/retry",
        follow_redirects=False,
    )

    assert response.status_code == 302
    assert (
        "The associated Expense must still be approved and have "
        "an approval timestamp before delivery can be retried."
        in _flashed_messages(authenticated_client)
    )


def test_retry_association_permission_is_enforced(
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
            "Denied retry must not access repositories."
        )

    monkeypatch.setattr(
        catering_routes,
        "CateringEventRepository",
        unexpected_repository,
    )

    response = authenticated_client.post(
        "/catering/events/7/expense-cost-associations/21/retry",
        follow_redirects=False,
    )

    assert response.status_code in (302, 403)
