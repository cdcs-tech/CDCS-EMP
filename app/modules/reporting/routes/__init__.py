"""
CDCS-EMP Reporting Module

HTTP blueprint.
"""

from flask import Blueprint


reporting_bp = Blueprint(
    "reporting",
    __name__,
)


from app.modules.reporting.routes import routes


__all__ = [
    "reporting_bp",
]
