"""
CDCS Enterprise Management Platform (CDCS-EMP)

Catering Module

Routes.
"""

from flask import (
    Blueprint,
    current_app,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)
from flask_login import current_user
from flask_login import login_required

from app.core.crud.exceptions import (
    EntityNotFoundException,
    EntityValidationException,
)

from app.core.crud.transaction import SQLAlchemyTransactionManager

from app.core.data import QueryOptions

from sqlalchemy.exc import MultipleResultsFound

from app.core.execution.context import ExecutionContext

from app.security.decorators import require_permission

from app.modules.catering.models import CateringQuotation
from app.modules.catering.models import CateringQuotationLine
from app.modules.catering.models import EventRequirement
from app.modules.catering.models import CateringPurchaseRequirement
from app.modules.catering.models import CateringExpenseCostAssociation

from app.modules.catering.forms import (
    CateringEventForm,
    CateringQuotationForm,
    CateringQuotationLineForm,
    CateringRequestForm,
    CustomerForm,
    EventRequirementForm,
    CateringPurchaseRequirementForm,
    InventoryLocationForm,
    ProductCategoryForm,
    ProductForm,
    StockItemForm,
    StockMovementForm,
    StockTransferForm,
    CateringRevenueForm,
    CateringExpenseCostAssociationForm,
)

from app.modules.catering.security import (
    CATERING_INVENTORY_LOCATION_CREATE,
    CATERING_INVENTORY_LOCATION_READ,
    CATERING_PRODUCT_CATEGORY_CREATE,
    CATERING_PRODUCT_CATEGORY_READ,
    CATERING_PRODUCT_CATEGORY_UPDATE,
    CATERING_PRODUCT_CREATE,
    CATERING_PRODUCT_READ,
    CATERING_PRODUCT_UPDATE,
    CATERING_STOCK_BALANCE_READ,
    CATERING_STOCK_ITEM_CREATE,
    CATERING_STOCK_ITEM_READ,
    CATERING_STOCK_MOVEMENT_CREATE,
    CATERING_STOCK_MOVEMENT_POST,
    CATERING_STOCK_MOVEMENT_READ,
    CATERING_STOCK_TRANSFER_CREATE,
    CATERING_STOCK_TRANSFER_POST,
    CATERING_STOCK_TRANSFER_READ,
    CATERING_CUSTOMER_CREATE,
    CATERING_CUSTOMER_DELETE,
    CATERING_CUSTOMER_READ,
    CATERING_CUSTOMER_UPDATE,
    CATERING_REQUEST_CANCEL,
    CATERING_REQUEST_CREATE,
    CATERING_REQUEST_DELETE,
    CATERING_REQUEST_READ,
    CATERING_REQUEST_SUBMIT,
    CATERING_REQUEST_UPDATE,
    CATERING_EVENT_CANCEL,
    CATERING_EVENT_CREATE,
    CATERING_EVENT_DELETE,
    CATERING_EVENT_READ,
    CATERING_EVENT_UPDATE,
    CATERING_EVENT_PLAN,
    CATERING_EVENT_READY,
    CATERING_EVENT_START_PRODUCTION,
    CATERING_EVENT_DELIVER,
    CATERING_EVENT_COMPLETE,
    CATERING_QUOTATION_ACCEPT,
    CATERING_QUOTATION_CREATE,
    CATERING_QUOTATION_DECLINE,
    CATERING_QUOTATION_DELETE,
    CATERING_QUOTATION_EXPIRE,
    CATERING_QUOTATION_ISSUE,
    CATERING_QUOTATION_READ,
    CATERING_QUOTATION_UPDATE,
    CATERING_EVENT_QUOTE,
    CATERING_EVENT_CONFIRM,
    CATERING_EXPENSE_COST_ASSOCIATION_CREATE,
    CATERING_EVENT_REQUIREMENT_CANCEL,
    CATERING_EVENT_REQUIREMENT_CREATE,
    CATERING_EVENT_REQUIREMENT_IDENTIFY,
    CATERING_EVENT_REQUIREMENT_READ,
    CATERING_EVENT_REQUIREMENT_READY,
    CATERING_EVENT_REQUIREMENT_UPDATE,
    CATERING_PURCHASE_REQUIREMENT_CREATE,
    CATERING_PURCHASE_REQUIREMENT_SUBMIT_TO_PROCUREMENT,
    CATERING_REVENUE_CREATE,
    CATERING_REVENUE_READ,
    CATERING_REVENUE_UPDATE,
    CATERING_REVENUE_ESTABLISH_ELIGIBILITY,
    CATERING_REVENUE_RECOGNIZE,
    CATERING_REVENUE_CANCEL,
)

from app.modules.catering.services import (
    InventoryLocationService,
    ProductCategoryService,
    ProductService,
    StockBalanceService,
    StockItemService,
    StockMovementService,
    StockTransferService,
    CustomerService,
    CateringRequestService,
    CateringEventService,
    CateringRequestEventCoordinationService,
    CateringQuotationService,
    CateringQuotationEventCoordinationService,
    EventRequirementService,
    CateringPurchaseRequirementService,
    CateringProcurementHandoffService,
    CateringRevenueService,
    CateringExpenseCostAssociationService,
)

from app.modules.catering.services.event_requirement_fulfilment import (
    EventRequirementFulfilmentVerifier,
)

from app.modules.catering.services.event_profitability import (
    EventProfitabilityService,
)

from app.modules.catering.security.authorization import (
    CateringAuthorizationAdapter,
)

from app.modules.catering.commands import (
    RecognizeCateringRevenueCommand,
)

from app.modules.catering.workflows.catering_quotation import (
    CateringQuotationWorkflow,
)

from app.modules.catering.workflows.catering_revenue import (
    CateringRevenueWorkflow,
)

from app.modules.catering.repositories.catering_quotation import (
    CateringQuotationRepository,
)

from app.modules.catering.repositories.catering_event import (
    CateringEventRepository,
)

from app.modules.catering.repositories.event_requirement import (
    EventRequirementRepository,
)

from app.modules.catering.repositories.catering_purchase_requirement import (
    CateringPurchaseRequirementRepository,
)

from app.modules.catering.repositories.catering_revenue import (
    CateringRevenueRepository,
)

from app.modules.catering.repositories.expense_cost_association import (
    CateringExpenseCostAssociationRepository,
)

from app.modules.expense.repositories.expense import ExpenseRepository

from . import catering_bp


_CUSTOMER_SORT_FIELDS = {
    "name",
    "customer_type",
    "phone",
    "email",
    "status",
}

_CATEGORY_SORT_FIELDS = {
    "name",
    "code",
    "is_active",
}

_PRODUCT_SORT_FIELDS = {
    "name",
    "code",
    "unit",
    "is_active",
}

_STOCK_ITEM_SORT_FIELDS = {
    "product_id",
    "minimum_level",
    "reorder_level",
    "is_active",
}

_STOCK_BALANCE_SORT_FIELDS = {
    "stock_item_id",
    "location_id",
    "quantity",
}

_STOCK_MOVEMENT_SORT_FIELDS = {
    "stock_item_id",
    "location_id",
    "movement_type",
    "quantity",
    "status",
    "occurred_at",
}

_STOCK_TRANSFER_SORT_FIELDS = {
    "stock_item_id",
    "source_location_id",
    "destination_location_id",
    "quantity",
    "reference",
    "status",
    "occurred_at",
}

_LOCATION_SORT_FIELDS = {
    "code",
    "name",
    "is_active",
}

_ALLOWED_PAGE_SIZES = {
    10,
    25,
    50,
    100,
}


def _parse_positive_int(
    value,
    default: int,
) -> int:
    """
    Parse a positive integer query parameter.

    Invalid, missing, or non-positive values fall back
    to the supplied default.
    """

    try:
        parsed = int(value)
    except (TypeError, ValueError):
        return default

    return parsed if parsed >= 1 else default


def _parse_page_size(
    value,
) -> int:
    """
    Parse a controlled page-size query parameter.

    Unsupported values fall back to the default page size.
    """

    parsed = _parse_positive_int(
        value,
        25,
    )

    return (
        parsed
        if parsed in _ALLOWED_PAGE_SIZES
        else 25
    )


def _parse_sort(
    value,
    allowed_fields: set[str],
    default: str,
) -> str:
    """
    Parse a controlled sort field.
    """

    if value in allowed_fields:
        return value

    return default


def _parse_sort_direction(
    value,
) -> str:
    """
    Parse a controlled sort direction.
    """

    return (
        value
        if value in {"asc", "desc"}
        else "asc"
    )


def _parse_status_filter(
    value,
) -> dict[str, bool]:
    """
    Translate the shared Catering status query parameter into
    an explicit is_active repository filter.

    The default behavior is active records only.
    """

    if value == "inactive":
        return {
            "is_active": False,
        }

    if value == "all":
        return {}

    return {
        "is_active": True,
    }


def _parse_customer_status_filter(
    value,
) -> dict[str, str]:
    """
    Translate the Customer status query parameter into
    an explicit status repository filter.

    Customer uses a status field rather than the shared
    is_active lifecycle field used by other Catering entities.
    The default behavior is active customers only.
    """

    if value == "inactive":
        return {
            "status": "INACTIVE",
        }

    if value == "all":
        return {}

    return {
        "status": "ACTIVE",
    }


def _build_customer_query_options() -> QueryOptions:
    """
    Build controlled query options for Customers.
    """

    return QueryOptions(
        page=_parse_positive_int(
            request.args.get("page"),
            1,
        ),
        page_size=_parse_page_size(
            request.args.get("page_size"),
        ),
        sort_by=_parse_sort(
            request.args.get("sort"),
            _CUSTOMER_SORT_FIELDS,
            "name",
        ),
        sort_direction=_parse_sort_direction(
            request.args.get("direction"),
        ),
        search=request.args.get(
            "search"
        ),
        filters=_parse_customer_status_filter(
            request.args.get("status"),
        ),
    )


def _build_category_query_options() -> QueryOptions:
    """
    Build controlled query options for Product Categories.
    """

    return QueryOptions(
        page=_parse_positive_int(
            request.args.get("page"),
            1,
        ),
        page_size=_parse_page_size(
            request.args.get("page_size"),
        ),
        sort_by=_parse_sort(
            request.args.get("sort"),
            _CATEGORY_SORT_FIELDS,
            "name",
        ),
        sort_direction=_parse_sort_direction(
            request.args.get("direction"),
        ),
        search=request.args.get(
            "search"
        ),
        filters=_parse_status_filter(
            request.args.get("status"),
        ),
    )


def _build_product_query_options() -> QueryOptions:
    """
    Build controlled query options for Products.
    """

    filters = _parse_status_filter(
        request.args.get("status"),
    )

    category_id = request.args.get(
        "category_id"
    )

    if category_id:
        try:
            parsed_category_id = int(
                category_id
            )
        except (TypeError, ValueError):
            parsed_category_id = None

        if (
            parsed_category_id is not None
            and parsed_category_id >= 1
        ):
            filters["category_id"] = parsed_category_id

    return QueryOptions(
        page=_parse_positive_int(
            request.args.get("page"),
            1,
        ),
        page_size=_parse_page_size(
            request.args.get("page_size"),
        ),
        sort_by=_parse_sort(
            request.args.get("sort"),
            _PRODUCT_SORT_FIELDS,
            "name",
        ),
        sort_direction=_parse_sort_direction(
            request.args.get("direction"),
        ),
        search=request.args.get(
            "search"
        ),
        filters=filters,
    )


def _build_stock_item_query_options() -> QueryOptions:
    """
    Build controlled query options for Stock Items.
    """

    return QueryOptions(
        page=_parse_positive_int(
            request.args.get("page"),
            1,
        ),
        page_size=_parse_page_size(
            request.args.get("page_size"),
        ),
        sort_by=_parse_sort(
            request.args.get("sort"),
            _STOCK_ITEM_SORT_FIELDS,
            "product_id",
        ),
        sort_direction=_parse_sort_direction(
            request.args.get("direction"),
        ),
        search=request.args.get(
            "search"
        ),
        filters=_parse_status_filter(
            request.args.get("status"),
        ),
    )


