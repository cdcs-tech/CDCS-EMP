"""
CDCS Enterprise Management Platform (CDCS-EMP)

Enterprise Event Framework

Event Handler Foundation

Defines the standard contract
for event consumers.
"""


from abc import ABC, abstractmethod



class BaseEventHandler(ABC):
    """
    Abstract base class for event handlers.
    """



    @abstractmethod
    def handle(
        self,
        event,
    ):
        """
        Process an event.

        Every handler must implement this method.
        """

        raise NotImplementedError



    def supports(
        self,
        event,
    ):
        """
        Optional handler filtering hook.

        Override when a handler needs
        conditional processing.
        """

        return True



    def __repr__(self):

        return (
            f"<EventHandler "
            f"{self.__class__.__name__}>"
        )
