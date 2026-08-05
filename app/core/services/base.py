"""
CDCS Enterprise Management Platform (CDCS-EMP)

Enterprise Services Framework

Base service foundation.
"""


from __future__ import annotations


from typing import (
    Any,
    Generic,
    TypeVar,
)


from app.core.crud import (
    CRUDRepository,
)


from app.core.data import (
    BaseEntity,
)


TEntity = TypeVar(
    "TEntity",
    bound=BaseEntity,
)



class BaseService(
    Generic[TEntity],
):
    """
    Base enterprise service.

    Provides common business service
    operations while delegating data
    access to repositories.
    """


    def __init__(
        self,
        repository: CRUDRepository[TEntity],
    ):
        """
        Initialize service.

        Repository dependency is injected.
        """

        self.repository = repository



    def get(
        self,
        entity_id: Any,
    ) -> TEntity | None:
        """
        Retrieve an entity.
        """

        return self.repository.get(
            entity_id
     )



    def get_all(
        self,
    ) -> list[TEntity]:
        """
        Retrieve all entities.
        """

        return self.repository.get_all()



    def create(
        self,
        entity: TEntity,
    ) -> TEntity:
        """
        Create entity.

        Validation hooks can be added
        by child services.
        """

        self.validate_create(
            entity
        )

        return self.repository.add(
            entity
        )



    def update(
        self,
        entity: TEntity,
    ) -> TEntity:
        """
        Update entity.
        """

        self.validate_update(
            entity
        )

        return self.repository.update(
            entity
        )



    def delete(
        self,
        entity_id: Any,
    ) -> bool:
        """
        Delete entity.
        """

        return self.repository.delete(
            entity_id
        )



    def validate_create(
        self,
        entity: TEntity,
    ) -> None:
        """
        Validation hook before creation.

        Child services override this.
        """

        return None



    def validate_update(
        self,
        entity: TEntity,
    ) -> None:
        """
        Validation hook before update.

        Child services override this.
        """

        return None



    def execute(
        self,
        operation,
        *args,
        **kwargs,
    ):
        """
        Execute custom business operation.

        Allows service-specific workflows.
        """

        return operation(
            *args,
            **kwargs
        )
