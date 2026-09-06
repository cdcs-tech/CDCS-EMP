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
from flask_login import current_user
from flask_login import login_required

from app.core.crud.exceptions import EntityNotFoundException
from app.core.data import QueryOptions

from app.security.decorators import require_permission

from app.modules.catering.forms import (
    InventoryLocationForm,
    ProductCategoryForm,
    ProductForm,
    StockItemForm,
    StockMovementForm,
    StockTransferForm,
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
)

from app.modules.catering.services import (
    InventoryLocationService,
    ProductCategoryService,
    ProductService,
    StockBalanceService,
    StockItemService,
    StockMovementService,
    StockTransferService,
)

from app.modules.catering.security.authorization import (
    CateringAuthorizationAdapter,
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
