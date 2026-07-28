"""
CDCS Enterprise Management Platform (CDCS-EMP)

Flask Extensions
"""

from flask import flash
from flask import redirect
from flask import request
from flask import url_for

from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import CSRFProtect

db = SQLAlchemy()

migrate = Migrate()

bcrypt = Bcrypt()

csrf = CSRFProtect()

login_manager = LoginManager()

login_manager.login_view = "auth.login"
login_manager.login_message = "Please log in to continue."
login_manager.login_message_category = "warning"


@login_manager.unauthorized_handler
def unauthorized():
    flash(
        "Please log in to continue.",
        "warning",
    )

    return redirect(
        url_for(
            "auth.login",
            next=request.url,
        )
    )
