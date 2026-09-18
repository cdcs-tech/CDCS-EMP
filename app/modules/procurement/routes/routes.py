"""
CDCS Enterprise Management Platform (CDCS-EMP)

Procurement Module

HTTP routes.
"""

from __future__ import annotations

from flask import (
    Blueprint,
    abort,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)
from flask_login import login_required

from app.core.data import QueryOptions
from app.modules.procurement.forms import (
    PurchaseOrderForm,
    PurchaseRequestForm,
    PurchaseRequestLineForm,
    PurchaseRequirementForm,
    SupplierForm,
)
from app.modules.procurement.models import (
    PurchaseOrder,
    PurchaseRequest,
    PurchaseRequestLine,
    PurchaseRequirement,
    Supplier,
)
from app.modules.procurement.security import (
    PROCUREMENT_PURCHASE_ORDER_CREATE,
    PROCUREMENT_PURCHASE_ORDER_DELETE,
    PROCUREMENT_PURCHASE_ORDER_READ,
    PROCUREMENT_PURCHASE_ORDER_UPDATE,
    PROCUREMENT_PURCHASE_REQUEST_CREATE,
    PROCUREMENT_PURCHASE_REQUEST_DELETE,
    PROCUREMENT_PURCHASE_REQUEST_LINE_CREATE,
    PROCUREMENT_PURCHASE_REQUEST_LINE_READ,
    PROCUREMENT_PURCHASE_REQUEST_LINE_UPDATE,
    PROCUREMENT_PURCHASE_REQUEST_LINE_DELETE,
    PROCUREMENT_PURCHASE_REQUEST_READ,
    PROCUREMENT_PURCHASE_REQUEST_UPDATE,
    PROCUREMENT_PURCHASE_REQUIREMENT_CREATE,
    PROCUREMENT_PURCHASE_REQUIREMENT_DELETE,
    PROCUREMENT_PURCHASE_REQUIREMENT_READ,
    PROCUREMENT_PURCHASE_REQUIREMENT_UPDATE,
    PROCUREMENT_SUPPLIER_CREATE,
    PROCUREMENT_SUPPLIER_DELETE,
    PROCUREMENT_SUPPLIER_READ,
    PROCUREMENT_SUPPLIER_UPDATE,
)
from app.modules.procurement.services import (
    PurchaseOrderService,
    PurchaseRequestLineService,
    PurchaseRequestService,
    PurchaseRequirementService,
    SupplierService,
)
from app.security.decorators import require_permission


procurement_bp = Blueprint(
    "procurement",
    __name__,
)


_SUPPLIER_SORT_FIELDS = {
    "name",
    "code",
    "supplier_type",
    "status",
}


_PURCHASE_REQUIREMENT_SORT_FIELDS = {
    "reference",
    "description",
    "source_module",
    "required_by_date",
    "status",
}


_PURCHASE_REQUEST_SORT_FIELDS = {
    "reference",
    "purchase_requirement_id",
    "request_date",
    "required_by_date",
    "status",
}


_PURCHASE_ORDER_SORT_FIELDS = {
    "reference",
    "supplier_id",
    "order_date",
    "expected_delivery_date",
    "status",
    "purchase_request_id",
}


def _parse_positive_int(
    value,
    default: int,
) -> int:
    """
    Parse a positive integer query parameter.
    """

    try:
        parsed = int(value)
    except (TypeError, ValueError):
        return default

    if parsed < 1:
        return default

    return parsed


