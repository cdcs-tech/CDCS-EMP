"""
CDCS Enterprise Management Platform (CDCS-EMP)

Enterprise Module Framework Exceptions

Provides specialized exceptions used by the
module registration and discovery system.
"""


class ModuleFrameworkException(Exception):
    """
    Base exception for all module framework errors.
    """

    pass


class ModuleRegistrationException(ModuleFrameworkException):
    """
    Raised when a module cannot be registered.
    """

    pass


class ModuleAlreadyRegisteredException(ModuleFrameworkException):
    """
    Raised when attempting to register a duplicate module.
    """

    pass


class ModuleNotFoundException(ModuleFrameworkException):
    """
    Raised when a requested module does not exist.
    """

    pass


class InvalidModuleMetadataException(ModuleFrameworkException):
    """
    Raised when module metadata fails validation.
    """

    pass


class ModuleDependencyException(ModuleFrameworkException):
    """
    Raised when module dependencies cannot be resolved.
    """

    pass


class ModuleInitializationException(ModuleFrameworkException):
    """
    Raised when a module fails during initialization.
    """

    pass
