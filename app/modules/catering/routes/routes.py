"""
CDCS Enterprise Management Platform (CDCS-EMP)

Catering Module

Routes.
"""

from flask import flash
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for
from flask_login import login_required
from flask_login import current_user
from flask_login import login_required

from app.core.data import QueryOptions

from app.security.decorators import require_permission

from app.modules.catering.forms import (
    ProductCategoryForm,
    ProductForm,
)

from app.modules.catering.security import (
    CATERING_PRODUCT_CATEGORY_CREATE,
    CATERING_PRODUCT_CATEGORY_READ,
    CATERING_PRODUCT_CATEGORY_UPDATE,
    CATERING_PRODUCT_CREATE,
    CATERING_PRODUCT_READ,
    CATERING_PRODUCT_UPDATE,
)

from app.modules.catering.services import (
    ProductCategoryService,
    ProductService,
)

from . import catering_bp


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
    Translate the Catering status query parameter into
    an explicit repository filter.

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

        if parsed_category_id is not None and parsed_category_id >= 1:
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
        can_read_categories=current_user.has_permission(
            CATERING_PRODUCT_CATEGORY_READ.name
        ),
        can_read_products=current_user.has_permission(
            CATERING_PRODUCT_READ.name
        ),
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
]
