"""
CDCS Enterprise Management Platform (CDCS-EMP)

Dashboard Routes
"""

from flask import render_template

from flask_login import login_required

from app.security.decorators import require_permission
from app.security.permissions import DASHBOARD_VIEW

from . import dashboard_bp


@dashboard_bp.route("/")
@login_required
@require_permission(DASHBOARD_VIEW)
def index():
    return render_template(
        "modules/dashboard/index.html"
    )