def _parse_page_size(
    value,
) -> int:
    """
    Parse the list page size.
    """

    page_size = _parse_positive_int(
        value,
        20,
    )

    return min(
        page_size,
        100,
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

    if str(value).lower() == "desc":
        return "desc"

    return "asc"


def _parse_status_filter(
    value,
) -> dict[str, str]:
    """
    Build a controlled status filter.
    """

    if not value:
        return {}

    return {
        "status": value,
    }


def _build_supplier_query_options() -> QueryOptions:
    """
    Build controlled query options for Suppliers.
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
            _SUPPLIER_SORT_FIELDS,
            "name",
        ),
        sort_direction=_parse_sort_direction(
            request.args.get("direction"),
        ),
        search=request.args.get(
            "search"
        ),
        filters=_parse_status_filter(
            request.args.get("status")
        ),
    )


def _build_purchase_requirement_query_options() -> QueryOptions:
    """
    Build controlled query options for Purchase Requirements.
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
            _PURCHASE_REQUIREMENT_SORT_FIELDS,
            "reference",
        ),
        sort_direction=_parse_sort_direction(
            request.args.get("direction"),
        ),
        search=request.args.get(
            "search"
        ),
        filters=_parse_status_filter(
            request.args.get("status")
        ),
    )


def _build_purchase_request_query_options() -> QueryOptions:
    """
    Build controlled query options for Purchase Requests.
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
            _PURCHASE_REQUEST_SORT_FIELDS,
            "reference",
        ),
        sort_direction=_parse_sort_direction(
            request.args.get("direction"),
        ),
        search=request.args.get(
            "search"
        ),
        filters=_parse_status_filter(
            request.args.get("status")
        ),
    )


def _build_purchase_order_query_options() -> QueryOptions:
    """
    Build controlled query options for Purchase Orders.
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
            _PURCHASE_ORDER_SORT_FIELDS,
            "reference",
        ),
        sort_direction=_parse_sort_direction(
            request.args.get("direction"),
        ),
        search=request.args.get(
            "search"
        ),
        filters=_parse_status_filter(
            request.args.get("status")
        ),
    )


def _load_purchase_requirement_choices(
    form: PurchaseRequestForm,
) -> None:
    """
    Populate Purchase Request Purchase Requirement choices.

    The selection is populated through the existing
    Purchase Requirement service and pagination contract.
    """

    service = PurchaseRequirementService()

    result = service.paginate(
        QueryOptions(
            page=1,
            page_size=1000,
            sort_by="reference",
            sort_direction="asc",
        )
    )

    form.purchase_requirement_id.choices = [
        (
            requirement.id,
            requirement.reference,
        )
        for requirement in result.items
    ]


def _load_purchase_order_choices(
    form: PurchaseOrderForm,
) -> None:
    """
    Populate Purchase Order Supplier and Purchase Request choices.

    The selections are populated through the existing
    Supplier and Purchase Request services and pagination
    contracts.
    """

    supplier_service = SupplierService()

    supplier_result = supplier_service.paginate(
        QueryOptions(
            page=1,
            page_size=1000,
            sort_by="name",
            sort_direction="asc",
        )
    )

    form.supplier_id.choices = [
        (
            supplier.id,
            supplier.name,
        )
        for supplier in supplier_result.items
    ]

    purchase_request_service = PurchaseRequestService()

    purchase_request_result = (
        purchase_request_service.paginate(
            QueryOptions(
                page=1,
                page_size=1000,
                sort_by="reference",
                sort_direction="asc",
            )
        )
    )

    form.purchase_request_id.choices = [
        (
            purchase_request.id,
            purchase_request.reference,
        )
        for purchase_request in purchase_request_result.items
    ]


@procurement_bp.route(
    "/suppliers/",
    methods=["GET"],
)
@login_required
@require_permission(PROCUREMENT_SUPPLIER_READ.name)
def suppliers():
    """
    Render the Procurement Supplier management list.
    """

    service = SupplierService()
    query_options = _build_supplier_query_options()

    result = service.paginate(
        query_options
    )

    return render_template(
        "modules/procurement/suppliers/index.html",
        suppliers=result,
        query_options=query_options,
    )


