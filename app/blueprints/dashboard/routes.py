from flask_login import login_required

from app.security.decorators import permission_required

from . import dashboard_bp


@dashboard_bp.route("/")
@login_required
def index():

    return render_template(
        "dashboard/index.html"
    )


@dashboard_bp.route("/admin-test")
@login_required
@permission_required(
    "system.admin"
)
def admin_test():

    return "Administrator access granted"
