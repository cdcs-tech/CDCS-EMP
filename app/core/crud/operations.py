"""
CDCS Enterprise Management Platform (CDCS-EMP)

Generic CRUD Framework

CRUD operation definitions.
"""

from enum import Enum


class CRUDOperation(str, Enum):
    """
    Standard CRUD operations supported
    by the enterprise platform.
    """

    CREATE = "create"

    READ = "read"

    UPDATE = "update"

    DELETE = "delete"


class CRUDAction(str, Enum):
    """
    Extended CRUD actions for enterprise
    workflows.
    """

    VIEW = "view"

    LIST = "list"

    CREATE = "create"

    EDIT = "edit"

    DELETE = "delete"


CRUD_OPERATION_MAP = {

    CRUDAction.VIEW:
        CRUDOperation.READ,

    CRUDAction.LIST:
        CRUDOperation.READ,

    CRUDAction.CREATE:
        CRUDOperation.CREATE,

    CRUDAction.EDIT:
        CRUDOperation.UPDATE,

    CRUDAction.DELETE:
        CRUDOperation.DELETE,

}