@procurement_bp.route(
    "/suppliers/create",
    methods=["GET", "POST"],
)
@login_required
@require_permission(PROCUREMENT_SUPPLIER_CREATE.name)
def create_supplier():
    """
    Create a Procurement Supplier.
    """

    form = SupplierForm()

    if form.validate_on_submit():
        service = SupplierService()

        supplier = service.create(
            Supplier(
                name=form.name.data,
                code=form.code.data,
                supplier_type=form.supplier_type.data,
                contact_information=form.contact_information.data,
                address_information=form.address_information.data,
                status=form.status.data,
            )
        )

        flash(
            "Supplier created successfully.",
            "success",
        )

        return redirect(
            url_for(
                "procurement.suppliers"
            )
        )

    return render_template(
        "modules/procurement/suppliers/create.html",
        form=form,
    )


@procurement_bp.route(
    "/suppliers/<int:supplier_id>",
    methods=["GET"],
)
@login_required
@require_permission(PROCUREMENT_SUPPLIER_READ.name)
def view_supplier(
    supplier_id: int,
):
    """
    View a Procurement Supplier.
    """

    service = SupplierService()

    supplier = service.get(
        supplier_id
    )

    return render_template(
        "modules/procurement/suppliers/view.html",
        supplier=supplier,
    )


@procurement_bp.route(
    "/suppliers/<int:supplier_id>/edit",
    methods=["GET", "POST"],
)
@login_required
@require_permission(PROCUREMENT_SUPPLIER_UPDATE.name)
def edit_supplier(
    supplier_id: int,
):
    """
    Edit a Procurement Supplier.
    """

    service = SupplierService()

    supplier = service.get(
        supplier_id
    )

    form = SupplierForm(
        obj=supplier
    )

    if form.validate_on_submit():
        supplier.name = form.name.data
        supplier.code = form.code.data
        supplier.supplier_type = form.supplier_type.data
        supplier.contact_information = (
            form.contact_information.data
        )
        supplier.address_information = (
            form.address_information.data
        )
        supplier.status = form.status.data

        service.update(
            supplier
        )

        flash(
            "Supplier updated successfully.",
            "success",
        )

        return redirect(
            url_for(
                "procurement.view_supplier",
                supplier_id=supplier.id,
            )
        )

    return render_template(
        "modules/procurement/suppliers/edit.html",
        form=form,
        supplier=supplier,
    )


@procurement_bp.route(
    "/suppliers/<int:supplier_id>/delete",
    methods=["POST"],
)
@login_required
@require_permission(PROCUREMENT_SUPPLIER_DELETE.name)
def delete_supplier(
    supplier_id: int,
):
    """
    Delete a Procurement Supplier.
    """

    service = SupplierService()

    service.delete(
        supplier_id
    )

    flash(
        "Supplier deleted successfully.",
        "success",
    )

    return redirect(
        url_for(
            "procurement.suppliers"
        )
    )


@procurement_bp.route(
    "/purchase-requirements/",
    methods=["GET"],
)
@login_required
@require_permission(
    PROCUREMENT_PURCHASE_REQUIREMENT_READ.name
)
def purchase_requirements():
    """
    Render the Procurement Purchase Requirement management list.
    """

    service = PurchaseRequirementService()
    query_options = (
        _build_purchase_requirement_query_options()
    )

    result = service.paginate(
        query_options
    )

    return render_template(
        "modules/procurement/purchase_requirements/index.html",
        purchase_requirements=result,
        query_options=query_options,
    )


@procurement_bp.route(
    "/purchase-requirements/create",
    methods=["GET", "POST"],
)
@login_required
@require_permission(
    PROCUREMENT_PURCHASE_REQUIREMENT_CREATE.name
)
def create_purchase_requirement():
    """
    Create a Procurement Purchase Requirement.
    """

    form = PurchaseRequirementForm()

    if form.validate_on_submit():
        service = PurchaseRequirementService()

        purchase_requirement = service.create(
            PurchaseRequirement(
                reference=form.reference.data,
                description=form.description.data,
                source_module=form.source_module.data,
                source_type=form.source_type.data,
                source_reference=form.source_reference.data,
                required_by_date=form.required_by_date.data,
                status=form.status.data,
            )
        )

        flash(
            "Purchase requirement created successfully.",
            "success",
        )

        return redirect(
            url_for(
                "procurement.purchase_requirements"
            )
        )

    return render_template(
        "modules/procurement/purchase_requirements/create.html",
        form=form,
    )


