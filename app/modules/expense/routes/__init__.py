"""
CDCS Enterprise Management Platform (CDCS-EMP)

Expense Management Module

HTTP blueprint.
"""

from flask import Blueprint


expense_bp = Blueprint(
    "expense",
    __name__,
)


from . import routes


__all__ = [
    "expense_bp",
]
