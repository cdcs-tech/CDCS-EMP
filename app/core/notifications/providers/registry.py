"""
CDCS Enterprise Management Platform (CDCS-EMP)

Enterprise Notification Framework

Notification Provider Registry

Maintains registered notification delivery
providers.
"""

from app.core.notifications.providers.base import (
    BaseNotificationProvider,
)


class NotificationProviderRegistry:
    """
    Central registry for notification
    delivery providers.
    """

    def __init__(self):
        """
        Initialize provider registry.
        """

        self._providers = {}


    def register(
        self,
        provider,
    ):
        """
        Register a notification provider.

        The provider must inherit from
        BaseNotificationProvider.
        """

        if not isinstance(
            provider,
            BaseNotificationProvider,
        ):
            raise TypeError(
                "Provider must inherit from "
                "BaseNotificationProvider."
            )


        provider_name = (
            provider.provider_name
        )


        if not provider_name:

            raise ValueError(
                "Provider name is required."
            )


        self._providers[
            provider_name
        ] = provider


    def get(
        self,
        provider_name,
    ):
        """
        Retrieve a registered provider.
        """

        return self._providers.get(
            provider_name
        )


    def has(
        self,
        provider_name,
    ):
        """
        Determine whether a provider
        is registered.
        """

        return (
            provider_name
            in self._providers
        )


    def all(self):
        """
        Return all registered providers.
        """

        return dict(
            self._providers
        )


    def count(self):
        """
        Return the number of registered
        providers.
        """

        return len(
            self._providers
        )


    def clear(self):
        """
        Clear the provider registry.

        Primarily intended for testing.
        """

        self._providers.clear()


    def __repr__(self):
        """
        Developer-friendly representation.
        """

        return (
            f"<NotificationProviderRegistry "
            f"providers={self.count()}>"
        )


notification_provider_registry = (
    NotificationProviderRegistry()
)
