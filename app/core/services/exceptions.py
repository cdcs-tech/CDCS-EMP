"""
CDCS Enterprise Management Platform (CDCS-EMP)

Enterprise Services Framework

Service layer exceptions.
"""


class ServiceException(Exception):
    """
    Base service layer exception.

    All service exceptions inherit
    from this class.
    """

    def __init__(
        self,
        message: str,
        code: str | None = None,
    ):
        super().__init__(
            message
        )

        self.message = message

        self.code = code



class ServiceValidationException(
    ServiceException,
):
    """
    Raised when service validation fails.
    """

    pass



class ServiceNotFoundException(
    ServiceException,
):
    """
    Raised when requested entity
    cannot be found.
    """

    pass



class ServiceConflictException(
    ServiceException,
):
    """
    Raised when an operation conflicts
    with existing business data.
    """

    pass



class ServiceOperationException(
    ServiceException,
):
    """
    Raised when a service operation
    cannot be completed.
    """

    pass
