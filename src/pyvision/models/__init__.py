"""Module for image processing strategies."""

from abc import ABC, abstractmethod

import numpy as np
from cv2 import UMat
from cv2.typing import MatLike
from numpy.typing import NDArray

Image = MatLike | NDArray[np.uint8] | NDArray[np.float32]


class ImageProcessingStrategy(ABC):
    """Abstract base class for image processing strategies."""

    @abstractmethod
    def process(self, _frame: Image) -> UMat:
        """Process an image.

        Args:
            frame (Image): The image to process.

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
    def process(self, _frame: Image) -> UMat:
        """Process an image.

        Args:
            frame (Image): The image to process.

        Returns:
            UMat: The processed image.
        """
        return self._wrapped.process(_frame)
