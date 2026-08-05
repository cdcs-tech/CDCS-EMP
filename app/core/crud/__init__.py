"""
CDCS Enterprise Management Platform (CDCS-EMP)

Generic CRUD Framework

Public interface for reusable CRUD
operations.
"""


from app.core.crud.service import (
    CRUDService,
)


from app.core.crud.exceptions import (
    CRUDException,
    EntityNotFoundException,
    EntityValidationException,
    DuplicateEntityException,
    InvalidCRUDOperationException,
)


from app.core.crud.operations import (
    CRUDOperation,
    CRUDAction,
    CRUD_OPERATION_MAP,
)


__all__ = [

    "CRUDService",

    "CRUDException",

    "EntityNotFoundException",

    "EntityValidationException",

    "DuplicateEntityException",

    "InvalidCRUDOperationException",

    "CRUDOperation",

    "CRUDAction",

    "CRUD_OPERATION_MAP",

]
