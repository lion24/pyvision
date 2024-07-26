"""This module contains classes for image processing filters."""

import cv2
import numpy as np
from cv2 import UMat

from pyvision.models import ImageProcessingDecorator, ImageProcessingStrategy


class NoOpFilter(ImageProcessingStrategy):
    """A class representing a no-op filter for image processing."""

    def process(self, frame: UMat) -> UMat:
        """Process an image.

        Args:
            frame (UMat): The image to process.

        Returns:
            UMat: The processed image.
        """
        return frame


class IdentityFilter(ImageProcessingDecorator):
    """A class representing an identity filter for image processing."""

    def __init__(self, wrapped: ImageProcessingStrategy) -> None:
        """Initialize the IdentityFilter.

        Args:
            wrapped (ImageProcessingStrategy): The wrapped image processing strategy.
        """
        super().__init__(wrapped)

    def process(self, frame: UMat) -> UMat:
        """Process an image.

        Args:
            frame (UMat): The image to process.

        Returns:
            UMat: The processed image.
        """
        frame = super().process(frame)
        kernel = np.array([[0, 0, 0], [0, 1, 0], [0, 0, 0]])
        return cv2.filter2D(frame, -1, cv2.UMat(kernel))  # type: ignore


class EdgeDetectionKernelFilter(ImageProcessingDecorator):
    """A class representing an edge detection filter for image processing."""

    def __init__(self, wrapped: ImageProcessingStrategy, ksize: int = 3) -> None:
        """Initialize the EdgeDetectionFilter.

        Args:
            wrapped (ImageProcessingStrategy): The wrapped image processing strategy.
            ksize (int): The kernel size for the Sobel operator.
        """
        self.ksize = ksize
        wrapped = GaussianBlurKernelFilter(wrapped)
        wrapped = GrayscaleFilter(wrapped)
        super().__init__(wrapped)

    def process(self, frame: UMat) -> UMat:
        """Process an image.

        Args:
            frame (UMat): The image to process.

        Returns:
            UMat: The processed image.
        """
        frame = super().process(frame)

        # Compute X and Y gradients using Sobel operator
        sobel_x = cv2.Sobel(frame, cv2.CV_64F, 1, 0, None, ksize=self.ksize)
        sobel_y = cv2.Sobel(frame, cv2.CV_64F, 0, 1, None, ksize=self.ksize)

        # Compute the gradient magnitude
        magnitude = cv2.magnitude(
            sobel_x, sobel_y
        )  # equals to np.sqrt(sobel_x**2 + sobel_y**2)

        return cv2.normalize(
            magnitude, frame, 0, 255, cv2.NORM_MINMAX, dtype=cv2.CV_8UC3
        )


class SharpenFilter(ImageProcessingDecorator):
    """A class representing a sharpen filter for image processing."""

    def __init__(self, wrapped: ImageProcessingStrategy) -> None:
        """Initialize the SharpenFilter.

        Args:
            wrapped (ImageProcessingStrategy): The wrapped image processing strategy.
        """
        super().__init__(wrapped)

    def process(self, frame: UMat) -> UMat:
        """Process an image.

        Args:
            frame (UMat): The image to process.

        Returns:
            UMat: The processed image.
        """
        frame = super().process(frame)
        kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]])
        return cv2.filter2D(frame, -1, cv2.UMat(kernel))  # type: ignore


class UnsharpMasking5By5KernelFilter(ImageProcessingDecorator):
    """A class representing an unsharp masking filter for image processing."""

    def __init__(self, wrapped: ImageProcessingStrategy) -> None:
        """Initialize the UnsharpMasking5By5KernelFilter.

        Args:
            wrapped (ImageProcessingStrategy): The wrapped image processing strategy.
        """
        super().__init__(wrapped)

    def process(self, frame: UMat) -> UMat:
        """Process an image.

        Args:
            frame (UMat): The image to process.

        Returns:
            UMat: The processed image.
        """
        frame = super().process(frame)
        kernel = -(1 / 256.0) * np.array(
            [
                [1, 4, 6, 4, 1],
                [4, 16, 24, 16, 4],
                [6, 24, -476, 24, 6],
                [4, 16, 24, 16, 4],
                [1, 4, 6, 4, 1],
            ]
        )
        return cv2.filter2D(frame, -1, cv2.UMat(kernel))  # type: ignore


