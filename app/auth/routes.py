"""
CDCS Enterprise Management Platform (CDCS-EMP)

Authentication Routes
"""

from urllib.parse import urlparse

from flask import flash
from flask import redirect
from flask import render_template
from flask import request
from flask import session
from flask import url_for

from flask_login import login_required
from flask_login import logout_user

from . import auth_bp
from .forms import LoginForm
from .services import AuthenticationService


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()

    if form.validate_on_submit():

        user = AuthenticationService.authenticate(
            username=form.username.data,
            password=form.password.data,
            remember=form.remember_me.data,
        )

        if user:

            next_page = request.args.get("next")

            if next_page:
                parsed = urlparse(next_page)

                if parsed.netloc:
                    next_page = None

            flash(
                "Login successful.",
                "success",
            )

            return redirect(
                next_page
                or url_for("dashboard.index")
            )

        flash(
            "Invalid username or password.",
            "danger",
        )

    return render_template(
        "auth/login.html",
        form=form,
    )


@auth_bp.route("/logout")
@login_required
def logout():

    logout_user()

    session.clear()

    flash(
        "You have been logged out.",
        "info",
    )

    return redirect(
        url_for("auth.login")
    )
