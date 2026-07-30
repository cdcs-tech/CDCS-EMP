"""
CDCS Enterprise Management Platform (CDCS-EMP)

Authorization Decorators
"""

from functools import wraps

from flask import abort

from flask_login import current_user


def require_permission(permission):
    """
    Require a single permission.
    """

    def decorator(function):

        @wraps(function)
        def wrapper(*args, **kwargs):

            if not current_user.is_authenticated:
                abort(401)

            if not current_user.has_permission(permission):
                abort(403)

            return function(*args, **kwargs)

        return wrapper

    return decorator


def require_permissions(*permissions):
    """
    Require all specified permissions.
    """

    def decorator(function):

        @wraps(function)
        def wrapper(*args, **kwargs):

            if not current_user.is_authenticated:
                abort(401)

            for permission in permissions:
                if not current_user.has_permission(permission):
                    abort(403)

            return function(*args, **kwargs)

        return wrapper

    return decorator


def require_role(role_name):
    """
    Require a specific role.
    """

    def decorator(function):

        @wraps(function)
        def wrapper(*args, **kwargs):

            if not current_user.is_authenticated:
                abort(401)

            if not current_user.has_role(role_name):
                abort(403)

            return function(*args, **kwargs)

        return wrapper

    return decorator