class GaussianBlurKernelFilter(ImageProcessingDecorator):
    """A class representing a Gaussian blur filter for image processing."""

    def __init__(self, wrapped: ImageProcessingStrategy) -> None:
        """Initialize the GaussianBlurKernelFilter.

        Args:
            wrapped (ImageProcessingStrategy): The wrapped image processing strategy.
        """
        super().__init__(wrapped)

    def process(self, frame: UMat) -> UMat:
        """Process an image.

        Args:
            frame (UMat): The image to process.

        Returns:
            UMat: The processed image.
        """
        frame = super().process(frame)
        kernel = (1 / 16.0) * np.array([[1, 2, 1], [2, 4, 2], [1, 2, 1]])
        return cv2.filter2D(frame, -1, cv2.UMat(kernel))  # type: ignore


class GaussianKernelFilter(ImageProcessingDecorator):
    """A class representing a Gaussian kernel filter for image processing."""

    def __init__(self, wrapped: ImageProcessingStrategy) -> None:
        """Initialize the GaussianKernelFilter.

        Args:
            wrapped (ImageProcessingStrategy): The wrapped image processing strategy.
        """
        super().__init__(wrapped)

    def process(self, frame: UMat) -> UMat:
        """Process an image.

        Args:
            frame (UMat): The image to process.

        Returns:
            UMat: The processed image.
        """
        frame = super().process(frame)
        kernel = (1 / 159.0) * np.array(
            [
                [2, 4, 5, 4, 2],
                [4, 9, 12, 9, 4],
                [5, 12, 15, 12, 5],
                [4, 9, 12, 9, 4],
                [2, 4, 5, 4, 2],
            ]
        )
        return cv2.filter2D(frame, -1, cv2.UMat(kernel))  # type: ignore


class GaussianSmoothingFilter(ImageProcessingDecorator):
    """A class representing a Gaussian smoothing filter for image processing."""

    def __init__(self, wrapped: ImageProcessingStrategy) -> None:
        """Initialize the GaussianSmoothingFilter.

        Args:
            wrapped (ImageProcessingStrategy): The wrapped image processing strategy.
        """
        super().__init__(wrapped)

    def process(self, frame: UMat) -> UMat:
        """Process an image.

        Args:
            frame (UMat): The image to process.

        Returns:
            UMat: The processed image.
        """
        frame = super().process(frame)
        kernel = (1 / 273) * np.array(
            [
                [1, 4, 7, 4, 1],
                [4, 16, 26, 16, 4],
                [7, 26, 41, 26, 7],
                [4, 16, 26, 16, 4],
                [1, 4, 7, 4, 1],
            ]
        )
        return cv2.filter2D(frame, -1, cv2.UMat(kernel))  # type: ignore


class LeftSobelKernelFilter(ImageProcessingDecorator):
    """A class representing a left Sobel kernel filter for image processing."""

    def __init__(self, wrapped: ImageProcessingStrategy) -> None:
        """Initialize the LeftSobelKernelFilter.

        Args:
            wrapped (ImageProcessingStrategy): The wrapped image processing strategy.
        """
        super().__init__(wrapped)

    def process(self, frame: UMat) -> UMat:
        """Process an image.

        Args:
            frame (UMat): The image to process.

        Returns:
            UMat: The processed image.
        """
        frame = super().process(frame)
        kernel = np.array([[1, 0, -1], [2, 0, -2], [1, 0, -1]])
        return cv2.filter2D(frame, -1, cv2.UMat(kernel))  # type: ignore


class TopSobelKernelFilter(ImageProcessingDecorator):
    """A class representing a top Sobel kernel filter for image processing."""

    def __init__(self, wrapped: ImageProcessingStrategy) -> None:
        """Initialize the TopSobelKernelFilter.

        Args:
            wrapped (ImageProcessingStrategy): The wrapped image processing strategy.
        """
        super().__init__(wrapped)

    def process(self, frame: UMat) -> UMat:
        """Process an image.

        Args:
            frame (UMat): The image to process.

        Returns:
            UMat: The processed image.
        """
        frame = super().process(frame)
        kernel = np.array([[1, 2, 1], [0, 0, 0], [-1, -2, -1]])
        return cv2.filter2D(frame, -1, cv2.UMat(kernel))  # type: ignore


