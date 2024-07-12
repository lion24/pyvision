"""Module for image processing strategies."""

from abc import ABC, abstractmethod

from cv2.typing import MatLike


class ImageProcessingStrategy(ABC):
    """Abstract base class for image processing strategies."""

    @abstractmethod
    def process(self, frame: MatLike) -> MatLike:
        """Process an image.

        Args:
            frame (MatLike): The image to process.

        Returns:
            MatLike: The processed image.
        """
        pass


class ImageProcessingDecorator(ImageProcessingStrategy):
    """Abstract base class for image processing decorators."""

    def __init__(self, wrapped: ImageProcessingStrategy) -> None:
        """Initialize the ImageProcessingDecorator.

        Args:
            wrapped (ImageProcessingStrategy): The wrapped image processing strategy.
        """
        self._wrapped = wrapped

    @abstractmethod
    def process(self, frame: MatLike) -> MatLike:
        """Process an image.

        Args:
            frame (MatLike): The image to process.

        Returns:
            MatLike: The processed image.
        """
        frame = self._wrapped.process(frame)
        return frame
