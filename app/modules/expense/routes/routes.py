"""
CDCS Enterprise Management Platform (CDCS-EMP)

Expense Management Module

HTTP routes.
"""

from __future__ import annotations

from flask import flash
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for
from flask_login import login_required

from app.core.data.query import QueryOptions
from app.security.decorators import require_permission

from app.modules.expense.forms import (
    ExpenseClassificationForm,
    ExpenseForm,
)
from app.modules.expense.models import (
    Expense,
    ExpenseClassification,
)
from app.modules.expense.security import (
    EXPENSE_CLASSIFICATION_CREATE,
    EXPENSE_CLASSIFICATION_DELETE,
    EXPENSE_CLASSIFICATION_READ,
    EXPENSE_CLASSIFICATION_UPDATE,
    EXPENSE_CREATE,
    EXPENSE_DELETE,
    EXPENSE_READ,
    EXPENSE_UPDATE,
)
from app.modules.expense.services import (
    ExpenseClassificationService,
    ExpenseService,
)

from . import expense_bp


_CLASSIFICATION_SORT_FIELDS = {
    "name",
    "code",
    "is_active",
}

_EXPENSE_SORT_FIELDS = {
    "description",
    "amount",
    "expense_date",
}

_PAGE_SIZES = (
    10,
    25,
    50,
    100,
)


def _parse_positive_int(
    value: str | None,
    default: int,
) -> int:
    """
    Parse a positive integer query parameter.
    """
    try:
        parsed = int(value or "")
    except (TypeError, ValueError):
        return default

    if parsed < 1:
        return default

    return parsed


def _parse_page_size(
    value: str | None,
) -> int:
    """
    Parse and constrain the requested page size.
    """
    parsed = _parse_positive_int(
        value,
        25,
    )

    if parsed not in _PAGE_SIZES:
        return 25

    return parsed


def _parse_sort(
    value: str | None,
) -> str:
    """
    Parse a controlled classification sort field.
    """
    if value in _CLASSIFICATION_SORT_FIELDS:
        return value

    return "name"


def _parse_sort_direction(
    value: str | None,
) -> str:
    """
    Parse a controlled sort direction.
    """
    if value in {"asc", "desc"}:
        return value

    return "asc"


def _parse_active_filter(
    value: str | None,
) -> bool | None:
    """
    Parse the optional classification active-state filter.
    """
    if value == "active":
        return True

    if value == "inactive":
        return False

    return None


def _build_classification_query_options() -> QueryOptions:
    """
    Build controlled query options for Expense Classification
    list operations.
    """
    page = _parse_positive_int(
        request.args.get("page"),
        1,
    )

    page_size = _parse_page_size(
        request.args.get("page_size"),
    )

    sort_by = _parse_sort(
        request.args.get("sort"),
    )

    sort_direction = _parse_sort_direction(
        request.args.get("direction"),
    )

    search = request.args.get(
        "search",
        type=str,
    )

    active_filter = _parse_active_filter(
        request.args.get("active"),
    )

    filters = {}

    if active_filter is not None:
        filters["is_active"] = active_filter

    return QueryOptions(
        page=page,
        page_size=page_size,
        sort_by=sort_by,
        sort_direction=sort_direction,
        search=search,
        filters=filters,
        include_inactive=True,
    )


def _parse_expense_sort(
    value: str | None,
) -> str:
    """
    Parse a controlled Expense sort field.
    """
    if value in _EXPENSE_SORT_FIELDS:
        return value

    return "expense_date"


def _build_expense_query_options() -> QueryOptions:
    """
    Build controlled query options for Expense list operations.
    """
    page = _parse_positive_int(
        request.args.get("page"),
        1,
    )

    page_size = _parse_page_size(
        request.args.get("page_size"),
    )

    sort_by = _parse_expense_sort(
        request.args.get("sort"),
    )

    sort_direction = _parse_sort_direction(
        request.args.get("direction"),
    )

    search = request.args.get(
        "search",
        type=str,
    )

    return QueryOptions(
        page=page,
        page_size=page_size,
        sort_by=sort_by,
        sort_direction=sort_direction,
        search=search,
    )


