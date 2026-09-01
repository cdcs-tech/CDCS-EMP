"""
CDCS Enterprise Management Platform (CDCS-EMP)

Catering Module

Routes.
"""

from flask import flash
from flask import redirect
from flask import render_template
from flask import url_for
from flask_login import login_required

from app.security.decorators import require_permission

from app.modules.catering.forms import (
    ProductCategoryForm,
)
from app.modules.catering.security import (
    CATERING_PRODUCT_CATEGORY_CREATE,
    CATERING_PRODUCT_CATEGORY_READ,
)
from app.modules.catering.services import (
    ProductCategoryService,
)

from . import catering_bp


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
        "modules/catering/index.html"
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

    product_categories = service.get_all()

    return render_template(
        "modules/catering/categories/index.html",
        product_categories=product_categories,
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


__all__ = [
    "index",
    "categories",
    "create_category",
]
