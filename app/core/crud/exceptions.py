"""
CDCS Enterprise Management Platform (CDCS-EMP)

Generic CRUD Framework

Standard CRUD exception definitions.
"""


class CRUDException(Exception):
    """
    Base exception for CRUD operations.
    """

    def __init__(
        self,
        message: str,
    ):
        self.message = message

        super().__init__(
            message
        )


class EntityNotFoundException(
    CRUDException
):
    """
    Raised when an entity cannot be found.
    """

    def __init__(
        self,
        entity_name: str,
        entity_id,
    ):
        super().__init__(
            (
                f"{entity_name} with id "
                f"{entity_id} was not found."
            )
        )

        self.entity_name = entity_name

        self.entity_id = entity_id


class EntityValidationException(
    CRUDException
):
    """
    Raised when entity validation fails.
    """

    pass


class DuplicateEntityException(
    CRUDException
):
    """
    Raised when a duplicate entity exists.
    """

    pass


class InvalidCRUDOperationException(
    CRUDException
):
    """
    Raised when an invalid CRUD operation
    is attempted.
    """

    pass