def _build_location_query_options() -> QueryOptions:
    """
    Build controlled query options for Inventory Locations.
    """

    return QueryOptions(
        page=_parse_positive_int(
            request.args.get("page"),
            1,
        ),
        page_size=_parse_page_size(
            request.args.get("page_size"),
        ),
        sort_by=_parse_sort(
            request.args.get("sort"),
            _LOCATION_SORT_FIELDS,
            "name",
        ),
        sort_direction=_parse_sort_direction(
            request.args.get("direction"),
        ),
        search=request.args.get(
            "search"
        ),
        filters=_parse_status_filter(
            request.args.get("status"),
        ),
    )


def _build_stock_balance_query_options() -> QueryOptions:
    """
    Build controlled query options for Stock Balances.
    """

    return QueryOptions(
        page=_parse_positive_int(
            request.args.get("page"),
            1,
        ),
        page_size=_parse_page_size(
            request.args.get("page_size"),
        ),
        sort_by=_parse_sort(
            request.args.get("sort"),
            _STOCK_BALANCE_SORT_FIELDS,
            "stock_item_id",
        ),
        sort_direction=_parse_sort_direction(
            request.args.get("direction"),
        ),
        search=request.args.get(
            "search"
        ),
    )


def _build_stock_movement_query_options() -> QueryOptions:
    """
    Build controlled query options for Stock Movements.
    """

    return QueryOptions(
        page=_parse_positive_int(
            request.args.get("page"),
            1,
        ),
        page_size=_parse_page_size(
            request.args.get("page_size"),
        ),
        sort_by=_parse_sort(
            request.args.get("sort"),
            _STOCK_MOVEMENT_SORT_FIELDS,
            "occurred_at",
        ),
        sort_direction=_parse_sort_direction(
            request.args.get("direction"),
        ),
        search=request.args.get(
            "search"
        ),
    )


def _build_stock_transfer_query_options() -> QueryOptions:
    """
    Build controlled query options for Stock Transfers.
    """

    return QueryOptions(
        page=_parse_positive_int(
            request.args.get("page"),
            1,
        ),
        page_size=_parse_page_size(
            request.args.get("page_size"),
        ),
        sort_by=_parse_sort(
            request.args.get("sort"),
            _STOCK_TRANSFER_SORT_FIELDS,
            "occurred_at",
        ),
        sort_direction=_parse_sort_direction(
            request.args.get("direction"),
        ),
        search=request.args.get(
            "search"
        ),
    )


def _build_catering_authorization_adapter() -> CateringAuthorizationAdapter:
    """
    Build the Catering service authorization adapter.

    The route layer supplies the authenticated subject's existing
    enterprise permission evaluator while keeping Catering services
    independent of Flask request context.
    """

    return CateringAuthorizationAdapter(
        lambda subject, permission_code: subject.has_permission(
            permission_code
        )
    )


@catering_bp.route("/")
@login_required
@require_permission(
    CATERING_PRODUCT_CATEGORY_READ.name
)
def index():
    """
    Render the Catering module landing page.
    """

    return render_template(
        "modules/catering/index.html",
        can_read_customers=current_user.has_permission(
            CATERING_CUSTOMER_READ.name
        ),
                can_read_requests=current_user.has_permission(
            CATERING_REQUEST_READ.name
        ),
        can_read_events=current_user.has_permission(
            CATERING_EVENT_READ.name
        ),
        can_read_revenues=current_user.has_permission(
            CATERING_REVENUE_READ.name
        ),
        can_read_categories=current_user.has_permission(
            CATERING_PRODUCT_CATEGORY_READ.name
        ),
        can_read_products=current_user.has_permission(
            CATERING_PRODUCT_READ.name
        ),
        can_read_stock_items=current_user.has_permission(
            CATERING_STOCK_ITEM_READ.name
        ),
        can_read_inventory_locations=current_user.has_permission(
            CATERING_INVENTORY_LOCATION_READ.name
        ),
        can_read_stock_balances=current_user.has_permission(
            CATERING_STOCK_BALANCE_READ.name
        ),
        can_read_stock_movements=current_user.has_permission(
            CATERING_STOCK_MOVEMENT_READ.name
        ),
        can_read_stock_transfers=current_user.has_permission(
            CATERING_STOCK_TRANSFER_READ.name
        ),
    )


@catering_bp.route(
    "/customers/"
)
@login_required
@require_permission(
    CATERING_CUSTOMER_READ.name
)
def customers():
    """
    Render the Customer management list.
    """

    service = CustomerService()

    result = service.paginate(
        _build_customer_query_options()
    )

    return render_template(
        "modules/catering/customers/index.html",
        customers=result.items,
        pagination=result,
    )


@catering_bp.route(
    "/customers/create",
    methods=["GET", "POST"],
)
@login_required
@require_permission(
    CATERING_CUSTOMER_CREATE.name
)
def create_customer():
    """
    Create a Catering Customer.
    """

    form = CustomerForm()

    if form.validate_on_submit():

        service = CustomerService()

        customer = service.create(
            service.repository.model(
                name=form.name.data,
                customer_type=form.customer_type.data,
                phone=form.phone.data,
                email=form.email.data,
                address=form.address.data,
                notes=form.notes.data,
            )
        )

        flash(
            "Customer created successfully.",
            "success",
        )

        return redirect(
            url_for(
                "catering.customers"
            )
        )

    return render_template(
        "modules/catering/customers/create.html",
        form=form,
    )


@catering_bp.route(
    "/customers/<int:customer_id>"
)
@login_required
@require_permission(
    CATERING_CUSTOMER_READ.name
)
def view_customer(
    customer_id,
):
    """
    Render a Customer detail view.
    """

    service = CustomerService()

    try:
        customer = service.get(
            customer_id
        )
    except EntityNotFoundException:
        flash(
            "Customer not found.",
            "danger",
        )

        return redirect(
            url_for(
                "catering.customers"
            )
        )

    return render_template(
        "modules/catering/customers/view.html",
        customer=customer,
    )


@catering_bp.route(
    "/customers/<int:customer_id>/edit",
    methods=["GET", "POST"],
)
@login_required
@require_permission(
    CATERING_CUSTOMER_UPDATE.name
)
def edit_customer(
    customer_id,
):
    """
    Edit a Catering Customer.
    """

    service = CustomerService()

    try:
        customer = service.get(
            customer_id
        )
    except EntityNotFoundException:
        flash(
            "Customer not found.",
            "danger",
        )

        return redirect(
            url_for(
                "catering.customers"
            )
        )

    form = CustomerForm(
        obj=customer
    )

    if form.validate_on_submit():

        customer.name = form.name.data
        customer.customer_type = (
            form.customer_type.data
        )
        customer.phone = form.phone.data
        customer.email = form.email.data
        customer.address = form.address.data
        customer.notes = form.notes.data

        service.update(
            customer
        )

        flash(
            "Customer updated successfully.",
            "success",
        )

        return redirect(
            url_for(
                "catering.view_customer",
                customer_id=customer.id,
            )
        )

    return render_template(
        "modules/catering/customers/edit.html",
        form=form,
        customer=customer,
    )


@catering_bp.route(
    "/customers/<int:customer_id>/activate",
    methods=["POST"],
)
@login_required
@require_permission(
    CATERING_CUSTOMER_UPDATE.name
)
def activate_customer(
    customer_id,
):
    """
    Activate a Catering Customer.
    """

    service = CustomerService()

    try:
        customer = service.activate(
            customer_id
        )
    except EntityNotFoundException:
        flash(
            "Customer not found.",
            "danger",
        )

        return redirect(
            url_for(
                "catering.customers"
            )
        )

    flash(
        "Customer activated successfully.",
        "success",
    )

    return redirect(
        url_for(
            "catering.view_customer",
            customer_id=customer.id,
        )
    )


@catering_bp.route(
    "/customers/<int:customer_id>/deactivate",
    methods=["POST"],
)
@login_required
@require_permission(
    CATERING_CUSTOMER_UPDATE.name
)
def deactivate_customer(
    customer_id,
):
    """
    Deactivate a Catering Customer.
    """

    service = CustomerService()

    try:
        customer = service.deactivate(
            customer_id
        )
    except EntityNotFoundException:
        flash(
            "Customer not found.",
            "danger",
        )

        return redirect(
            url_for(
                "catering.customers"
            )
        )

    flash(
        "Customer deactivated successfully.",
        "success",
    )

    return redirect(
        url_for(
            "catering.view_customer",
            customer_id=customer.id,
        )
    )


@catering_bp.route(
    "/revenues/"
)
@login_required
@require_permission(
    CATERING_REVENUE_READ.name
)
def revenues():
    """
    Render the Catering Revenue list.
    """

    service = CateringRevenueService(
        authorization_adapter=_build_catering_authorization_adapter(),
    )

    result = service.repository.paginate(
        QueryOptions(
            page=_parse_positive_int(
                request.args.get("page"),
                1,
            ),
            page_size=_parse_page_size(
                request.args.get("page_size")
            ),
            sort_by="revenue_date",
            sort_direction=_parse_sort_direction(
                request.args.get("direction")
            ),
        )
    )

    return render_template(
        "modules/catering/revenues/index.html",
        revenues=result.items,
        pagination=result,
    )


@catering_bp.route(
    "/revenues/create",
    methods=["GET", "POST"],
)
@login_required
@require_permission(
    CATERING_REVENUE_CREATE.name
)
def create_revenue():
    """
    Create a Catering Revenue record.
    """

    form = CateringRevenueForm()

    customers = CustomerService().paginate(
        QueryOptions(
            page=1,
            page_size=100,
            sort_by="name",
            sort_direction="asc",
        )
    )

    events = CateringEventService(
        authorization_adapter=_build_catering_authorization_adapter(),
    ).repository.paginate(
        QueryOptions(
            page=1,
            page_size=100,
            sort_by="event_date",
            sort_direction="desc",
        )
    )

    form.customer_id.choices = [
        (customer.id, customer.name)
        for customer in customers.items
    ]

    form.event_id.choices = [
        (
            event.id,
            f"Event #{event.id} — {event.event_date} — {event.status}",
        )
        for event in events.items
    ]

    if form.validate_on_submit():

        service = CateringRevenueService(
            authorization_adapter=_build_catering_authorization_adapter(),
        )

        revenue = service.create(
            service.repository.model(
                revenue_reference=form.revenue_reference.data,
                source_type=form.source_type.data,
                source_reference=form.source_reference.data,
                customer_id=form.customer_id.data,
                event_id=form.event_id.data,
                amount=form.amount.data,
                currency=form.currency.data,
                revenue_date=form.revenue_date.data,
                revenue_classification=form.revenue_classification.data,
                status=CateringRevenueWorkflow.DRAFT,
            ),
            subject=current_user,
        )

        flash(
            "Catering Revenue created successfully.",
            "success",
        )

        return redirect(
            url_for(
                "catering.view_revenue",
                revenue_id=revenue.id,
            )
        )

    return render_template(
        "modules/catering/revenues/create.html",
        form=form,
    )


@catering_bp.route(
    "/revenues/<int:revenue_id>"
)
@login_required
@require_permission(
    CATERING_REVENUE_READ.name
)
def view_revenue(
    revenue_id,
):
    """
    Render a Catering Revenue detail view.
    """

    service = CateringRevenueService(
        authorization_adapter=_build_catering_authorization_adapter(),
    )

    try:
        revenue = service.get(
            revenue_id
        )
    except EntityNotFoundException:
        flash(
            "Catering Revenue not found.",
            "danger",
        )

        return redirect(
            url_for(
                "catering.revenues"
            )
        )

    return render_template(
        "modules/catering/revenues/view.html",
        revenue=revenue,
    )