def _load_expense_classification_choices(
    form: ExpenseForm,
) -> None:
    """
    Populate Expense Classification choices for Expense forms.

    Only active Expense Classifications are available for new or
    edited operational Expense records.
    """
    service = ExpenseClassificationService()

    result = service.paginate(
        QueryOptions(
            page=1,
            page_size=1000,
            sort_by="name",
            sort_direction="asc",
            filters={
                "is_active": True,
            },
            include_inactive=False,
        )
    )

    form.classification_id.choices = [
        (
            classification.id,
            classification.name,
        )
        for classification in result.items
    ]


@expense_bp.route(
    "/classifications/",
    methods=["GET"],
)
@login_required
@require_permission(
    EXPENSE_CLASSIFICATION_READ.name
)
def classifications():
    """
    Render the Expense Classification management list.
    """
    service = ExpenseClassificationService()

    query_options = _build_classification_query_options()

    result = service.paginate(
        query_options
    )

    return render_template(
        "modules/expense/classifications/index.html",
        classifications=result,
        query_options=query_options,
        search=query_options.search or "",
        active=request.args.get("active", ""),
        sort_by=query_options.sort_by,
        sort_direction=query_options.sort_direction,
        page_size=query_options.page_size,
        page_sizes=_PAGE_SIZES,
    )


@expense_bp.route(
    "/classifications/create",
    methods=["GET", "POST"],
)
@login_required
@require_permission(
    EXPENSE_CLASSIFICATION_CREATE.name
)
def create_classification():
    """
    Create an Expense Classification.
    """
    form = ExpenseClassificationForm()

    if form.validate_on_submit():
        service = ExpenseClassificationService()

        classification = service.create(
            ExpenseClassification(
                name=form.name.data,
                code=form.code.data,
                description=form.description.data,
            )
        )

        flash(
            "Expense classification created successfully.",
            "success",
        )

        return redirect(
            url_for(
                "expense.classifications"
            )
        )

    return render_template(
        "modules/expense/classifications/create.html",
        form=form,
    )


@expense_bp.route(
    "/classifications/<int:classification_id>",
    methods=["GET"],
)
@login_required
@require_permission(
    EXPENSE_CLASSIFICATION_READ.name
)
def view_classification(
    classification_id: int,
):
    """
    View an Expense Classification.
    """
    service = ExpenseClassificationService()

    classification = service.get(
        classification_id
    )

    return render_template(
        "modules/expense/classifications/view.html",
        classification=classification,
    )


@expense_bp.route(
    "/classifications/<int:classification_id>/edit",
    methods=["GET", "POST"],
)
@login_required
@require_permission(
    EXPENSE_CLASSIFICATION_UPDATE.name
)
def edit_classification(
    classification_id: int,
):
    """
    Edit an Expense Classification.
    """
    service = ExpenseClassificationService()

    classification = service.get(
        classification_id
    )

    form = ExpenseClassificationForm(
        obj=classification
    )

    if form.validate_on_submit():
        classification.name = form.name.data
        classification.code = form.code.data
        classification.description = form.description.data

        service.update(
            classification
        )

        flash(
            "Expense classification updated successfully.",
            "success",
        )

        return redirect(
            url_for(
                "expense.view_classification",
                classification_id=classification.id,
            )
        )

    return render_template(
        "modules/expense/classifications/edit.html",
        form=form,
        classification=classification,
    )


@expense_bp.route(
    "/classifications/<int:classification_id>/delete",
    methods=["POST"],
)
@login_required
@require_permission(
    EXPENSE_CLASSIFICATION_DELETE.name
)
def delete_classification(
    classification_id: int,
):
    """
    Delete an Expense Classification.
    """
    service = ExpenseClassificationService()

    service.delete(
        classification_id
    )

    flash(
        "Expense classification deleted successfully.",
        "success",
    )

    return redirect(
        url_for(
            "expense.classifications"
        )
    )


@expense_bp.route(
    "/classifications/<int:classification_id>/activate",
    methods=["POST"],
)
@login_required
@require_permission(
    EXPENSE_CLASSIFICATION_UPDATE.name
)
def activate_classification(
    classification_id: int,
):
    """
    Activate an Expense Classification.
    """
    service = ExpenseClassificationService()

    service.activate(
        classification_id
    )

    flash(
        "Expense classification activated successfully.",
        "success",
    )

    return redirect(
        url_for(
            "expense.classifications"
        )
    )


