"""
CDCS Enterprise Management Platform (CDCS-EMP)

Authentication Services
"""

from flask import session
from flask_login import login_user

from app.extensions import bcrypt
from app.extensions import db
from app.models import User


class AuthenticationService:
    """
    Authentication service.
    """

    @staticmethod
    def authenticate(
        username,
        password,
        remember=False,
    ):
        user = User.query.filter_by(
            username=username
        ).first()

        if user is None:
            return None

        if not user.is_active:
            return None

        if user.is_deleted:
            return None

        if not user.check_password(password):
            return None

        login_user(
            user,
            remember=remember,
        )

        session.permanent = True

        user.update_last_login()

        db.session.commit()

        return user