class VerticalSobelKernelFilter(ImageProcessingDecorator):
    """A class representing a right Sobel kernel filter for image processing."""

    def __init__(self, wrapped: ImageProcessingStrategy) -> None:
        """Initialize the VerticalSobelKernelFilter.

        Args:
            wrapped (ImageProcessingStrategy): The wrapped image processing strategy.
        """
        super().__init__(wrapped)

    def process(self, frame: UMat) -> UMat:
        """Process an image.

        Args:
            frame (UMat): The image to process.

        Returns:
            UMat: The processed image.
        """
        frame = super().process(frame)
        kernel = np.array([[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]])
        return cv2.filter2D(frame, -1, cv2.UMat(kernel))  # type: ignore


class HorizontalSobelKernelFilter(ImageProcessingDecorator):
    """A class representing a bottom Sobel kernel filter for image processing."""

    def __init__(self, wrapped: ImageProcessingStrategy) -> None:
        """Initialize the HorizontalSobelKernelFilter.

        Args:
            wrapped (ImageProcessingStrategy): The wrapped image processing strategy.
        """
        super().__init__(wrapped)

    def process(self, frame: UMat) -> UMat:
        """Process an image.

        Args:
            frame (UMat): The image to process.

        Returns:
            UMat: The processed image.
        """
        frame = super().process(frame)
        kernel = np.array([[-1, -2, -1], [0, 0, 0], [1, 2, 1]])
        return cv2.filter2D(frame, -1, cv2.UMat(kernel))  # type: ignore


class LapaclacianKernelFilter(ImageProcessingDecorator):
    """A class representing a Laplacian custom filter for image processing."""

    def __init__(self, wrapped: ImageProcessingStrategy) -> None:
        """Initialize the LapaclacianKernelFilter.

        Args:
            wrapped (ImageProcessingStrategy): The wrapped image processing strategy.
        """
        super().__init__(wrapped)

    def process(self, frame: UMat) -> UMat:
        """Process an image.

        Args:
            frame (UMat): The image to process.

        Returns:
            UMat: The processed image.
        """
        frame = super().process(frame)
        kernel = np.array([[0, 1, 0], [1, -4, 1], [0, 1, 0]])
        return cv2.filter2D(frame, -1, cv2.UMat(kernel))  # type: ignore


class LOGKernelFilter(ImageProcessingDecorator):
    """A class representing a Laplacian of Gaussian filter for image processing."""

    def __init__(self, wrapped: ImageProcessingStrategy) -> None:
        """Initialize the LOGKernelFilter.

        Args:
            wrapped (ImageProcessingStrategy): The wrapped image processing strategy.
        """
        super().__init__(wrapped)

    def process(self, frame: UMat) -> UMat:
        """Process an image.

        Args:
            frame (UMat): The image to process.

        Returns:
            UMat: The processed image.
        """
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        return cv2.Laplacian(cv2.GaussianBlur(gray, (3, 3), 0), -1)


class CannyFilter(ImageProcessingDecorator):
    """A class representing an edge detection filter for image processing."""

    def __init__(self, wrapped: ImageProcessingStrategy) -> None:
        """Initialize the CannyFilter.

        Args:
            wrapped (ImageProcessingStrategy): The wrapped image processing strategy.
        """
        super().__init__(wrapped)

    def process(self, frame: UMat) -> UMat:
        """Process an image.

        Args:
            frame (UMat): The image to process.

        Returns:
            UMat: The processed image.
        """
        frame = super().process(frame)
        return cv2.Canny(frame, 100, 200)


class GrayscaleFilter(ImageProcessingDecorator):
    """A class representing a Grey Code filter for image processing."""

    def __init__(self, wrapped: ImageProcessingStrategy) -> None:
        """Initialize the GreyCodeKernelFilter.

        Args:
            wrapped (ImageProcessingStrategy): The wrapped image processing strategy.
        """
        super().__init__(wrapped)

    def process(self, frame: UMat) -> UMat:
        """Process an image.

        Args:
            frame (UMat): The image to process.

        Returns:
            UMat: The processed image.
        """
        return cv2.cvtColor(super().process(frame), cv2.COLOR_BGR2GRAY)