@expense_bp.route(
    "/classifications/<int:classification_id>/deactivate",
    methods=["POST"],
)
@login_required
@require_permission(
    EXPENSE_CLASSIFICATION_UPDATE.name
)
def deactivate_classification(
    classification_id: int,
):
    """
    Deactivate an Expense Classification.
    """
    service = ExpenseClassificationService()

    service.deactivate(
        classification_id
    )

    flash(
        "Expense classification deactivated successfully.",
        "success",
    )

    return redirect(
        url_for(
            "expense.classifications"
        )
    )


@expense_bp.route(
    "/expenses/",
    methods=["GET"],
)
@login_required
@require_permission(
    EXPENSE_READ.name
)
def expenses():
    """
    Render the Expense operational-record management list.
    """
    service = ExpenseService()

    query_options = _build_expense_query_options()

    result = service.paginate(
        query_options
    )

    return render_template(
        "modules/expense/expenses/index.html",
        expenses=result,
        query_options=query_options,
        search=query_options.search or "",
        sort_by=query_options.sort_by,
        sort_direction=query_options.sort_direction,
        page_size=query_options.page_size,
        page_sizes=_PAGE_SIZES,
    )


@expense_bp.route(
    "/expenses/create",
    methods=["GET", "POST"],
)
@login_required
@require_permission(
    EXPENSE_CREATE.name
)
def create_expense():
    """
    Create an Expense operational record.
    """
    form = ExpenseForm()

    _load_expense_classification_choices(
        form
    )

    if form.validate_on_submit():
        service = ExpenseService()

        expense = service.create(
            Expense(
                classification_id=form.classification_id.data,
                description=form.description.data,
                amount=form.amount.data,
                expense_date=form.expense_date.data,
            )
        )

        flash(
            "Expense created successfully.",
            "success",
        )

        return redirect(
            url_for(
                "expense.expenses"
            )
        )

    return render_template(
        "modules/expense/expenses/create.html",
        form=form,
    )


@expense_bp.route(
    "/expenses/<int:expense_id>",
    methods=["GET"],
)
@login_required
@require_permission(
    EXPENSE_READ.name
)
def view_expense(
    expense_id: int,
):
    """
    View an Expense operational record.
    """
    service = ExpenseService()

    expense = service.get(
        expense_id
    )

    return render_template(
        "modules/expense/expenses/view.html",
        expense=expense,
    )


@expense_bp.route(
    "/expenses/<int:expense_id>/edit",
    methods=["GET", "POST"],
)
@login_required
@require_permission(
    EXPENSE_UPDATE.name
)
def edit_expense(
    expense_id: int,
):
    """
    Edit an Expense operational record.
    """
    service = ExpenseService()

    expense = service.get(
        expense_id
    )

    form = ExpenseForm(
        obj=expense
    )

    _load_expense_classification_choices(
        form
    )

    if form.validate_on_submit():
        expense.classification_id = (
            form.classification_id.data
        )
        expense.description = (
            form.description.data
        )
        expense.amount = (
            form.amount.data
        )
        expense.expense_date = (
            form.expense_date.data
        )

        service.update(
            expense
        )

        flash(
            "Expense updated successfully.",
            "success",
        )

        return redirect(
            url_for(
                "expense.view_expense",
                expense_id=expense.id,
            )
        )

    return render_template(
        "modules/expense/expenses/edit.html",
        form=form,
        expense=expense,
    )


@expense_bp.route(
    "/expenses/<int:expense_id>/delete",
    methods=["POST"],
)
@login_required
@require_permission(
    EXPENSE_DELETE.name
)
def delete_expense(
    expense_id: int,
):
    """
    Delete an Expense operational record.
    """
    service = ExpenseService()

    service.delete(
        expense_id
    )

    flash(
        "Expense deleted successfully.",
        "success",
    )

    return redirect(
        url_for(
            "expense.expenses"
        )
    )


__all__ = [
    "activate_classification",
    "classifications",
    "create_classification",
    "create_expense",
    "deactivate_classification",
    "delete_classification",
    "delete_expense",
    "edit_classification",
    "edit_expense",
    "expenses",
    "view_classification",
    "view_expense",
]
