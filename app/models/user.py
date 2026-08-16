"""
CDCS Enterprise Management Platform (CDCS-EMP)

User Model
"""

from datetime import datetime

from flask_login import UserMixin

from app.extensions import bcrypt
from app.extensions import db

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

    # -------------------------------
    # Organization Relationship
    # -------------------------------

    organization_memberships = db.relationship(
        "OrganizationMembership",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    # -------------------------------
    # RBAC Relationship
    # -------------------------------

    user_roles = db.relationship(
        "UserRole",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    # -------------------------------
    # Password Management
    # -------------------------------

    def set_password(self, password):
        self.password_hash = (
            bcrypt
            .generate_password_hash(password)
            .decode("utf-8")
        )

    def check_password(self, password):
        return bcrypt.check_password_hash(
            self.password_hash,
            password,
        )

    # -------------------------------
    # User Information
    # -------------------------------

    @property
    def full_name(self):
        return (
            f"{self.first_name} "
            f"{self.last_name}"
        )

    def update_last_login(self):
        self.last_login = datetime.utcnow()

    # -------------------------------
    # RBAC Methods
    # -------------------------------

    def has_role(self, role_name):
        """
        Check whether user has a role.
        """

        for user_role in self.user_roles:

            if user_role.role.name == role_name:
                return True

        return False


    def has_permission(self, permission_name):
        """
        Check whether user has permission.
        """

        for user_role in self.user_roles:

            role = user_role.role

            for role_permission in role.role_permissions:

                if (
                    role_permission
                    .permission
                    .name
                    == permission_name
                ):
                    return True

        return False


    def get_permissions(self):
        """
        Return all effective permissions.
        """

        permissions = set()

        for user_role in self.user_roles:

            role = user_role.role

            for role_permission in role.role_permissions:

                permissions.add(
                    role_permission.permission.name
                )

        return permissions


    def __repr__(self):

        return (
            f"<User("
            f"id={self.id}, "
            f"username='{self.username}'"
            f")>"
        )