@procurement_bp.route(
    "/purchase-requirements/<int:purchase_requirement_id>",
    methods=["GET"],
)
@login_required
@require_permission(
    PROCUREMENT_PURCHASE_REQUIREMENT_READ.name
)
def view_purchase_requirement(
    purchase_requirement_id: int,
):
    """
    View a Procurement Purchase Requirement.
    """

    service = PurchaseRequirementService()

    purchase_requirement = service.get(
        purchase_requirement_id
    )

    return render_template(
        "modules/procurement/purchase_requirements/view.html",
        purchase_requirement=purchase_requirement,
    )


@procurement_bp.route(
    "/purchase-requirements/<int:purchase_requirement_id>/edit",
    methods=["GET", "POST"],
)
@login_required
@require_permission(
    PROCUREMENT_PURCHASE_REQUIREMENT_UPDATE.name
)
def edit_purchase_requirement(
    purchase_requirement_id: int,
):
    """
    Edit a Procurement Purchase Requirement.
    """

    service = PurchaseRequirementService()

    purchase_requirement = service.get(
        purchase_requirement_id
    )

    form = PurchaseRequirementForm(
        obj=purchase_requirement
    )

    if form.validate_on_submit():
        purchase_requirement.reference = (
            form.reference.data
        )
        purchase_requirement.description = (
            form.description.data
        )
        purchase_requirement.source_module = (
            form.source_module.data
        )
        purchase_requirement.source_type = (
            form.source_type.data
        )
        purchase_requirement.source_reference = (
            form.source_reference.data
        )
        purchase_requirement.required_by_date = (
            form.required_by_date.data
        )
        purchase_requirement.status = (
            form.status.data
        )

        service.update(
            purchase_requirement
        )

        flash(
            "Purchase requirement updated successfully.",
            "success",
        )

        return redirect(
            url_for(
                "procurement.view_purchase_requirement",
                purchase_requirement_id=(
                    purchase_requirement.id
                ),
            )
        )

    return render_template(
        "modules/procurement/purchase_requirements/edit.html",
        form=form,
        purchase_requirement=purchase_requirement,
    )


@procurement_bp.route(
    "/purchase-requirements/<int:purchase_requirement_id>/delete",
    methods=["POST"],
)
@login_required
@require_permission(
    PROCUREMENT_PURCHASE_REQUIREMENT_DELETE.name
)
def delete_purchase_requirement(
    purchase_requirement_id: int,
):
    """
    Delete a Procurement Purchase Requirement.
    """

    service = PurchaseRequirementService()

    service.delete(
        purchase_requirement_id
    )

    flash(
        "Purchase requirement deleted successfully.",
        "success",
    )

    return redirect(
        url_for(
            "procurement.purchase_requirements"
        )
    )


@procurement_bp.route(
    "/purchase-requests/",
    methods=["GET"],
)
@login_required
@require_permission(
    PROCUREMENT_PURCHASE_REQUEST_READ.name
)
def purchase_requests():
    """
    Render the Procurement Purchase Request management list.
    """

    service = PurchaseRequestService()
    query_options = (
        _build_purchase_request_query_options()
    )

    result = service.paginate(
        query_options
    )

    return render_template(
        "modules/procurement/purchase_requests/index.html",
        purchase_requests=result,
        query_options=query_options,
    )


