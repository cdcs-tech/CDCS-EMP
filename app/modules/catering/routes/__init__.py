"""
CDCS Enterprise Management Platform (CDCS-EMP)

Catering Module

HTTP blueprint.
"""

from flask import Blueprint


catering_bp = Blueprint(
    "catering",
    __name__,
)


from . import routes