@catering_bp.route(
    "/revenues/<int:revenue_id>/edit",
    methods=["GET", "POST"],
)
@login_required
@require_permission(
    CATERING_REVENUE_UPDATE.name
)
def edit_revenue(
    revenue_id,
):
    """
    Edit a DRAFT Catering Revenue record.
    """

    service = CateringRevenueService(
        authorization_adapter=_build_catering_authorization_adapter(),
    )

    try:
        revenue = service.get(
            revenue_id
        )
    except EntityNotFoundException:
        flash(
            "Catering Revenue not found.",
            "danger",
        )

        return redirect(
            url_for(
                "catering.revenues"
            )
        )

    form = CateringRevenueForm(
        obj=revenue
    )

    customers = CustomerService().paginate(
        QueryOptions(
            page=1,
            page_size=100,
            sort_by="name",
            sort_direction="asc",
        )
    )

    events = CateringEventService(
        authorization_adapter=_build_catering_authorization_adapter(),
    ).repository.paginate(
        QueryOptions(
            page=1,
            page_size=100,
            sort_by="event_date",
            sort_direction="desc",
        )
    )

    form.customer_id.choices = [
        (customer.id, customer.name)
        for customer in customers.items
    ]

    form.event_id.choices = [
        (
            event.id,
            f"Event #{event.id} — {event.event_date} — {event.status}",
        )
        for event in events.items
    ]

    if form.validate_on_submit():

        revenue.revenue_reference = (
            form.revenue_reference.data
        )
        revenue.source_type = (
            form.source_type.data
        )
        revenue.source_reference = (
            form.source_reference.data
        )
        revenue.customer_id = (
            form.customer_id.data
        )
        revenue.event_id = (
            form.event_id.data
        )
        revenue.amount = (
            form.amount.data
        )
        revenue.currency = (
            form.currency.data
        )
        revenue.revenue_date = (
            form.revenue_date.data
        )
        revenue.revenue_classification = (
            form.revenue_classification.data
        )

        service.update(
            revenue,
            subject=current_user,
        )

        flash(
            "Catering Revenue updated successfully.",
            "success",
        )

        return redirect(
            url_for(
                "catering.view_revenue",
                revenue_id=revenue.id,
            )
        )

    return render_template(
        "modules/catering/revenues/edit.html",
        form=form,
        revenue=revenue,
    )


@catering_bp.route(
    "/revenues/<int:revenue_id>/establish-eligibility",
    methods=["POST"],
)
@login_required
@require_permission(
    CATERING_REVENUE_ESTABLISH_ELIGIBILITY.name
)
def establish_revenue_eligibility(
    revenue_id,
):
    """
    Establish Catering Revenue recognition eligibility.
    """

    service = CateringRevenueService(
        authorization_adapter=_build_catering_authorization_adapter(),
    )

    try:
        revenue = service.get(
            revenue_id
        )

        service.establish_eligibility(
            revenue,
            subject=current_user,
        )

        flash(
            "Catering Revenue marked eligible for recognition.",
            "success",
        )

    except (
        EntityNotFoundException,
        EntityValidationException,
        ValueError,
    ) as exc:
        flash(
            str(exc),
            "danger",
        )

    return redirect(
        url_for(
            "catering.view_revenue",
            revenue_id=revenue_id,
        )
    )


@catering_bp.route(
    "/revenues/<int:revenue_id>/recognize",
    methods=["POST"],
)
@login_required
@require_permission(CATERING_REVENUE_RECOGNIZE.name)
def recognize_revenue(revenue_id):
    """
    Recognize Catering Revenue through the enterprise execution framework.
    """
    command = RecognizeCateringRevenueCommand(
        revenue_id
    )

    context = ExecutionContext(
        user_id=str(current_user.id),
        module_name="CATERING",
        operation="catering.revenue.recognize",
    )

    dispatcher = current_app.extensions[
        "command_dispatcher"
    ]

    result = dispatcher.dispatch(
        command,
        context,
    )

    flash(
        result.message,
        "success" if result.success else "danger",
    )

    return redirect(
        url_for(
            "catering.view_revenue",
            revenue_id=revenue_id,
        )
    )


@catering_bp.route(
    "/revenues/<int:revenue_id>/cancel",
    methods=["POST"],
)
@login_required
@require_permission(
    CATERING_REVENUE_CANCEL.name
)
def cancel_revenue(
    revenue_id,
):
    """
    Cancel a Catering Revenue record.
    """

    service = CateringRevenueService(
        authorization_adapter=_build_catering_authorization_adapter(),
    )

    try:
        revenue = service.get(
            revenue_id
        )

        service.cancel(
            revenue,
            subject=current_user,
        )

        flash(
            "Catering Revenue cancelled successfully.",
            "success",
        )

    except (
        EntityNotFoundException,
        EntityValidationException,
        ValueError,
    ) as exc:
        flash(
            str(exc),
            "danger",
        )

    return redirect(
        url_for(
            "catering.view_revenue",
            revenue_id=revenue_id,
        )
    )


@catering_bp.route(
    "/requests/"
)
@login_required
@require_permission(
    CATERING_REQUEST_READ.name
)
def catering_requests():
    """
    Render the Catering Request management list.
    """

    service = CateringRequestService(
        authorization_adapter=_build_catering_authorization_adapter(),
    )

    result = service.repository.paginate(
        QueryOptions(
            page=_parse_positive_int(
                request.args.get("page"),
                1,
            ),
            page_size=_parse_page_size(
                request.args.get("page_size"),
            ),
            sort_by="request_date",
            sort_direction=_parse_sort_direction(
                request.args.get("direction"),
            ),
        )
    )

    return render_template(
        "modules/catering/requests/index.html",
        requests=result.items,
        pagination=result,
    )


@catering_bp.route(
    "/events/create-from-request",
)
@login_required
@require_permission(
    CATERING_REQUEST_READ.name
)
def select_catering_request_for_event():
    """
    Select a submitted Catering Request for Event creation.
    """

    service = CateringRequestService(
        authorization_adapter=_build_catering_authorization_adapter(),
    )

    result = service.repository.paginate(
        QueryOptions(
            page=_parse_positive_int(
                request.args.get("page"),
                1,
            ),
            page_size=_parse_page_size(
                request.args.get("page_size"),
            ),
            filters={
                "status": "SUBMITTED",
            },
            sort_by="request_date",
            sort_direction=_parse_sort_direction(
                request.args.get("direction"),
            ),
        )
    )

    return render_template(
        "modules/catering/events/select_request.html",
        requests=result.items,
        pagination=result,
    )


@catering_bp.route(
    "/requests/create",
    methods=["GET", "POST"],
)
@login_required
@require_permission(
    CATERING_REQUEST_CREATE.name
)
def create_catering_request():
    """
    Create a Catering Request.
    """

    service = CateringRequestService(
        authorization_adapter=_build_catering_authorization_adapter(),
    )

    form = CateringRequestForm()

    customers = CustomerService().paginate(
        QueryOptions(
            page=1,
            page_size=100,
            filters={
                "status": "ACTIVE",
            },
            sort_by="name",
            sort_direction="asc",
        )
    )

    form.customer_id.choices = [
        (
            customer.id,
            customer.name,
        )
        for customer in customers.items
    ]

    if form.validate_on_submit():

        catering_request = service.create(
            service.repository.model(
                customer_id=form.customer_id.data,
                request_date=form.request_date.data,
                requested_service=form.requested_service.data,
                service_date=form.service_date.data,
                attendance=form.attendance.data,
                requirements=form.requirements.data,
                notes=form.notes.data,
            ),
            subject=current_user,
        )

        flash(
            "Catering Request created successfully.",
            "success",
        )

        return redirect(
            url_for(
                "catering.view_catering_request",
                request_id=catering_request.id,
            )
        )

    return render_template(
        "modules/catering/requests/create.html",
        form=form,
    )


@catering_bp.route(
    "/requests/<int:request_id>"
)
@login_required
@require_permission(
    CATERING_REQUEST_READ.name
)
def view_catering_request(
    request_id,
):
    """
    Render a Catering Request detail view.
    """

    service = CateringRequestService(
        authorization_adapter=_build_catering_authorization_adapter(),
    )

    try:
        catering_request = service.get(
            request_id
        )
    except EntityNotFoundException:
        flash(
            "Catering Request not found.",
            "danger",
        )

        return redirect(
            url_for(
                "catering.catering_requests"
            )
        )

    return render_template(
        "modules/catering/requests/view.html",
        catering_request=catering_request,
    )


@catering_bp.route(
    "/requests/<int:request_id>/edit",
    methods=["GET", "POST"],
)
@login_required
@require_permission(
    CATERING_REQUEST_UPDATE.name
)
def edit_catering_request(
    request_id,
):
    """
    Edit a Catering Request.
    """

    service = CateringRequestService(
        authorization_adapter=_build_catering_authorization_adapter(),
    )

    try:
        catering_request = service.get(
            request_id
        )
    except EntityNotFoundException:
        flash(
            "Catering Request not found.",
            "danger",
        )

        return redirect(
            url_for(
                "catering.catering_requests"
            )
        )

    customers = CustomerService().paginate(
        QueryOptions(
            page=1,
            page_size=100,
            filters={
                "status": "ACTIVE",
            },
            sort_by="name",
            sort_direction="asc",
        )
    )

    form = CateringRequestForm(
        obj=catering_request
    )

    form.customer_id.choices = [
        (
            customer.id,
            customer.name,
        )
        for customer in customers.items
    ]

    if form.validate_on_submit():

        catering_request.customer_id = (
            form.customer_id.data
        )
        catering_request.request_date = (
            form.request_date.data
        )
        catering_request.requested_service = (
            form.requested_service.data
        )
        catering_request.service_date = (
            form.service_date.data
        )
        catering_request.attendance = (
            form.attendance.data
        )
        catering_request.requirements = (
            form.requirements.data
        )
        catering_request.notes = (
            form.notes.data
        )

        service.update(
            catering_request,
            subject=current_user,
        )

        flash(
            "Catering Request updated successfully.",
            "success",
        )

        return redirect(
            url_for(
                "catering.view_catering_request",
                request_id=catering_request.id,
            )
        )

    return render_template(
        "modules/catering/requests/edit.html",
        form=form,
        catering_request=catering_request,
    )



@catering_bp.route(
    "/requests/<int:request_id>/submit",
    methods=["POST"],
)
@login_required
@require_permission(
    CATERING_REQUEST_SUBMIT.name
)
def submit_catering_request(request_id):
    """Submit a Catering Request."""

    service = CateringRequestService(
        authorization_adapter=_build_catering_authorization_adapter(),
    )

    try:
        catering_request = service.get(request_id)
        service.submit(
            catering_request,
            subject=current_user,
        )
    except EntityNotFoundException:
        flash("Catering Request not found.", "danger")
        return redirect(url_for("catering.catering_requests"))
    except PermissionError:
        flash(
            "You are not authorized to submit this Catering Request.",
            "danger",
        )
    except EntityValidationException as exc:
        flash(str(exc), "danger")
    except ValueError as exc:
        flash(str(exc), "danger")
    else:
        flash("Catering Request submitted successfully.", "success")

    return redirect(
        url_for(
            "catering.view_catering_request",
            request_id=request_id,
        )
    )


