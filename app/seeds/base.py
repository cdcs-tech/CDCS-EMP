"""
CDCS Enterprise Management Platform (CDCS-EMP)

Seeder Base Class
"""

from abc import ABC
from abc import abstractmethod

from app.extensions import db


class BaseSeeder(ABC):
    """
    Base class for all database seeders.

    Responsibilities:

    - Standard logging
    - Transaction management
    - Rollback on failure
    - Common helper methods
    """

    name = "Base Seeder"

    def log(self, message):

        print(f"[{self.name}] {message}")

    def exists(self, model, **filters):

        return model.query.filter_by(
            **filters
        ).first()

    def commit(self):

        try:

            db.session.commit()

        except Exception:

            db.session.rollback()

            raise

    def add(self, entity):

        db.session.add(entity)

    def add_all(self, entities):

        db.session.add_all(entities)

    @abstractmethod
    def run(self):
        """
        Execute the seeder.
        """
        raise NotImplementedError
