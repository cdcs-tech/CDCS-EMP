"""
CDCS Enterprise Management Platform (CDCS-EMP)

User Model
"""

from datetime import datetime

from flask_login import UserMixin

from app.extensions import bcrypt, db

from .base import BaseModel
from .mixins import (
    AuditMixin,
    SoftDeleteMixin,
    TimestampMixin,
)


class User(
    UserMixin,
    BaseModel,
    TimestampMixin,
    AuditMixin,
    SoftDeleteMixin,
):
    """
    Platform user.
    """

    __tablename__ = "users"

    username = db.Column(
        db.String(50),
        unique=True,
        nullable=False,
        index=True,
    )

    email = db.Column(
        db.String(255),
        unique=True,
        nullable=False,
        index=True,
    )

    password_hash = db.Column(
        db.String(255),
        nullable=False,
    )

    first_name = db.Column(
        db.String(100),
        nullable=False,
    )

    last_name = db.Column(
        db.String(100),
        nullable=False,
    )

    is_active = db.Column(
        db.Boolean,
        nullable=False,
        default=True,
    )

    last_login = db.Column(
        db.DateTime,
        nullable=True,
    )

    user_roles = db.relationship(
    "UserRole",
    back_populates="user",
    cascade="all, delete-orphan",
    )

    def set_password(self, password):
        """
        Hash and store a password.
        """
        self.password_hash = bcrypt.generate_password_hash(
            password
        ).decode("utf-8")

    def check_password(self, password):
        """
        Verify a password.
        """
        return bcrypt.check_password_hash(
            self.password_hash,
            password,
        )

    @property
    def full_name(self):
        """
        Return the user's full name.
        """
        return f"{self.first_name} {self.last_name}"

    def update_last_login(self):
        """
        Record the user's last successful login.
        """
        self.last_login = datetime.utcnow()

    def __repr__(self):
        return (
            f"<User(id={self.id}, "
            f"username='{self.username}')>"
        )
