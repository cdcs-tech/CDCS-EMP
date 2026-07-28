"""
Permission Model
"""

from app.extensions import db
from .base import BaseModel
from .mixins import TimestampMixin


class Permission(BaseModel, TimestampMixin):
    __tablename__ = "permissions"

    name = db.Column(
        db.String(100),
        unique=True,
        nullable=False,
        index=True,
    )

    module = db.Column(
        db.String(100),
        nullable=False,
        index=True,
    )

    description = db.Column(
        db.String(255),
        nullable=True,
    )

    role_permissions = db.relationship(
        "RolePermission",
        back_populates="permission",
        cascade="all, delete-orphan",
    )

    def __repr__(self):
        return (
            f"<Permission(module='{self.module}', "
            f"name='{self.name}')>"
        )