@procurement_bp.route(
    "/purchase-requests/create",
    methods=["GET", "POST"],
)
@login_required
@require_permission(
    PROCUREMENT_PURCHASE_REQUEST_CREATE.name
)
def create_purchase_request():
    """
    Create a Procurement Purchase Request.
    """

    form = PurchaseRequestForm()

    _load_purchase_requirement_choices(
        form
    )

    if form.validate_on_submit():
        service = PurchaseRequestService()

        purchase_request = service.create(
            PurchaseRequest(
                reference=form.reference.data,
                purchase_requirement_id=(
                    form.purchase_requirement_id.data
                ),
                request_date=form.request_date.data,
                required_by_date=form.required_by_date.data,
                status=form.status.data,
                justification=form.justification.data,
                notes=form.notes.data,
            )
        )

        flash(
            "Purchase request created successfully.",
            "success",
        )

        return redirect(
            url_for(
                "procurement.purchase_requests"
            )
        )

    return render_template(
        "modules/procurement/purchase_requests/create.html",
        form=form,
    )


@procurement_bp.route(
    "/purchase-requests/<int:purchase_request_id>",
    methods=["GET"],
)
@login_required
@require_permission(
    PROCUREMENT_PURCHASE_REQUEST_READ.name
)
def view_purchase_request(
    purchase_request_id: int,
):
    """
    View a Procurement Purchase Request.
    """

    service = PurchaseRequestService()

    purchase_request = service.get(
        purchase_request_id
    )

    return render_template(
        "modules/procurement/purchase_requests/view.html",
        purchase_request=purchase_request,
    )


@procurement_bp.route(
    "/purchase-requests/<int:purchase_request_id>/edit",
    methods=["GET", "POST"],
)
@login_required
@require_permission(
    PROCUREMENT_PURCHASE_REQUEST_UPDATE.name
)
def edit_purchase_request(
    purchase_request_id: int,
):
    """
    Edit a Procurement Purchase Request.
    """

    service = PurchaseRequestService()

    purchase_request = service.get(
        purchase_request_id
    )

    form = PurchaseRequestForm(
        obj=purchase_request
    )

    _load_purchase_requirement_choices(
        form
    )

    if form.validate_on_submit():
        purchase_request.reference = (
            form.reference.data
        )
        purchase_request.purchase_requirement_id = (
            form.purchase_requirement_id.data
        )
        purchase_request.request_date = (
            form.request_date.data
        )
        purchase_request.required_by_date = (
            form.required_by_date.data
        )
        purchase_request.status = (
            form.status.data
        )
        purchase_request.justification = (
            form.justification.data
        )
        purchase_request.notes = (
            form.notes.data
        )

        service.update(
            purchase_request
        )

        flash(
            "Purchase request updated successfully.",
            "success",
        )

        return redirect(
            url_for(
                "procurement.view_purchase_request",
                purchase_request_id=(
                    purchase_request.id
                ),
            )
        )

    return render_template(
        "modules/procurement/purchase_requests/edit.html",
        form=form,
        purchase_request=purchase_request,
    )


@procurement_bp.route(
    "/purchase-requests/<int:purchase_request_id>/delete",
    methods=["POST"],
)
@login_required
@require_permission(
    PROCUREMENT_PURCHASE_REQUEST_DELETE.name
)
def delete_purchase_request(
    purchase_request_id: int,
):
    """
    Delete a Procurement Purchase Request.
    """

    service = PurchaseRequestService()

    service.delete(
        purchase_request_id
    )

    flash(
        "Purchase request deleted successfully.",
        "success",
    )

    return redirect(
        url_for(
            "procurement.purchase_requests"
        )
    )


