"""
CDCS Enterprise Management Platform (CDCS-EMP)

Generic CRUD Framework

Public interface for reusable CRUD
operations and infrastructure.
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
    SQLAlchemyTransactionManager,
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


# ---------------------------------------------------------
# Configuration Framework
# ---------------------------------------------------------

from app.core.crud.config import (
    CRUDConfig,
)


# ---------------------------------------------------------
# Registry Framework
# ---------------------------------------------------------

from app.core.crud.registry import (
    CRUDRegistry,
    CRUDDefinition,
    crud_registry,
)


__all__ = [

    # Services

    "CRUDService",


    # Repository

    "CRUDRepository",


    # Transactions

    "TransactionManager",

    "SimpleTransactionManager",

    "SQLAlchemyTransactionManager",


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


    # Configuration

    "CRUDConfig",


    # Registry

    "CRUDRegistry",

    "CRUDDefinition",

    "crud_registry",

]