@catering_bp.route(
    "/requests/<int:request_id>/cancel",
    methods=["POST"],
)
@login_required
@require_permission(
    CATERING_REQUEST_CANCEL.name
)
def cancel_catering_request(
    request_id,
):
    """
    Cancel a Catering Request.
    """

    service = CateringRequestService(
        authorization_adapter=_build_catering_authorization_adapter(),
    )

    try:
        catering_request = service.get(
            request_id
        )

        service.cancel(
            catering_request,
            subject=current_user,
        )
    except EntityNotFoundException:
        flash(
            "Catering Request not found.",
            "danger",
        )

        return redirect(
            url_for(
                "catering.catering_requests"
            )
        )

    flash(
        "Catering Request cancelled successfully.",
        "success",
    )

    return redirect(
        url_for(
            "catering.view_catering_request",
            request_id=request_id,
        )
    )


@catering_bp.route(
    "/requests/<int:request_id>/delete",
    methods=["POST"],
)
@login_required
@require_permission(
    CATERING_REQUEST_DELETE.name
)
def delete_catering_request(
    request_id,
):
    """
    Delete a Catering Request.
    """

    service = CateringRequestService(
        authorization_adapter=_build_catering_authorization_adapter(),
    )

    try:
        service.delete(
            request_id,
            subject=current_user,
        )
    except EntityNotFoundException:
        flash(
            "Catering Request not found.",
            "danger",
        )

        return redirect(
            url_for(
                "catering.catering_requests"
            )
        )

    flash(
        "Catering Request deleted successfully.",
        "success",
    )

    return redirect(
        url_for(
            "catering.catering_requests"
        )
    )


@catering_bp.route("/quotations")
@login_required
@require_permission(CATERING_QUOTATION_READ.name)
def catering_quotations():
    """List Catering quotations."""
    service = CateringQuotationService(
        authorization_adapter=_build_catering_authorization_adapter(),
    )

    result = service.repository.paginate(
        QueryOptions(
            page=_parse_positive_int(request.args.get("page"), 1),
            page_size=_parse_page_size(request.args.get("page_size")),
            sort_by="quotation_date",
            sort_direction=_parse_sort_direction(
                request.args.get("direction")
            ),
        )
    )

    return render_template(
        "modules/catering/quotations/index.html",
        quotations=result.items,
        pagination=result,
    )


@catering_bp.route(
    "/events/<int:event_id>/create-quotation",
    methods=["GET", "POST"],
)
@login_required
@require_permission(CATERING_QUOTATION_CREATE.name)
def create_catering_quotation_from_event(event_id):
    """Create a Catering quotation for an existing Catering Event."""
    event_service = CateringEventService(
        authorization_adapter=_build_catering_authorization_adapter(),
    )

    try:
        catering_event = event_service.get(event_id)
    except EntityNotFoundException:
        flash("Catering event not found.", "danger")
        return redirect(url_for("catering.catering_events"))

    form = CateringQuotationForm()

    line_forms = [
        CateringQuotationLineForm(prefix=f"line-{index}")
        for index in range(5)
    ]

    if form.validate_on_submit():
        populated_line_forms = []

        for line_form in line_forms:
            has_data = any(
                field.raw_data and any(
                    value.strip() for value in field.raw_data
                )
                for field in (
                    line_form.description,
                    line_form.item_reference,
                    line_form.quantity,
                    line_form.unit,
                    line_form.unit_price,
                    line_form.notes,
                )
            )

            if not has_data:
                continue

            if not line_form.validate():
                continue

            populated_line_forms.append(line_form)

        quotation = CateringQuotation(
            customer_id=catering_event.customer_id,
            event_id=catering_event.id,
            quotation_date=form.quotation_date.data,
            valid_until=form.valid_until.data,
            adjustment_amount=form.adjustment_amount.data or 0,
            customer_notes=form.customer_notes.data,
            status=CateringQuotationWorkflow.DRAFT,
        )

        quotation.lines = [
            CateringQuotationLine(
                description=line_form.description.data,
                item_reference=line_form.item_reference.data,
                quantity=line_form.quantity.data,
                unit=line_form.unit.data,
                unit_price=line_form.unit_price.data,
                notes=line_form.notes.data,
            )
            for line_form in populated_line_forms
        ]

        try:
            quotation = CateringQuotationService(
                authorization_adapter=_build_catering_authorization_adapter(),
            ).create(
                quotation,
                subject=current_user,
            )
        except EntityValidationException as exc:
            flash(str(exc), "danger")
        else:
            flash("Catering quotation created successfully.", "success")
            return redirect(
                url_for(
                    "catering.view_catering_quotation",
                    quotation_id=quotation.id,
                )
            )

    return render_template(
        "modules/catering/quotations/create.html",
        form=form,
        line_forms=line_forms,
        catering_event=catering_event,
    )


@catering_bp.route("/quotations/<int:quotation_id>")
@login_required
@require_permission(CATERING_QUOTATION_READ.name)
def view_catering_quotation(quotation_id):
    """View a Catering quotation."""
    service = CateringQuotationService(
        authorization_adapter=_build_catering_authorization_adapter(),
    )

    try:
        catering_quotation = service.get(quotation_id)
    except EntityNotFoundException:
        flash("Catering quotation not found.", "danger")
        return redirect(url_for("catering.catering_quotations"))

    return render_template(
        "modules/catering/quotations/view.html",
        catering_quotation=catering_quotation,
    )


@catering_bp.route(
    "/quotations/<int:quotation_id>/edit",
    methods=["GET", "POST"],
)
@login_required
@require_permission(CATERING_QUOTATION_UPDATE.name)
def edit_catering_quotation(quotation_id):
    """Edit a draft Catering quotation."""
    service = CateringQuotationService(
        authorization_adapter=_build_catering_authorization_adapter(),
    )

    try:
        catering_quotation = service.get(quotation_id)
    except EntityNotFoundException:
        flash("Catering quotation not found.", "danger")
        return redirect(url_for("catering.catering_quotations"))

    form = CateringQuotationForm(obj=catering_quotation)

    line_forms = [
        CateringQuotationLineForm(
            prefix=f"line-{index}",
            obj=(
                catering_quotation.lines[index]
                if index < len(catering_quotation.lines)
                else None
            ),
        )
        for index in range(5)
    ]

    if form.validate_on_submit():
        populated_line_forms = []

        for line_form in line_forms:
            has_data = any(
                field.data not in (None, "")
                for field in (
                    line_form.description,
                    line_form.item_reference,
                    line_form.quantity,
                    line_form.unit,
                    line_form.unit_price,
                    line_form.notes,
                )
            )

            if not has_data:
                continue

            if not line_form.validate():
                continue

            populated_line_forms.append(line_form)

        catering_quotation.quotation_date = form.quotation_date.data
        catering_quotation.valid_until = form.valid_until.data
        catering_quotation.adjustment_amount = (
            form.adjustment_amount.data or 0
        )
        catering_quotation.customer_notes = form.customer_notes.data

        catering_quotation.lines = [
            CateringQuotationLine(
                description=line_form.description.data,
                item_reference=line_form.item_reference.data,
                quantity=line_form.quantity.data,
                unit=line_form.unit.data,
                unit_price=line_form.unit_price.data,
                notes=line_form.notes.data,
            )
            for line_form in populated_line_forms
        ]

        try:
            service.update(
                catering_quotation,
                subject=current_user,
            )
        except EntityValidationException as exc:
            flash(str(exc), "danger")
        else:
            flash("Catering quotation updated successfully.", "success")
            return redirect(
                url_for(
                    "catering.view_catering_quotation",
                    quotation_id=catering_quotation.id,
                )
            )

    return render_template(
        "modules/catering/quotations/edit.html",
        form=form,
        line_forms=line_forms,
        catering_quotation=catering_quotation,
    )


@catering_bp.route(
    "/quotations/<int:quotation_id>/issue",
    methods=["POST"],
)
@login_required
@require_permission(CATERING_QUOTATION_ISSUE.name)
def issue_catering_quotation(quotation_id):
    """Issue a draft Catering quotation."""
    service = CateringQuotationService(
        authorization_adapter=_build_catering_authorization_adapter(),
    )

    try:
        catering_quotation = service.get(quotation_id)
        catering_quotation = service.issue(
            catering_quotation,
            subject=current_user,
        )
    except EntityNotFoundException:
        flash("Catering quotation not found.", "danger")
        return redirect(url_for("catering.catering_quotations"))
    except EntityValidationException as exc:
        flash(str(exc), "danger")
        return redirect(
            url_for(
                "catering.view_catering_quotation",
                quotation_id=quotation_id,
            )
        )

    flash("Catering quotation issued successfully.", "success")
    return redirect(
        url_for(
            "catering.view_catering_quotation",
            quotation_id=catering_quotation.id,
        )
    )


@catering_bp.route(
    "/quotations/<int:quotation_id>/accept",
    methods=["POST"],
)
@login_required
@require_permission(CATERING_QUOTATION_ACCEPT.name)
def accept_catering_quotation(quotation_id):
    """Accept a quotation and progress its associated Event to QUOTED."""
    service = CateringQuotationService(
        authorization_adapter=_build_catering_authorization_adapter(),
    )

    try:
        catering_quotation = service.get(quotation_id)
        catering_quotation = service.accept(
            catering_quotation,
            subject=current_user,
        )
    except EntityNotFoundException:
        flash("Catering quotation not found.", "danger")
        return redirect(url_for("catering.catering_quotations"))
    except EntityValidationException as exc:
        flash(str(exc), "danger")
        return redirect(
            url_for(
                "catering.view_catering_quotation",
                quotation_id=quotation_id,
            )
        )

    try:
        coordination_service = CateringQuotationEventCoordinationService(
            quotation_repository=CateringQuotationRepository(),
            event_repository=CateringEventRepository(),
            authorization_adapter=_build_catering_authorization_adapter(),
        )
        coordination_service.progress_event_from_accepted_quotation(
            catering_quotation.id,
            subject=current_user,
        )
    except (
        EntityNotFoundException,
        EntityValidationException,
        PermissionError,
        RuntimeError,
    ) as exc:
        flash(
            "The quotation was accepted, but its associated Event could "
            f"not be progressed to QUOTED: {exc}",
            "warning",
        )
        return redirect(
            url_for(
                "catering.view_catering_quotation",
                quotation_id=catering_quotation.id,
            )
        )

    flash(
        "Catering quotation accepted successfully; associated Event "
        "progressed to QUOTED.",
        "success",
    )
    return redirect(
        url_for(
            "catering.view_catering_quotation",
            quotation_id=catering_quotation.id,
        )
    )


@catering_bp.route(
    "/quotations/<int:quotation_id>/decline",
    methods=["POST"],
)
@login_required
@require_permission(CATERING_QUOTATION_DECLINE.name)
def decline_catering_quotation(quotation_id):
    """Decline an issued Catering quotation."""
    service = CateringQuotationService(
        authorization_adapter=_build_catering_authorization_adapter(),
    )

    try:
        catering_quotation = service.get(quotation_id)
        catering_quotation = service.decline(
            catering_quotation,
            subject=current_user,
        )
    except EntityNotFoundException:
        flash("Catering quotation not found.", "danger")
        return redirect(url_for("catering.catering_quotations"))
    except EntityValidationException as exc:
        flash(str(exc), "danger")
        return redirect(
            url_for(
                "catering.view_catering_quotation",
                quotation_id=quotation_id,
            )
        )

    flash("Catering quotation declined.", "success")
    return redirect(
        url_for(
            "catering.view_catering_quotation",
            quotation_id=catering_quotation.id,
        )
    )


@catering_bp.route(
    "/quotations/<int:quotation_id>/expire",
    methods=["POST"],
)
@login_required
@require_permission(CATERING_QUOTATION_EXPIRE.name)
def expire_catering_quotation(quotation_id):
    """Expire an issued Catering quotation."""
    service = CateringQuotationService(
        authorization_adapter=_build_catering_authorization_adapter(),
    )

    try:
        catering_quotation = service.get(quotation_id)
        catering_quotation = service.expire(
            catering_quotation,
            subject=current_user,
        )
    except EntityNotFoundException:
        flash("Catering quotation not found.", "danger")
        return redirect(url_for("catering.catering_quotations"))
    except EntityValidationException as exc:
        flash(str(exc), "danger")
        return redirect(
            url_for(
                "catering.view_catering_quotation",
                quotation_id=quotation_id,
            )
        )

    flash("Catering quotation expired.", "success")
    return redirect(
        url_for(
            "catering.view_catering_quotation",
            quotation_id=catering_quotation.id,
        )
    )


