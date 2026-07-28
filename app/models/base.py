"""
CDCS Enterprise Management Platform (CDCS-EMP)

Base Model
"""

from sqlalchemy import MetaData
from sqlalchemy.orm import declared_attr

from app.extensions import db
import uuid

from sqlalchemy.dialects.mssql import UNIQUEIDENTIFIER

# ------------------------------------------------------------------
# Naming Convention for Constraints and Indexes
# ------------------------------------------------------------------

NAMING_CONVENTION = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}

metadata = MetaData(naming_convention=NAMING_CONVENTION)


class BaseModel(db.Model):
    """
    Base model for all CDCS-EMP entities.
    """

    __abstract__ = True

    metadata = metadata

    id = db.Column(
    db.Integer,
    primary_key=True,
    autoincrement=True,
    )

    guid = db.Column(
    UNIQUEIDENTIFIER,
    nullable=False,
    unique=True,
    default=uuid.uuid4,
    )

    @declared_attr
    def __tablename__(cls):
        """
        Automatically generate table names.

        Example:
            User -> users
            Role -> roles
        """
        return cls.__name__.lower() + "s"

    def save(self):
        """
        Save the current entity.
        """
        db.session.add(self)
        db.session.commit()

    def delete(self):
        """
        Delete the current entity.
        """
        db.session.delete(self)
        db.session.commit()

    def __repr__(self):
        """
        String representation of the entity.
        """
        return f"<{self.__class__.__name__}(id={self.id})>"
