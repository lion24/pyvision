"""Module for image processing strategies."""

from abc import ABC, abstractmethod

from cv2 import UMat


class ImageProcessingStrategy(ABC):
    """Abstract base class for image processing strategies."""

    @abstractmethod
    def process(self, frame: UMat) -> UMat:
        """Process an image.

        Args:
            frame (UMat): The image to process.

        Returns:
            UMat: The processed image.
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
    def process(self, frame: UMat) -> UMat:
        """Process an image.

        Args:
            frame (UMat): The image to process.

        Returns:
            UMat: The processed image.
        """
        return self._wrapped.process(frame)