@catering_bp.route(
    "/events/"
)
@login_required
@require_permission(
    CATERING_EVENT_READ.name
)
def catering_events():
    """
    Render the Catering Event list.
    """

    service = CateringEventService(
        authorization_adapter=_build_catering_authorization_adapter(),
    )

    result = service.repository.paginate(
        QueryOptions(
            page=_parse_positive_int(
                request.args.get("page"),
                1,
            ),
            page_size=_parse_page_size(
                request.args.get("page_size")
            ),
            sort_by="event_date",
            sort_direction=_parse_sort_direction(
                request.args.get("direction")
            ),
        )
    )

    return render_template(
        "modules/catering/events/index.html",
        events=result.items,
        pagination=result,
    )


@catering_bp.route(
    "/requests/<int:request_id>/create-event",
    methods=["GET", "POST"],
)
@login_required
@require_permission(
    CATERING_EVENT_CREATE.name
)
def create_catering_event_from_request(
    request_id,
):
    """
    Create an operational Catering Event from an existing Request.
    """

    request_service = CateringRequestService(
        authorization_adapter=_build_catering_authorization_adapter(),
    )

    try:
        catering_request = request_service.get(request_id)
    except EntityNotFoundException:
        flash(
            "Catering Request not found.",
            "danger",
        )
        return redirect(
            url_for("catering.catering_requests")
        )

    form = CateringEventForm()

    if request.method == "GET":
        form.event_date.data = catering_request.service_date
        form.service_details.data = catering_request.requested_service
        form.attendance.data = catering_request.attendance
        form.operational_notes.data = (
            catering_request.notes
            or catering_request.requirements
        )

    if form.validate_on_submit():
        coordination_service = (
            CateringRequestEventCoordinationService(
                authorization_adapter=(
                    _build_catering_authorization_adapter()
                ),
            )
        )

        try:
            catering_event = (
                coordination_service.create_event_from_request(
                    request_id,
                    subject=current_user,
                    event_date=form.event_date.data,
                    service_details=form.service_details.data,
                    attendance=form.attendance.data,
                    operational_notes=form.operational_notes.data,
                )
            )
        except (
            EntityNotFoundException,
            EntityValidationException,
            PermissionError,
            RuntimeError,
            ValueError,
        ) as exc:
            flash(str(exc), "danger")
            return redirect(
                url_for(
                    "catering.view_catering_request",
                    request_id=request_id,
                )
            )

        flash(
            "Catering Event created successfully.",
            "success",
        )
        return redirect(
            url_for(
                "catering.view_catering_event",
                event_id=catering_event.id,
            )
        )

    return render_template(
        "modules/catering/events/create.html",
        form=form,
        catering_request=catering_request,
    )


@catering_bp.route(
    "/events/<int:event_id>"
)
@login_required
@require_permission(
    CATERING_EVENT_READ.name
)
def view_catering_event(
    event_id,
):
    """
    Render a Catering Event detail view.
    """

    service = CateringEventService(
        authorization_adapter=_build_catering_authorization_adapter(),
    )

    try:
        catering_event = service.get(
            event_id
        )
    except EntityNotFoundException:
        flash(
            "Catering Event not found.",
            "danger",
        )

        return redirect(
            url_for(
                "catering.catering_events"
            )
        )

    quotation_repository = CateringQuotationRepository()

    accepted_quotation = (
        quotation_repository.get_accepted_by_event_id(
            catering_event.id
        )
    )

    expense_cost_association_repository = (
        CateringExpenseCostAssociationRepository()
    )
    expense_repository = ExpenseRepository()

    expense_cost_associations = (
        expense_cost_association_repository.get_by_catering_context(
            "CATERING_EVENT",
            f"EVENT-{catering_event.id}",
        )
    )

    expense_cost_association_rows = []

    for association in expense_cost_associations:
        expense_cost_association_rows.append(
            {
                "association": association,
                "expense": expense_repository.get_by_id(
                    association.expense_id
                ),
            }
        )

    profitability_result = None
    profitability_unavailable = False
    profitability_data_conflict = False

    profitability_service = EventProfitabilityService(
        catering_event_repository=CateringEventRepository(),
        catering_revenue_repository=CateringRevenueRepository(),
        expense_cost_association_repository=(
            CateringExpenseCostAssociationRepository()
        ),
        expense_repository=expense_repository,
    )

    try:
        profitability_result = (
            profitability_service.calculate_for_event(
                catering_event.id
            )
        )
    except MultipleResultsFound:
        # Multiple recognized revenue records violate the current
        # profitability service's single-revenue expectation.
        profitability_unavailable = True
        profitability_data_conflict = True
    except ValueError:
        # Authoritative revenue or consumed-cost data is unavailable.
        profitability_unavailable = True

    return render_template(
        "modules/catering/events/view.html",
        catering_event=catering_event,
        can_create_expense_cost_association=(
            current_user.has_permission(
                CATERING_EXPENSE_COST_ASSOCIATION_CREATE.name
            )
        ),
        accepted_quotation=accepted_quotation,
        profitability_result=profitability_result,
        profitability_unavailable=profitability_unavailable,
        profitability_data_conflict=profitability_data_conflict,
        expense_cost_association_rows=expense_cost_association_rows,
    )


@catering_bp.route(
    "/events/<int:event_id>/edit",
    methods=["GET", "POST"],
)
@login_required
@require_permission(
    CATERING_EVENT_UPDATE.name
)
def edit_catering_event(
    event_id,
):
    """
    Edit the operational fields of a Catering Event.
    """

    service = CateringEventService(
        authorization_adapter=_build_catering_authorization_adapter(),
    )

    try:
        catering_event = service.get(
            event_id
        )
    except EntityNotFoundException:
        flash(
            "Catering Event not found.",
            "danger",
        )

        return redirect(
            url_for(
                "catering.catering_events"
            )
        )

    form = CateringEventForm(
        obj=catering_event,
    )

    if form.validate_on_submit():

        catering_event.event_date = (
            form.event_date.data
        )
        catering_event.service_details = (
            form.service_details.data
        )
        catering_event.attendance = (
            form.attendance.data
        )
        catering_event.operational_notes = (
            form.operational_notes.data
        )

        service.update(
            catering_event,
            subject=current_user,
        )

        flash(
            "Catering Event updated successfully.",
            "success",
        )

        return redirect(
            url_for(
                "catering.view_catering_event",
                event_id=catering_event.id,
            )
        )

    return render_template(
        "modules/catering/events/edit.html",
        form=form,
        catering_event=catering_event,
    )


@catering_bp.route(
    "/events/<int:event_id>/quote",
    methods=["POST"],
)
@login_required
@require_permission(
    CATERING_EVENT_QUOTE.name
)
def quote_catering_event(
    event_id,
):
    """
    Progress a Catering Event from REQUESTED to QUOTED
    using its accepted Catering Quotation.
    """

    quotation_repository = CateringQuotationRepository()

    try:
        catering_quotation = (
            quotation_repository.get_accepted_by_event_id(
                event_id
            )
        )

        if catering_quotation is None:
            raise EntityValidationException(
                "No ACCEPTED quotation exists for this Event."
            )

        coordination_service = (
            CateringQuotationEventCoordinationService(
                quotation_repository=quotation_repository,
                event_repository=CateringEventRepository(),
                authorization_adapter=(
                    _build_catering_authorization_adapter()
                ),
            )
        )

        coordination_service.progress_event_from_accepted_quotation(
            catering_quotation.id,
            subject=current_user,
        )

        flash(
            "Catering Event progressed to QUOTED.",
            "success",
        )

    except EntityNotFoundException:
        flash(
            "Catering Event or Quotation not found.",
            "danger",
        )
    except EntityValidationException as exc:
        flash(
            str(exc),
            "danger",
        )

    return redirect(
        url_for(
            "catering.view_catering_event",
            event_id=event_id,
        )
    )


@catering_bp.route(
    "/events/<int:event_id>/request-confirmation",
    methods=["POST"],
)
@login_required
@require_permission(
    CATERING_EVENT_CONFIRM.name
)
def request_confirmation_catering_event(
    event_id,
):
    """
    Progress a Catering Event from QUOTED to PENDING_CONFIRMATION.
    """

    service = CateringEventService(
        authorization_adapter=_build_catering_authorization_adapter(),
    )

    try:
        catering_event = service.get(
            event_id
        )

        service.request_confirmation(
            catering_event,
            subject=current_user,
        )

    except EntityNotFoundException:
        flash(
            "Catering Event not found.",
            "danger",
        )

        return redirect(
            url_for(
                "catering.catering_events"
            )
        )

    except EntityValidationException as exc:
        flash(
            str(exc),
            "danger",
        )

    else:
        flash(
            "Catering Event moved to pending confirmation.",
            "success",
        )

    return redirect(
        url_for(
            "catering.view_catering_event",
            event_id=event_id,
        )
    )


@catering_bp.route(
    "/events/<int:event_id>/confirm",
    methods=["POST"],
)
@login_required
@require_permission(
    CATERING_EVENT_CONFIRM.name
)
def confirm_catering_event(
    event_id,
):
    """
    Confirm a Catering Event.
    """

    service = CateringEventService(
        authorization_adapter=_build_catering_authorization_adapter(),
    )

    try:
        catering_event = service.get(
            event_id
        )

        service.confirm(
            catering_event,
            subject=current_user,
        )

    except EntityNotFoundException:
        flash(
            "Catering Event not found.",
            "danger",
        )

        return redirect(
            url_for(
                "catering.catering_events"
            )
        )

    except EntityValidationException as exc:
        flash(
            str(exc),
            "danger",
        )

    else:
        flash(
            "Catering Event confirmed successfully.",
            "success",
        )

    return redirect(
        url_for(
            "catering.view_catering_event",
            event_id=event_id,
        )
    )


@catering_bp.route(
    "/events/<int:event_id>/plan",
    methods=["POST"],
)
@login_required
@require_permission(
    CATERING_EVENT_PLAN.name
)
def plan_catering_event(event_id):
    """
    Progress a confirmed Catering Event to PLANNING.
    """

    service = CateringEventService(
        authorization_adapter=_build_catering_authorization_adapter(),
    )

    try:
        catering_event = service.get(event_id)

        service.plan(
            catering_event,
            subject=current_user,
        )

    except EntityNotFoundException:
        flash(
            "Catering Event not found.",
            "danger",
        )

        return redirect(
            url_for(
                "catering.catering_events"
            )
        )

    except EntityValidationException as exc:
        flash(
            str(exc),
            "danger",
        )

    else:
        flash(
            "Catering Event moved to planning.",
            "success",
        )

    return redirect(
        url_for(
            "catering.view_catering_event",
            event_id=event_id,
        )
    )


@catering_bp.route(
    "/events/<int:event_id>/ready",
    methods=["POST"],
)
@login_required
@require_permission(
    CATERING_EVENT_READY.name
)
def ready_catering_event(event_id):
    """
    Progress a planned Catering Event to READY.
    """

    service = CateringEventService(
        authorization_adapter=_build_catering_authorization_adapter(),
    )

    try:
        catering_event = service.get(event_id)

        service.ready(
            catering_event,
            subject=current_user,
        )

    except EntityNotFoundException:
        flash(
            "Catering Event not found.",
            "danger",
        )

        return redirect(
            url_for(
                "catering.catering_events"
            )
        )

    except EntityValidationException as exc:
        flash(
            str(exc),
            "danger",
        )

    else:
        flash(
            "Catering Event marked ready.",
            "success",
        )

    return redirect(
        url_for(
            "catering.view_catering_event",
            event_id=event_id,
        )
    )


