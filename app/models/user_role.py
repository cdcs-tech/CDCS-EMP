"""
UserRole Association Model
"""

from app.extensions import db
from .base import BaseModel


class UserRole(BaseModel):
    __tablename__ = "user_roles"

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False,
    )

    role_id = db.Column(
        db.Integer,
        db.ForeignKey("roles.id"),
        nullable=False,
    )

    user = db.relationship(
        "User",
        back_populates="user_roles",
    )

    role = db.relationship(
        "Role",
        back_populates="user_roles",
    )

    __table_args__ = (
        db.UniqueConstraint(
            "user_id",
            "role_id",
            name="uq_user_role",
        ),
    )
