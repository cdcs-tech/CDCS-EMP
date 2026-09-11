"""
CDCS Enterprise Management Platform (CDCS-EMP)

Procurement Module

HTTP routes.
"""

from __future__ import annotations

from flask import (
    Blueprint,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)
from flask_login import login_required

from app.core.data import QueryOptions
from app.modules.procurement.forms import SupplierForm
from app.modules.procurement.models import Supplier
from app.modules.procurement.security import (
    PROCUREMENT_SUPPLIER_CREATE,
    PROCUREMENT_SUPPLIER_DELETE,
    PROCUREMENT_SUPPLIER_READ,
    PROCUREMENT_SUPPLIER_UPDATE,
)
from app.modules.procurement.services import SupplierService
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
    Parse the Supplier list page size.
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
    Build the controlled Supplier status filter.
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


__all__ = [
    "procurement_bp",
]