@catering_bp.route(
    "/events/<int:event_id>/start-production",
    methods=["POST"],
)
@login_required
@require_permission(
    CATERING_EVENT_START_PRODUCTION.name
)
def start_production_catering_event(event_id):
    """
    Start production for a READY Catering Event.
    """

    service = CateringEventService(
        authorization_adapter=_build_catering_authorization_adapter(),
    )

    try:
        catering_event = service.get(event_id)

        service.start_production(
            catering_event,
            subject=current_user,
        )

    except EntityNotFoundException:
        flash(
            "Catering Event not found.",
            "danger",
        )

        return redirect(
            url_for(
                "catering.catering_events"
            )
        )

    except EntityValidationException as exc:
        flash(
            str(exc),
            "danger",
        )

    else:
        flash(
            "Catering Event moved to production.",
            "success",
        )

    return redirect(
        url_for(
            "catering.view_catering_event",
            event_id=event_id,
        )
    )


@catering_bp.route(
    "/events/<int:event_id>/deliver",
    methods=["POST"],
)
@login_required
@require_permission(
    CATERING_EVENT_DELIVER.name
)
def deliver_catering_event(event_id):
    """
    Mark an IN_PRODUCTION Catering Event as DELIVERED.
    """

    service = CateringEventService(
        authorization_adapter=_build_catering_authorization_adapter(),
    )

    try:
        catering_event = service.get(event_id)

        service.deliver(
            catering_event,
            subject=current_user,
        )

    except EntityNotFoundException:
        flash(
            "Catering Event not found.",
            "danger",
        )

        return redirect(
            url_for(
                "catering.catering_events"
            )
        )

    except EntityValidationException as exc:
        flash(
            str(exc),
            "danger",
        )

    else:
        flash(
            "Catering Event marked delivered.",
            "success",
        )

    return redirect(
        url_for(
            "catering.view_catering_event",
            event_id=event_id,
        )
    )


@catering_bp.route(
    "/events/<int:event_id>/complete",
    methods=["POST"],
)
@login_required
@require_permission(
    CATERING_EVENT_COMPLETE.name
)
def complete_catering_event(event_id):
    """
    Complete a DELIVERED Catering Event.
    """

    service = CateringEventService(
        authorization_adapter=_build_catering_authorization_adapter(),
    )

    try:
        catering_event = service.get(event_id)

        service.complete(
            catering_event,
            subject=current_user,
        )

    except EntityNotFoundException:
        flash(
            "Catering Event not found.",
            "danger",
        )

        return redirect(
            url_for(
                "catering.catering_events"
            )
        )

    except EntityValidationException as exc:
        flash(
            str(exc),
            "danger",
        )

    else:
        flash(
            "Catering Event completed successfully.",
            "success",
        )

    return redirect(
        url_for(
            "catering.view_catering_event",
            event_id=event_id,
        )
    )


@catering_bp.route(
    "/events/<int:event_id>/cancel",
    methods=["POST"],
)
@login_required
@require_permission(
    CATERING_EVENT_CANCEL.name
)
def cancel_catering_event(
    event_id,
):
    """
    Cancel a Catering Event.
    """

    service = CateringEventService(
        authorization_adapter=_build_catering_authorization_adapter(),
    )

    try:
        catering_event = service.get(
            event_id
        )
        service.cancel(
            catering_event,
            subject=current_user,
        )
    except EntityNotFoundException:
        flash(
            "Catering Event not found.",
            "danger",
        )

        return redirect(
            url_for(
                "catering.catering_events"
            )
        )

    flash(
        "Catering Event cancelled successfully.",
        "success",
    )

    return redirect(
        url_for(
            "catering.view_catering_event",
            event_id=event_id,
        )
    )


@catering_bp.route(
    "/events/<int:event_id>/delete",
    methods=["POST"],
)
@login_required
@require_permission(
    CATERING_EVENT_DELETE.name
)
def delete_catering_event(
    event_id,
):
    """
    Delete a Catering Event.
    """

    service = CateringEventService(
        authorization_adapter=_build_catering_authorization_adapter(),
    )

    try:
        service.delete(
            event_id,
            subject=current_user,
        )
    except EntityNotFoundException:
        flash(
            "Catering Event not found.",
            "danger",
        )

        return redirect(
            url_for(
                "catering.catering_events"
            )
        )

    flash(
        "Catering Event deleted successfully.",
        "success",
    )

    return redirect(
        url_for(
            "catering.catering_events"
        )
    )


@catering_bp.route(
    "/events/<int:event_id>/expense-cost-associations/create",
    methods=["GET", "POST"],
)
@login_required
@require_permission(
    CATERING_EXPENSE_COST_ASSOCIATION_CREATE.name
)
def create_event_expense_cost_association(event_id):
    """Associate an existing Expense with a Catering Event."""

    form = CateringExpenseCostAssociationForm()

    event_repository = CateringEventRepository()
    expense_repository = ExpenseRepository()
    association_repository = CateringExpenseCostAssociationRepository()

    event = event_repository.get_by_id(event_id)
    if event is None:
        flash("Catering Event not found.", "danger")
        return redirect(url_for("catering.catering_events"))

    if form.validate_on_submit():
        expense_id = form.expense_id.data
        expense = expense_repository.get_by_id(expense_id)

        if expense is None:
            flash("Expense not found.", "danger")
        elif (
            getattr(expense, "status", None) != "APPROVED"
            or getattr(expense, "approved_at", None) is None
        ):
            flash(
                "Only approved Expenses with an approval timestamp "
                "can be associated with a Catering Event.",
                "warning",
            )
        else:
            context_type = "CATERING_EVENT"
            context_reference = f"EVENT-{event.id}"

            # Check the actual database uniqueness combination:
            # expense_id + catering_context_type + catering_context_reference.
            existing_associations = association_repository.get_all()

            duplicate_exists = any(
                association.expense_id == expense_id
                and association.catering_context_type == context_type
                and association.catering_context_reference
                == context_reference
                for association in existing_associations
            )

            if duplicate_exists:
                flash(
                    "This Expense is already associated with this "
                    "Catering Event.",
                    "warning",
                )
            else:
                contribution_id = (
                    f"expense:{expense_id}:"
                    f"catering:event:{event.id}:"
                    "consume_approved_expense"
                )

                association = CateringExpenseCostAssociation(
                    expense_id=expense_id,
                    catering_context_type=context_type,
                    catering_context_reference=context_reference,
                    status="ELIGIBLE",
                    contribution_id=contribution_id,
                )

                service = CateringExpenseCostAssociationService(
                    repository=association_repository,
                    authorization_adapter=(
                        _build_catering_authorization_adapter()
                    ),
                )

                service.create(
                    association,
                    subject=current_user,
                )

                flash(
                    "Expense associated with Catering Event successfully.",
                    "success",
                )
                return redirect(
                    url_for(
                        "catering.view_catering_event",
                        event_id=event.id,
                    )
                )

    return render_template(
        "modules/catering/expense_cost_associations/create.html",
        form=form,
        event=event,
    )


@catering_bp.route(
    "/events/<int:event_id>/requirements"
)
@login_required
@require_permission(
    CATERING_EVENT_REQUIREMENT_READ.name
)
def catering_event_requirements(event_id):
    """
    Render Event Requirements for a Catering Event.
    """

    try:
        catering_event = CateringEventService(
            authorization_adapter=_build_catering_authorization_adapter(),
        ).get(event_id)
    except EntityNotFoundException:
        flash(
            "Catering event not found.",
            "danger",
        )
        return redirect(
            url_for("catering.catering_events")
        )

    repository = EventRequirementRepository()

    requirements = repository.query(
        QueryOptions(
            filters={
                "event_id": event_id,
            },
            page=1,
            page_size=100,
            sort_by="id",
            sort_direction="asc",
        )
    )

    return render_template(
        "modules/catering/event_requirements/index.html",
        catering_event=catering_event,
        requirements=requirements,
    )


@catering_bp.route(
    "/events/<int:event_id>/requirements/create",
    methods=["GET", "POST"],
)
@login_required
@require_permission(
    CATERING_EVENT_REQUIREMENT_CREATE.name
)
def create_catering_event_requirement(event_id):
    """
    Create an Event Requirement for a Catering Event.
    """

    try:
        catering_event = CateringEventService(
            authorization_adapter=_build_catering_authorization_adapter(),
        ).get(event_id)
    except EntityNotFoundException:
        flash(
            "Catering event not found.",
            "danger",
        )
        return redirect(
            url_for("catering.catering_events")
        )

    form = EventRequirementForm()

    if form.validate_on_submit():
        requirement = EventRequirement(
            event_id=catering_event.id,
            description=form.description.data,
            item_reference=form.item_reference.data,
            quantity=form.quantity.data,
            unit=form.unit.data,
            fulfilment_type=form.fulfilment_type.data,
            required_by_date=form.required_by_date.data,
            notes=form.notes.data,
            status="DRAFT",
        )

        try:
            requirement = EventRequirementService(
                authorization_adapter=_build_catering_authorization_adapter(),
            ).create(
                requirement,
                subject=current_user,
            )
        except EntityNotFoundException as exc:
            flash(
                str(exc),
                "danger",
            )
        except EntityValidationException as exc:
            flash(
                str(exc),
                "danger",
            )
        except ValueError as exc:
            flash(
                str(exc),
                "danger",
            )
        else:
            flash(
                "Event Requirement created successfully.",
                "success",
            )
            return redirect(
                url_for(
                    "catering.view_catering_event_requirement",
                    event_id=catering_event.id,
                    requirement_id=requirement.id,
                )
            )

    return render_template(
        "modules/catering/event_requirements/create.html",
        form=form,
        catering_event=catering_event,
    )


@catering_bp.route(
    "/events/<int:event_id>/requirements/<int:requirement_id>"
)
@login_required
@require_permission(
    CATERING_EVENT_REQUIREMENT_READ.name
)
def view_catering_event_requirement(
    event_id,
    requirement_id,
):
    """
    Render an Event Requirement detail view.
    """

    repository = EventRequirementRepository()

    try:
        catering_event = CateringEventService(
            authorization_adapter=_build_catering_authorization_adapter(),
        ).get(event_id)

        requirement = repository.get_by_id(requirement_id)
    except EntityNotFoundException:
        flash(
            "Event Requirement not found.",
            "danger",
        )
        return redirect(
            url_for(
                "catering.catering_event_requirements",
                event_id=event_id,
            )
        )

    if requirement.event_id != catering_event.id:
        flash(
            "Event Requirement does not belong to this Catering Event.",
            "danger",
        )
        return redirect(
            url_for(
                "catering.catering_event_requirements",
                event_id=event_id,
            )
        )

    return render_template(
        "modules/catering/event_requirements/view.html",
        requirement=requirement,
        catering_event=catering_event,
    )


