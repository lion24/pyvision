"""Camera module related to camera operations."""

import abc


class VideoStreamProvider(metaclass=abc.ABCMeta):
    """Each video stream provider will need to implement this interface.

    It will define the methods needed in order to parse various video
    streams
    """

    @classmethod
    def __subclasshook__(cls, subclass: type) -> bool:
        """Check if a class or its subclasses implement all the required methods of the VideoStreamProvider interface.

        Args:
            cls (type): The class object.
            subclass (type): The subclass object.

        Returns:
            bool: True if the subclass implements all the required methods, False otherwise.
        """
        if cls is VideoStreamProvider:
            required_methods = {"start", "update", "read", "stop", "isOpened"}
            if all(
                any(method in B.__dict__ for B in subclass.__mro__)
                for method in required_methods
            ):
                return True
        return NotImplemented

    @classmethod
    @abc.abstractmethod
    def start(cls):
        """Start the streaming service."""

    @classmethod
    @abc.abstractmethod
    def update(cls):
        """Update the previous frame by the newest one read."""

    @classmethod
    @abc.abstractmethod
    def read(cls):
        """Return the frame most recently read."""

    @classmethod
    @abc.abstractmethod
    def stop(cls):
        """Stop the streaming service."""

    @classmethod
    @abc.abstractmethod
    def isOpened(cls):
        """Check if the video stream is open."""
