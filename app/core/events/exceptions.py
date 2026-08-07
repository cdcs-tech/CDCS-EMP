"""
CDCS Enterprise Management Platform (CDCS-EMP)

Enterprise Event Framework Exceptions

Provides centralized exceptions for:
- Event registration
- Event publishing
- Event handling
"""


class EventException(Exception):
    """
    Base exception for all event framework errors.
    """

    pass



class EventRegistrationException(EventException):
    """
    Raised when event registration fails.
    """

    pass



class EventPublishingException(EventException):
    """
    Raised when event publishing fails.
    """

    pass



class EventHandlerException(EventException):
    """
    Raised when event handler execution fails.
    """

    pass