@catering_bp.route(
    "/events/<int:event_id>/requirements/"
    "<int:requirement_id>/purchase-requirement/create",
    methods=["GET", "POST"],
)
@login_required
@require_permission(CATERING_PURCHASE_REQUIREMENT_CREATE.name)
def create_catering_purchase_requirement(
    event_id: int,
    requirement_id: int,
):
    """Create a Catering Purchase Requirement for an Event Requirement."""
    event_service = CateringEventService(
        authorization_adapter=_build_catering_authorization_adapter()
    )
    requirement_repository = EventRequirementRepository()

    try:
        catering_event = event_service.get(event_id)
        requirement = requirement_repository.get_by_id(
            requirement_id
        )

        if (
            requirement is None
            or requirement.event_id != event_id
        ):
            raise EntityNotFoundException(
                "EventRequirement",
                requirement_id,
            )

        if catering_event.status != "CONFIRMED":
            raise ValueError(
                "Catering Purchase Requirements can only be "
                "created for a CONFIRMED Catering Event."
            )

        if requirement.fulfilment_type != "PROCUREMENT":
            raise ValueError(
                "Catering Purchase Requirements require a "
                "PROCUREMENT Event Requirement."
            )

        if requirement.purchase_requirement is not None:
            raise ValueError(
                "A Catering Purchase Requirement already exists "
                "for this Event Requirement."
            )

        form = CateringPurchaseRequirementForm()

        if form.validate_on_submit():
            purchase_requirement = CateringPurchaseRequirement(
                event_requirement_id=requirement.id,
                description=form.description.data.strip(),
                item_reference=(
                    form.item_reference.data.strip()
                    if form.item_reference.data
                    else None
                ),
                quantity=form.quantity.data,
                unit=form.unit.data.strip(),
                required_by_date=form.required_by_date.data,
                justification=(
                    form.justification.data.strip()
                    if form.justification.data
                    else None
                ),
                status="DRAFT",
            )

            transaction = SQLAlchemyTransactionManager()

            try:
                transaction.begin()

                CateringPurchaseRequirementService(
                    authorization_adapter=(
                        _build_catering_authorization_adapter()
                    )
                ).create(
                    purchase_requirement,
                    subject=current_user,
                )

                transaction.commit()

            except Exception:
                if transaction.active:
                    transaction.rollback()
                raise

            flash(
                "Catering Purchase Requirement created successfully.",
                "success",
            )

            return redirect(
                url_for(
                    "catering.view_catering_event_requirement",
                    event_id=event_id,
                    requirement_id=requirement_id,
                )
            )

        return render_template(
            "modules/catering/purchase_requirements/create.html",
            form=form,
            catering_event=catering_event,
            requirement=requirement,
        )

    except (
        EntityNotFoundException,
        EntityValidationException,
        ValueError,
        RuntimeError,
    ) as exc:
        flash(str(exc), "danger")
        return redirect(
            url_for(
                "catering.view_catering_event_requirement",
                event_id=event_id,
                requirement_id=requirement_id,
            )
        )


@catering_bp.route(
    "/events/<int:event_id>/requirements/<int:requirement_id>/"
    "purchase-requirement/submit",
    methods=["POST"],
)
@login_required
@require_permission(
    CATERING_PURCHASE_REQUIREMENT_SUBMIT_TO_PROCUREMENT.name
)
def submit_catering_purchase_requirement_to_procurement(
    event_id: int,
    requirement_id: int,
):
    """Submit a Catering Purchase Requirement to Procurement."""
    try:
        event_requirement = EventRequirementRepository().get_by_id(
            requirement_id
        )

        if (
            event_requirement is None
            or event_requirement.event_id != event_id
        ):
            raise EntityNotFoundException(
                "EventRequirement",
                requirement_id,
            )

        purchase_requirement = (
            CateringPurchaseRequirementRepository().get_by_id(
                getattr(
                    event_requirement.purchase_requirement,
                    "id",
                    None,
                )
            )
            if event_requirement.purchase_requirement is not None
            else None
        )

        if purchase_requirement is None:
            raise EntityNotFoundException(
                "CateringPurchaseRequirement",
                requirement_id,
            )

        transaction = SQLAlchemyTransactionManager()

        try:
            transaction.begin()

            CateringProcurementHandoffService(
                authorization_adapter=(
                    _build_catering_authorization_adapter()
                )
            ).submit_to_procurement(
                purchase_requirement,
                subject=current_user,
            )

            transaction.commit()

        except Exception:
            if transaction.active:
                transaction.rollback()
            raise

        flash(
            "Catering Purchase Requirement submitted to Procurement.",
            "success",
        )

    except (
        EntityNotFoundException,
        EntityValidationException,
        ValueError,
        RuntimeError,
    ) as exc:
        flash(str(exc), "danger")

    return redirect(
        url_for(
            "catering.view_catering_event_requirement",
            event_id=event_id,
            requirement_id=requirement_id,
        )
    )


@catering_bp.route(
    "/events/<int:event_id>/requirements/<int:requirement_id>/edit",
    methods=["GET", "POST"],
)
@login_required
@require_permission(
    CATERING_EVENT_REQUIREMENT_UPDATE.name
)
def edit_catering_event_requirement(
    event_id,
    requirement_id,
):
    """
    Edit an Event Requirement.
    """

    repository = EventRequirementRepository()

    try:
        catering_event = CateringEventService(
            authorization_adapter=_build_catering_authorization_adapter(),
        ).get(event_id)

        requirement = repository.get_by_id(requirement_id)
    except EntityNotFoundException:
        flash(
            "Event Requirement not found.",
            "danger",
        )
        return redirect(
            url_for(
                "catering.catering_event_requirements",
                event_id=event_id,
            )
        )

    if requirement.event_id != catering_event.id:
        flash(
            "Event Requirement does not belong to this Catering Event.",
            "danger",
        )
        return redirect(
            url_for(
                "catering.catering_event_requirements",
                event_id=event_id,
            )
        )

    form = EventRequirementForm(
        obj=requirement
    )

    if form.validate_on_submit():
        requirement.description = form.description.data
        requirement.item_reference = form.item_reference.data
        requirement.quantity = form.quantity.data
        requirement.unit = form.unit.data
        requirement.fulfilment_type = form.fulfilment_type.data
        requirement.required_by_date = form.required_by_date.data
        requirement.notes = form.notes.data

        try:
            EventRequirementService(
                authorization_adapter=_build_catering_authorization_adapter(),
            ).update(
                requirement,
                subject=current_user,
            )
        except EntityNotFoundException as exc:
            flash(
                str(exc),
                "danger",
            )
        except EntityValidationException as exc:
            flash(
                str(exc),
                "danger",
            )
        except ValueError as exc:
            flash(
                str(exc),
                "danger",
            )
        else:
            flash(
                "Event Requirement updated successfully.",
                "success",
            )
            return redirect(
                url_for(
                    "catering.view_catering_event_requirement",
                    event_id=catering_event.id,
                    requirement_id=requirement.id,
                )
            )

    return render_template(
        "modules/catering/event_requirements/edit.html",
        form=form,
        requirement=requirement,
        catering_event=catering_event,
    )


@catering_bp.route(
    "/events/<int:event_id>/requirements/<int:requirement_id>/identify",
    methods=["POST"],
)
@login_required
@require_permission(
    CATERING_EVENT_REQUIREMENT_IDENTIFY.name
)
def identify_catering_event_requirement(
    event_id,
    requirement_id,
):
    """
    Identify an Event Requirement.
    """

    repository = EventRequirementRepository()

    try:
        requirement = repository.get_by_id(requirement_id)

        if requirement.event_id != event_id:
            raise EntityValidationException(
                "Event Requirement does not belong to this Catering Event."
            )

        EventRequirementService(
            authorization_adapter=_build_catering_authorization_adapter(),
        ).identify(
            requirement,
            subject=current_user,
        )
    except EntityNotFoundException:
        flash(
            "Event Requirement not found.",
            "danger",
        )
    except EntityValidationException as exc:
        flash(
            str(exc),
            "danger",
        )
    except ValueError as exc:
        flash(
            str(exc),
            "danger",
        )
    else:
        flash(
            "Event Requirement identified successfully.",
            "success",
        )

    return redirect(
        url_for(
            "catering.view_catering_event_requirement",
            event_id=event_id,
            requirement_id=requirement_id,
        )
    )


@catering_bp.route(
    "/events/<int:event_id>/requirements/<int:requirement_id>/ready",
    methods=["POST"],
)
@login_required
@require_permission(
    CATERING_EVENT_REQUIREMENT_READY.name
)
def ready_catering_event_requirement(
    event_id,
    requirement_id,
):
    """
    Mark an Event Requirement ready after verifying fulfilment.
    """

    repository = EventRequirementRepository()

    try:
        requirement = repository.get_by_id(requirement_id)

        if requirement is None:
            raise EntityNotFoundException(
                "Event Requirement not found."
            )

        if requirement.event_id != event_id:
            raise EntityValidationException(
                "Event Requirement does not belong to this Catering Event."
            )

        EventRequirementService(
            authorization_adapter=_build_catering_authorization_adapter(),
            fulfilment_verifier=EventRequirementFulfilmentVerifier(),
        ).ready(
            requirement,
            subject=current_user,
        )

    except EntityNotFoundException:
        flash(
            "Event Requirement not found.",
            "danger",
        )
    except EntityValidationException as exc:
        flash(
            str(exc),
            "danger",
        )
    except (ValueError, RuntimeError) as exc:
        flash(
            str(exc),
            "danger",
        )
    else:
        flash(
            "Event Requirement marked ready successfully.",
            "success",
        )

    return redirect(
        url_for(
            "catering.view_catering_event_requirement",
            event_id=event_id,
            requirement_id=requirement_id,
        )
    )


@catering_bp.route(
    "/events/<int:event_id>/requirements/<int:requirement_id>/cancel",
    methods=["POST"],
)
@login_required
@require_permission(
    CATERING_EVENT_REQUIREMENT_CANCEL.name
)
def cancel_catering_event_requirement(
    event_id,
    requirement_id,
):
    """
    Cancel an Event Requirement.
    """

    repository = EventRequirementRepository()

    try:
        requirement = repository.get_by_id(requirement_id)

        if requirement.event_id != event_id:
            raise EntityValidationException(
                "Event Requirement does not belong to this Catering Event."
            )

        EventRequirementService(
            authorization_adapter=_build_catering_authorization_adapter(),
        ).cancel(
            requirement,
            subject=current_user,
        )
    except EntityNotFoundException:
        flash(
            "Event Requirement not found.",
            "danger",
        )
    except EntityValidationException as exc:
        flash(
            str(exc),
            "danger",
        )
    except ValueError as exc:
        flash(
            str(exc),
            "danger",
        )
    else:
        flash(
            "Event Requirement cancelled successfully.",
            "success",
        )

    return redirect(
        url_for(
            "catering.view_catering_event_requirement",
            event_id=event_id,
            requirement_id=requirement_id,
        )
    )


@catering_bp.route("/categories/")
@login_required
@require_permission(
    CATERING_PRODUCT_CATEGORY_READ.name
)
def categories():
    """
    Render the Product Category management list.
    """

    service = ProductCategoryService()

    result = service.paginate(
        _build_category_query_options()
    )

    return render_template(
        "modules/catering/categories/index.html",
        product_categories=result.items,
        pagination=result,
    )


@catering_bp.route(
    "/categories/create",
    methods=["GET", "POST"],
)
@login_required
@require_permission(
    CATERING_PRODUCT_CATEGORY_CREATE.name
)
def create_category():
    """
    Create a Product Category.
    """

    form = ProductCategoryForm()

    if form.validate_on_submit():

        service = ProductCategoryService()

        category = service.create(
            service.repository.model(
                name=form.name.data,
                code=form.code.data,
                description=form.description.data,
            )
        )

        flash(
            "Product category created successfully.",
            "success",
        )

        return redirect(
            url_for(
                "catering.categories"
            )
        )

    return render_template(
        "modules/catering/categories/create.html",
        form=form,
    )


@catering_bp.route(
    "/categories/<int:category_id>/activate",
    methods=["POST"],
)
@login_required
@require_permission(
    CATERING_PRODUCT_CATEGORY_UPDATE.name
)
def activate_category(
    category_id,
):
    """
    Activate a Product Category.
    """

    service = ProductCategoryService()

    service.activate(
        category_id
    )

    flash(
        "Product category activated successfully.",
        "success",
    )

    return redirect(
        url_for(
            "catering.categories"
        )
    )


