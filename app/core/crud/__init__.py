"""
CDCS Enterprise Management Platform (CDCS-EMP)

Generic CRUD Framework

Public interface for reusable CRUD
operations.
"""


# ---------------------------------------------------------
# Services
# ---------------------------------------------------------

from app.core.crud.service import (
    CRUDService,
)


# ---------------------------------------------------------
# Repository
# ---------------------------------------------------------

from app.core.crud.repository import (
    CRUDRepository,
)


# ---------------------------------------------------------
# Transactions
# ---------------------------------------------------------

from app.core.crud.transaction import (
    TransactionManager,
    SimpleTransactionManager,
)


# ---------------------------------------------------------
# Exceptions
# ---------------------------------------------------------

from app.core.crud.exceptions import (
    CRUDException,
    EntityNotFoundException,
    EntityValidationException,
    DuplicateEntityException,
    InvalidCRUDOperationException,
)


# ---------------------------------------------------------
# Operations
# ---------------------------------------------------------

from app.core.crud.operations import (
    CRUDOperation,
    CRUDAction,
    CRUD_OPERATION_MAP,
)


# ---------------------------------------------------------
# UI Framework
# ---------------------------------------------------------

from app.core.crud.views import (
    CRUDView,
)


from app.core.crud.forms import (
    CRUDForm,
)


from app.core.crud.tables import (
    CRUDTable,
    TableColumn,
)


__all__ = [

    # Services

    "CRUDService",


    # Repository

    "CRUDRepository",


    # Transactions

    "TransactionManager",

    "SimpleTransactionManager",


    # Exceptions

    "CRUDException",

    "EntityNotFoundException",

    "EntityValidationException",

    "DuplicateEntityException",

    "InvalidCRUDOperationException",


    # Operations

    "CRUDOperation",

    "CRUDAction",

    "CRUD_OPERATION_MAP",


    # UI Framework

    "CRUDView",

    "CRUDForm",

    "CRUDTable",

    "TableColumn",

]
