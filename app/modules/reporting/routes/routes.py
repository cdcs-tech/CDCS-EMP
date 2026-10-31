"""
CDCS-EMP Reporting Module

Reporting landing page and read-only report routes.
"""

from datetime import date

from flask import render_template, request
from flask_login import login_required
from sqlalchemy import false, select
from sqlalchemy.exc import MultipleResultsFound

from app.core.data import QueryOptions
from app.core.reporting.permissions import ReportPermissionCode
from app.extensions import db
from app.modules.catering.models import Customer
from app.modules.catering.repositories.catering_event import (
    CateringEventRepository,
)
from app.modules.catering.repositories.catering_revenue import (
    CateringRevenueRepository,
)
from app.modules.catering.repositories.expense_cost_association import (
    CateringExpenseCostAssociationRepository,
)
from app.modules.catering.services.event_profitability import (
    EventProfitabilityService,
)
from app.modules.expense.repositories.expense import ExpenseRepository
from app.modules.reporting.routes import reporting_bp
from app.modules.reporting.services.catering_event_profitability_register import (
    CateringEventProfitabilityRegisterService,
)
from app.security.decorators import require_permission


REGISTER_OPERATIONAL_STATUSES = (
    "REQUESTED",
    "QUOTED",
    "PENDING_CONFIRMATION",
    "CONFIRMED",
    "PLANNING",
    "READY",
    "IN_PRODUCTION",
    "DELIVERED",
    "COMPLETED",
    "CANCELLED",
)


def _get_catering_events():
    """Return a bounded, date-sorted list for the detail report selector."""

    result = CateringEventRepository().paginate(
        QueryOptions(
            page=1,
            page_size=100,
            sort_by="event_date",
            sort_direction="desc",
        )
    )
    return result.items


def _get_active_customers():
    """Return active customers for the register filter."""

    statement = (
        select(Customer)
        .where(Customer.is_deleted == false())
        .order_by(Customer.name.asc(), Customer.id.asc())
    )
    return db.session.execute(statement).scalars().all()


@reporting_bp.route("/")
@login_required
@require_permission(ReportPermissionCode.VIEW)
def index():
    """Render the Reporting landing page."""

    return render_template("modules/reporting/index.html")


@reporting_bp.route("/catering-event-profitability-register")
@login_required
@require_permission(ReportPermissionCode.EXECUTE)
def catering_event_profitability_register():
    """Render the filtered, paginated Catering Event Profitability Register."""

    raw_date_from = request.args.get("date_from", "").strip()
    raw_date_to = request.args.get("date_to", "").strip()
    operational_status = request.args.get("operational_status", "").strip()
    raw_customer_id = request.args.get("customer_id", "").strip()
    raw_page = request.args.get("page", "1").strip()

    report_error = None
    date_from = None
    date_to = None
    customer_id = None
    page = 1

    try:
        if raw_date_from:
            date_from = date.fromisoformat(raw_date_from)

        if raw_date_to:
            date_to = date.fromisoformat(raw_date_to)

        if date_from and date_to and date_from > date_to:
            raise ValueError("Start date cannot be after end date.")

        if operational_status and operational_status not in (
            REGISTER_OPERATIONAL_STATUSES
        ):
            raise ValueError("Choose a valid operational status.")

        if raw_customer_id:
            customer_id = int(raw_customer_id)
            if customer_id <= 0:
                raise ValueError("Choose a valid customer.")

        page = int(raw_page)
        if page < 1:
            raise ValueError("Page must be at least 1.")

    except ValueError as exc:
        report_error = str(exc)

    customers = _get_active_customers()
    register_result = None

    if report_error is None:
        service = CateringEventProfitabilityRegisterService()
        register_result = service.get_register(
            date_from=date_from,
            date_to=date_to,
            operational_status=operational_status or None,
            customer_id=customer_id,
            page=page,
            page_size=service.DEFAULT_PAGE_SIZE,
        )

    return render_template(
        "modules/reporting/catering_event_profitability_register.html",
        register_result=register_result,
        customers=customers,
        operational_statuses=REGISTER_OPERATIONAL_STATUSES,
        selected_date_from=raw_date_from,
        selected_date_to=raw_date_to,
        selected_operational_status=operational_status,
        selected_customer_id=raw_customer_id,
        report_error=report_error,
    ), (400 if report_error else 200)


@reporting_bp.route("/catering-event-profitability")
@login_required
@require_permission(ReportPermissionCode.EXECUTE)
def catering_event_profitability():
    """Select a Catering Event or display its read-only profitability."""

    events = _get_catering_events()
    raw_event_id = request.args.get("event_id", "").strip()

    if not raw_event_id:
        return render_template(
            "modules/reporting/catering_event_profitability.html",
            events=events,
            profitability_result=None,
            profitability_unavailable=False,
            profitability_data_conflict=False,
            selected_event_id=None,
            report_error=None,
        )

    try:
        event_id = int(raw_event_id)
        if event_id <= 0:
            raise ValueError("Event ID must be a positive integer.")
    except ValueError:
        return render_template(
            "modules/reporting/catering_event_profitability.html",
            events=events,
            profitability_result=None,
            profitability_unavailable=False,
            profitability_data_conflict=False,
            selected_event_id=None,
            report_error="Choose a valid Catering Event.",
        ), 400

    service = EventProfitabilityService(
        catering_event_repository=CateringEventRepository(),
        catering_revenue_repository=CateringRevenueRepository(),
        expense_cost_association_repository=(
            CateringExpenseCostAssociationRepository()
        ),
        expense_repository=ExpenseRepository(),
    )

    try:
        result = service.calculate_for_event(event_id)
    except MultipleResultsFound:
        return render_template(
            "modules/reporting/catering_event_profitability.html",
            events=events,
            profitability_result=None,
            profitability_unavailable=True,
            profitability_data_conflict=True,
            selected_event_id=event_id,
            report_error=None,
        )
    except ValueError:
        return render_template(
            "modules/reporting/catering_event_profitability.html",
            events=events,
            profitability_result=None,
            profitability_unavailable=True,
            profitability_data_conflict=False,
            selected_event_id=event_id,
            report_error=None,
        )

    return render_template(
        "modules/reporting/catering_event_profitability.html",
        events=events,
        profitability_result=result,
        profitability_unavailable=False,
        profitability_data_conflict=False,
        selected_event_id=event_id,
        report_error=None,
    )