@catering_bp.route(
    "/categories/<int:category_id>/deactivate",
    methods=["POST"],
)
@login_required
@require_permission(
    CATERING_PRODUCT_CATEGORY_UPDATE.name
)
def deactivate_category(
    category_id,
):
    """
    Deactivate a Product Category.
    """

    service = ProductCategoryService()

    service.deactivate(
        category_id
    )

    flash(
        "Product category deactivated successfully.",
        "success",
    )

    return redirect(
        url_for(
            "catering.categories"
        )
    )


@catering_bp.route("/products/")
@login_required
@require_permission(
    CATERING_PRODUCT_READ.name
)
def products():
    """
    Render the Product management list.
    """

    service = ProductService()

    result = service.paginate(
        _build_product_query_options()
    )

    category_service = ProductCategoryService()

    product_categories = category_service.get_all()

    return render_template(
        "modules/catering/products/index.html",
        products=result.items,
        pagination=result,
        product_categories=product_categories,
    )


@catering_bp.route(
    "/products/create",
    methods=["GET", "POST"],
)
@login_required
@require_permission(
    CATERING_PRODUCT_CREATE.name
)
def create_product():
    """
    Create a Catering Product.
    """

    form = ProductForm()

    category_service = ProductCategoryService()

    product_categories = category_service.get_all()

    form.category_id.choices = [
        (
            category.id,
            category.name,
        )
        for category in product_categories
        if category.is_active
    ]

    if form.validate_on_submit():

        service = ProductService()

        product = service.create(
            service.repository.model(
                category_id=form.category_id.data,
                name=form.name.data,
                code=form.code.data,
                description=form.description.data,
                unit=form.unit.data,
            )
        )

        flash(
            "Product created successfully.",
            "success",
        )

        return redirect(
            url_for(
                "catering.products"
            )
        )

    return render_template(
        "modules/catering/products/create.html",
        form=form,
    )


@catering_bp.route(
    "/products/<int:product_id>/activate",
    methods=["POST"],
)
@login_required
@require_permission(
    CATERING_PRODUCT_UPDATE.name
)
def activate_product(
    product_id,
):
    """
    Activate a Product.
    """

    service = ProductService()

    service.activate(
        product_id
    )

    flash(
        "Product activated successfully.",
        "success",
    )

    return redirect(
        url_for(
            "catering.products"
        )
    )


@catering_bp.route(
    "/products/<int:product_id>/deactivate",
    methods=["POST"],
)
@login_required
@require_permission(
    CATERING_PRODUCT_UPDATE.name
)
def deactivate_product(
    product_id,
):
    """
    Deactivate a Product.
    """

    service = ProductService()

    service.deactivate(
        product_id
    )

    flash(
        "Product deactivated successfully.",
        "success",
    )

    return redirect(
        url_for(
            "catering.products"
        )
    )


@catering_bp.route("/stock-items/")
@login_required
@require_permission(
    CATERING_STOCK_ITEM_READ.name
)
def stock_items():
    """
    Render the Stock Item management list.
    """

    service = StockItemService()

    result = service.paginate(
        _build_stock_item_query_options()
    )

    return render_template(
        "modules/catering/stock_items/index.html",
        stock_items=result.items,
        pagination=result,
    )


@catering_bp.route(
    "/stock-items/create",
    methods=["GET", "POST"],
)
@login_required
@require_permission(
    CATERING_STOCK_ITEM_CREATE.name
)
def create_stock_item():
    """
    Create a Stock Item from an existing Catering Product.
    """

    form = StockItemForm()

    product_service = ProductService()

    products = product_service.get_all()

    form.product_id.choices = [
        (
            product.id,
            product.name,
        )
        for product in products
        if product.is_active
    ]

    if form.validate_on_submit():

        service = StockItemService()

        stock_item = service.create(
            service.repository.model(
                product_id=form.product_id.data,
                minimum_level=form.minimum_level.data,
                reorder_level=form.reorder_level.data,
                is_active=form.is_active.data,
            )
        )

        flash(
            "Stock item created successfully.",
            "success",
        )

        return redirect(
            url_for(
                "catering.stock_items"
            )
        )

    return render_template(
        "modules/catering/stock_items/create.html",
        form=form,
    )


@catering_bp.route("/locations/")
@login_required
@require_permission(
    CATERING_INVENTORY_LOCATION_READ.name
)
def locations():
    """
    Render the Inventory Location management list.
    """

    service = InventoryLocationService()

    result = service.paginate(
        _build_location_query_options()
    )

    return render_template(
        "modules/catering/locations/index.html",
        locations=result.items,
        pagination=result,
    )


@catering_bp.route(
    "/locations/create",
    methods=["GET", "POST"],
)
@login_required
@require_permission(
    CATERING_INVENTORY_LOCATION_CREATE.name
)
def create_location():
    """
    Create an Inventory Location.
    """

    form = InventoryLocationForm()

    if form.validate_on_submit():

        service = InventoryLocationService()

        location = service.create(
            service.repository.model(
                code=form.code.data,
                name=form.name.data,
                description=form.description.data,
                is_active=form.is_active.data,
            )
        )

        flash(
            "Inventory location created successfully.",
            "success",
        )

        return redirect(
            url_for(
                "catering.locations"
            )
        )

    return render_template(
        "modules/catering/locations/create.html",
        form=form,
    )


@catering_bp.route("/balances/")
@login_required
@require_permission(
    CATERING_STOCK_BALANCE_READ.name
)
def balances():
    """
    Render the read-only Stock Balance list.
    """

    service = StockBalanceService()

    result = service.paginate(
        _build_stock_balance_query_options()
    )

    return render_template(
        "modules/catering/balances/index.html",
        balances=result.items,
        pagination=result,
    )


@catering_bp.route("/movements/")
@login_required
@require_permission(
    CATERING_STOCK_MOVEMENT_READ.name
)
def movements():
    """
    Render the Stock Movement management list.
    """

    service = StockMovementService()

    result = service.paginate(
        _build_stock_movement_query_options()
    )

    return render_template(
        "modules/catering/movements/index.html",
        movements=result.items,
        pagination=result,
    )


@catering_bp.route(
    "/movements/create",
    methods=["GET", "POST"],
)
@login_required
@require_permission(
    CATERING_STOCK_MOVEMENT_CREATE.name
)
def create_movement():
    """
    Create a Draft Stock Movement.
    """

    form = StockMovementForm()

    stock_item_service = StockItemService()
    location_service = InventoryLocationService()

    stock_items = stock_item_service.get_all()
    locations = location_service.get_all()

    form.stock_item_id.choices = [
        (
            stock_item.id,
            (
                stock_item.product.name
                if stock_item.product
                else str(stock_item.id)
            ),
        )
        for stock_item in stock_items
        if stock_item.is_active
    ]

    form.location_id.choices = [
        (
            location.id,
            location.name,
        )
        for location in locations
        if location.is_active
    ]

    if form.validate_on_submit():

        service = StockMovementService(
            authorization_adapter=(
                _build_catering_authorization_adapter()
            )
        )

        movement = service.create(
            service.repository.model(
                stock_item_id=form.stock_item_id.data,
                location_id=form.location_id.data,
                movement_type=form.movement_type.data,
                quantity=form.quantity.data,
                reference=form.reference.data,
                reason=form.reason.data,
                occurred_at=form.occurred_at.data,
            ),
            subject=current_user,
        )

        flash(
            "Stock movement created successfully.",
            "success",
        )

        return redirect(
            url_for(
                "catering.movements"
            )
        )

    return render_template(
        "modules/catering/movements/create.html",
        form=form,
    )


@catering_bp.route(
    "/movements/<int:movement_id>/post",
    methods=["POST"],
)
@login_required
@require_permission(
    CATERING_STOCK_MOVEMENT_POST.name
)
def post_movement(
    movement_id,
):
    """
    Post a Draft Stock Movement.
    """

    service = StockMovementService(
        authorization_adapter=(
            _build_catering_authorization_adapter()
        )
    )

    try:
        movement = service.get(
            movement_id
        )

    except EntityNotFoundException:
        flash(
            "Stock movement not found.",
            "error",
        )

        return redirect(
            url_for(
                "catering.movements"
            )
        )

    try:
        service.post_movement(
            movement,
            subject=current_user,
        )

    except (ValueError, RuntimeError) as exc:
        flash(
            str(exc),
            "error",
        )

        return redirect(
            url_for(
                "catering.movements"
            )
        )

    flash(
        "Stock movement posted successfully.",
        "success",
    )

    return redirect(
        url_for(
            "catering.movements"
        )
    )


@catering_bp.route("/transfers/")
@login_required
@require_permission(
    CATERING_STOCK_TRANSFER_READ.name
)
def transfers():
    """
    Render the Stock Transfer management list.
    """

    service = StockTransferService()

    result = service.paginate(
        _build_stock_transfer_query_options()
    )

    return render_template(
        "modules/catering/transfers/index.html",
        transfers=result.items,
        pagination=result,
    )


@catering_bp.route(
    "/transfers/create",
    methods=["GET", "POST"],
)
@login_required
@require_permission(
    CATERING_STOCK_TRANSFER_CREATE.name
)
def create_transfer():
    """
    Create a Draft Stock Transfer.
    """

    form = StockTransferForm()

    stock_item_service = StockItemService()
    location_service = InventoryLocationService()

    stock_items = stock_item_service.get_all()
    locations = location_service.get_all()

    form.stock_item_id.choices = [
        (
            stock_item.id,
            (
                stock_item.product.name
                if stock_item.product
                else str(stock_item.id)
            ),
        )
        for stock_item in stock_items
        if stock_item.is_active
    ]

    form.source_location_id.choices = [
        (
            location.id,
            location.name,
        )
        for location in locations
        if location.is_active
    ]

    form.destination_location_id.choices = [
        (
            location.id,
            location.name,
        )
        for location in locations
        if location.is_active
    ]

    if form.validate_on_submit():

        service = StockTransferService(
            authorization_adapter=(
                _build_catering_authorization_adapter()
            )
        )

        transfer = service.create(
            service.repository.model(
                stock_item_id=form.stock_item_id.data,
                source_location_id=form.source_location_id.data,
                destination_location_id=form.destination_location_id.data,
                quantity=form.quantity.data,
                reference=form.reference.data,
                reason=form.reason.data,
                status="DRAFT",
                occurred_at=form.occurred_at.data,
            ),
            subject=current_user,
        )

        flash(
            "Stock transfer created successfully.",
            "success",
        )

        return redirect(
            url_for(
                "catering.transfers"
            )
        )

    return render_template(
        "modules/catering/transfers/create.html",
        form=form,
    )


@catering_bp.route(
    "/transfers/<int:transfer_id>/post",
    methods=["POST"],
)
@login_required
@require_permission(
    CATERING_STOCK_TRANSFER_POST.name
)
def post_transfer(
    transfer_id,
):
    """
    Post a Draft Stock Transfer.
    """

    service = StockTransferService(
        authorization_adapter=(
            _build_catering_authorization_adapter()
        )
    )

    try:
        transfer = service.get(
            transfer_id
        )

    except EntityNotFoundException:
        flash(
            "Stock transfer not found.",
            "error",
        )

        return redirect(
            url_for(
                "catering.transfers"
            )
        )

    try:
        service.post_transfer(
            transfer,
            subject=current_user,
        )

    except (ValueError, RuntimeError) as exc:
        flash(
            str(exc),
            "error",
        )

        return redirect(
            url_for(
                "catering.transfers"
            )
        )

    flash(
        "Stock transfer posted successfully.",
        "success",
    )

    return redirect(
        url_for(
            "catering.transfers"
        )
    )


__all__ = [
    "index",
    "categories",
    "create_category",
    "activate_category",
    "deactivate_category",
    "products",
    "create_product",
    "activate_product",
    "deactivate_product",
    "stock_items",
    "create_stock_item",
    "locations",
    "create_location",
    "balances",
    "movements",
    "create_movement",
    "post_movement",
    "transfers",
    "create_transfer",
    "post_transfer",
]