@procurement_bp.route(
    "/purchase-requests/<int:purchase_request_id>/lines/create",
    methods=["GET", "POST"],
)
@login_required
@require_permission(
    PROCUREMENT_PURCHASE_REQUEST_LINE_CREATE.name
)
def create_purchase_request_line(
    purchase_request_id: int,
):
    purchase_request_service = PurchaseRequestService()

    purchase_request = purchase_request_service.get(
        purchase_request_id
    )

    if purchase_request is None:
        abort(404)

    form = PurchaseRequestLineForm()

    if form.validate_on_submit():
        service = PurchaseRequestLineService()

        line = PurchaseRequestLine(
            purchase_request_id=purchase_request_id,
            description=form.description.data,
            item_reference=form.item_reference.data,
            quantity=form.quantity.data,
            unit=form.unit.data,
            estimated_unit_cost=form.estimated_unit_cost.data,
            estimated_total=form.estimated_total.data,
            required_by_date=form.required_by_date.data,
            notes=form.notes.data,
        )

        service.create(line)

        flash(
            "Purchase request line created successfully.",
            "success",
        )

        return redirect(
            url_for(
                "procurement.view_purchase_request",
                purchase_request_id=purchase_request_id,
            )
        )

    return render_template(
        "modules/procurement/purchase_requests/line_form.html",
        form=form,
        purchase_request=purchase_request,
        page_title="Add Purchase Request Line",
    )


@procurement_bp.route(
    "/purchase-requests/<int:purchase_request_id>/lines/<int:line_id>/edit",
    methods=["GET", "POST"],
)
@login_required
@require_permission(
    PROCUREMENT_PURCHASE_REQUEST_LINE_UPDATE.name
)
def edit_purchase_request_line(
    purchase_request_id: int,
    line_id: int,
):
    purchase_request_service = PurchaseRequestService()

    purchase_request = purchase_request_service.get(
        purchase_request_id
    )

    if purchase_request is None:
        abort(404)

    service = PurchaseRequestLineService()
    line = service.get(line_id)

    if line is None or line.purchase_request_id != purchase_request_id:
        abort(404)

    form = PurchaseRequestLineForm(
        obj=line
    )

    if form.validate_on_submit():
        line.description = form.description.data
        line.item_reference = form.item_reference.data
        line.quantity = form.quantity.data
        line.unit = form.unit.data
        line.estimated_unit_cost = form.estimated_unit_cost.data
        line.estimated_total = form.estimated_total.data
        line.required_by_date = form.required_by_date.data
        line.notes = form.notes.data

        service.update(line)

        flash(
            "Purchase request line updated successfully.",
            "success",
        )

        return redirect(
            url_for(
                "procurement.view_purchase_request",
                purchase_request_id=purchase_request_id,
            )
        )

    return render_template(
        "modules/procurement/purchase_requests/line_form.html",
        form=form,
        purchase_request=purchase_request,
        line=line,
        page_title="Edit Purchase Request Line",
    )


@procurement_bp.route(
    "/purchase-requests/<int:purchase_request_id>/lines/<int:line_id>/delete",
    methods=["POST"],
)
@login_required
@require_permission(
    PROCUREMENT_PURCHASE_REQUEST_LINE_DELETE.name
)
def delete_purchase_request_line(
    purchase_request_id: int,
    line_id: int,
):
    purchase_request_service = PurchaseRequestService()

    purchase_request = purchase_request_service.get(
        purchase_request_id
    )

    if purchase_request is None:
        abort(404)

    service = PurchaseRequestLineService()
    line = service.get(line_id)

    if line is None or line.purchase_request_id != purchase_request_id:
        abort(404)

    service.delete(line_id)

    flash(
        "Purchase request line deleted successfully.",
        "success",
    )

    return redirect(
        url_for(
            "procurement.view_purchase_request",
            purchase_request_id=purchase_request_id,
        )
    )


@procurement_bp.route(
    "/purchase-orders/",
    methods=["GET"],
)
@login_required
@require_permission(
    PROCUREMENT_PURCHASE_ORDER_READ.name
)
def purchase_orders():
    """
    Render the Procurement Purchase Order management list.
    """

    service = PurchaseOrderService()
    query_options = (
        _build_purchase_order_query_options()
    )

    result = service.paginate(
        query_options
    )

    return render_template(
        "modules/procurement/purchase_orders/index.html",
        purchase_orders=result,
        query_options=query_options,
    )


