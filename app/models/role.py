"""
Role Model
"""

from app.extensions import db
from .base import BaseModel
from .mixins import TimestampMixin


class Role(BaseModel, TimestampMixin):
    __tablename__ = "roles"

    name = db.Column(
        db.String(100),
        unique=True,
        nullable=False,
        index=True,
    )

    description = db.Column(
        db.String(255),
        nullable=True,
    )

    is_system = db.Column(
        db.Boolean,
        default=False,
        nullable=False,
    )

    user_roles = db.relationship(
        "UserRole",
        back_populates="role",
        cascade="all, delete-orphan",
    )

    role_permissions = db.relationship(
        "RolePermission",
        back_populates="role",
        cascade="all, delete-orphan",
    )

    def __repr__(self):
        return f"<Role(name='{self.name}')>"
