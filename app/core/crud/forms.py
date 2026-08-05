"""
CDCS Enterprise Management Platform (CDCS-EMP)

Generic CRUD Framework

Enterprise form abstraction.
"""

from __future__ import annotations

from typing import Any, Dict, Generic, TypeVar


from app.core.data import (
    BaseEntity,
)


TEntity = TypeVar(
    "TEntity",
    bound=BaseEntity,
)


class CRUDForm(
    Generic[TEntity],
):
    """
    Base enterprise CRUD form.

    Provides common behaviour for
    create and edit workflows.
    """

    def __init__(
        self,
        data: Dict[str, Any] | None = None,
        entity: TEntity | None = None,
    ):
        self.data = (
            data
            or {}
        )

        self.entity = entity

        self.errors = []


    def validate(
        self,
    ) -> bool:
        """
        Validate form data.

        Child forms should override
        this method.
        """

        self.errors.clear()

        return True


    def populate(
        self,
        entity: TEntity,
    ) -> None:
        """
        Populate form from entity.
        """

        self.entity = entity


    def get_data(
        self,
    ) -> Dict[str, Any]:
        """
        Return submitted data.
        """

        return dict(
            self.data
        )


    def save_data(
        self,
    ) -> Dict[str, Any]:
        """
        Prepare validated data
        for persistence.
        """

        if not self.validate():

            raise ValueError(
                "Form validation failed"
            )

        return self.get_data()