@procurement_bp.route(
    "/purchase-orders/create",
    methods=["GET", "POST"],
)
@login_required
@require_permission(
    PROCUREMENT_PURCHASE_ORDER_CREATE.name
)
def create_purchase_order():
    """
    Create a Procurement Purchase Order.
    """

    form = PurchaseOrderForm()

    _load_purchase_order_choices(
        form
    )

    if form.validate_on_submit():
        service = PurchaseOrderService()

        purchase_order = service.create(
            PurchaseOrder(
                reference=form.reference.data,
                supplier_id=form.supplier_id.data,
                order_date=form.order_date.data,
                expected_delivery_date=(
                    form.expected_delivery_date.data
                ),
                status=form.status.data,
                purchase_request_id=(
                    form.purchase_request_id.data
                ),
            )
        )

        flash(
            "Purchase order created successfully.",
            "success",
        )

        return redirect(
            url_for(
                "procurement.purchase_orders"
            )
        )

    return render_template(
        "modules/procurement/purchase_orders/form.html",
        form=form,
        title="New Purchase Order",
        subtitle="Create a new Procurement purchase order.",
        submit_label="Create Purchase Order",
        cancel_url=url_for(
            "procurement.purchase_orders"
        ),
    )


@procurement_bp.route(
    "/purchase-orders/<int:purchase_order_id>",
    methods=["GET"],
)
@login_required
@require_permission(
    PROCUREMENT_PURCHASE_ORDER_READ.name
)
def view_purchase_order(
    purchase_order_id: int,
):
    """
    View a Procurement Purchase Order.
    """

    service = PurchaseOrderService()

    purchase_order = service.get(
        purchase_order_id
    )

    return render_template(
        "modules/procurement/purchase_orders/view.html",
        purchase_order=purchase_order,
    )


@procurement_bp.route(
    "/purchase-orders/<int:purchase_order_id>/edit",
    methods=["GET", "POST"],
)
@login_required
@require_permission(
    PROCUREMENT_PURCHASE_ORDER_UPDATE.name
)
def edit_purchase_order(
    purchase_order_id: int,
):
    """
    Edit a Procurement Purchase Order.
    """

    service = PurchaseOrderService()

    purchase_order = service.get(
        purchase_order_id
    )

    form = PurchaseOrderForm(
        obj=purchase_order
    )

    _load_purchase_order_choices(
        form
    )

    if form.validate_on_submit():
        purchase_order.reference = (
            form.reference.data
        )
        purchase_order.supplier_id = (
            form.supplier_id.data
        )
        purchase_order.order_date = (
            form.order_date.data
        )
        purchase_order.expected_delivery_date = (
            form.expected_delivery_date.data
        )
        purchase_order.status = (
            form.status.data
        )
        purchase_order.purchase_request_id = (
            form.purchase_request_id.data
        )

        service.update(
            purchase_order
        )

        flash(
            "Purchase order updated successfully.",
            "success",
        )

        return redirect(
            url_for(
                "procurement.view_purchase_order",
                purchase_order_id=(
                    purchase_order.id
                ),
            )
        )

    return render_template(
        "modules/procurement/purchase_orders/form.html",
        form=form,
        purchase_order=purchase_order,
        title="Edit Purchase Order",
        subtitle="Update the Procurement purchase order.",
        submit_label="Save Changes",
        cancel_url=url_for(
            "procurement.view_purchase_order",
            purchase_order_id=purchase_order.id,
        ),
    )


@procurement_bp.route(
    "/purchase-orders/<int:purchase_order_id>/delete",
    methods=["POST"],
)
@login_required
@require_permission(
    PROCUREMENT_PURCHASE_ORDER_DELETE.name
)
def delete_purchase_order(
    purchase_order_id: int,
):
    """
    Delete a Procurement Purchase Order.
    """

    service = PurchaseOrderService()

    service.delete(
        purchase_order_id
    )

    flash(
        "Purchase order deleted successfully.",
        "success",
    )

    return redirect(
        url_for(
            "procurement.purchase_orders"
        )
    )


__all__ = [
    "procurement_bp",
]
