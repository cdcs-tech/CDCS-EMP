"""
CDCS Enterprise Management Platform (CDCS-EMP)

Catering Module

Routes.
"""

from flask import render_template
from flask_login import login_required

from app.security.decorators import require_permission

from app.modules.catering.security import (
    CATERING_PRODUCT_CATEGORY_READ,
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
