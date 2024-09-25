"""This module contains classes for image processing filters."""

import cv2
import numpy as np
from cv2 import UMat

from pyvision.models import Image, ImageProcessingDecorator, ImageProcessingStrategy


class NoOpFilter(ImageProcessingStrategy):
    """A class representing a no-op filter for image processing."""

    def process(self, frame: Image) -> UMat:
        """Process an image.

        Args:
            frame (UMat): The image to process.

        Returns:
            UMat: The processed image.
        """
        return cv2.UMat(frame)  # type: ignore


class IdentityFilter(ImageProcessingDecorator):
    """A class representing an identity filter for image processing."""

    def __init__(self, wrapped: ImageProcessingStrategy) -> None:
        """Initialize the IdentityFilter.

        Args:
            wrapped (ImageProcessingStrategy): The wrapped image processing strategy.
        """
        super().__init__(wrapped)

    def process(self, _frame: Image) -> UMat:
        """Process an image.

        Args:
            frame (UMat): The image to process.

        Returns:
            UMat: The processed image.
        """
        frame = super().process(_frame)
        array = np.array([[0, 0, 0], [0, 1, 0], [0, 0, 0]], dtype="uint8")
        input_kernel = cv2.UMat(array)  # type: ignore
        return cv2.filter2D(frame, -1, input_kernel)


class EdgeDetectionKernelFilter(ImageProcessingDecorator):
    """A class representing an edge detection filter for image processing."""

    def __init__(self, wrapped: ImageProcessingStrategy, ksize: int = 3) -> None:
        """Initialize the EdgeDetectionFilter.

        Args:
            wrapped (ImageProcessingStrategy): The wrapped image processing strategy.
            ksize (int): The kernel size for the Sobel operator.
        """
        self.ksize = ksize
        wrapped = GrayscaleFilter(wrapped)
        wrapped = GaussianKernelFilter(wrapped)
        super().__init__(wrapped)

    def process(self, _frame: Image) -> UMat:
        """Process an image.

        Args:
            frame (UMat): The image to process.

        Returns:
            UMat: The processed image.
        """
        frame = super().process(_frame)

        # Compute X and Y gradients using Sobel operator
        sobel_x = cv2.Sobel(frame, cv2.CV_64F, 1, 0, None, ksize=self.ksize)
        sobel_y = cv2.Sobel(frame, cv2.CV_64F, 0, 1, None, ksize=self.ksize)

        # Compute the gradient magnitude
        magnitude = cv2.magnitude(
            sobel_x, sobel_y
        )  # equals to np.sqrt(sobel_x**2 + sobel_y**2)

        _, thres = cv2.threshold(magnitude, 64, 255, cv2.THRESH_TOZERO)

        return cv2.normalize(thres, frame, 0, 255, cv2.NORM_MINMAX, dtype=cv2.CV_8UC3)


class SharpenFilter(ImageProcessingDecorator):
    """A class representing a sharpen filter for image processing."""

    def __init__(self, wrapped: ImageProcessingStrategy) -> None:
        """Initialize the SharpenFilter.

        Args:
            wrapped (ImageProcessingStrategy): The wrapped image processing strategy.
        """
        super().__init__(wrapped)

    def process(self, _frame: Image) -> UMat:
        """Process an image.

        Args:
            frame (UMat): The image to process.

        Returns:
            UMat: The processed image.
        """
        frame = super().process(_frame)
        array = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]], dtype="uint8")
        input_kernel = cv2.UMat(array)  # type: ignore
        return cv2.filter2D(frame, -1, input_kernel)


class UnsharpMasking5By5KernelFilter(ImageProcessingDecorator):
    """A class representing an unsharp masking filter for image processing."""

    def __init__(self, wrapped: ImageProcessingStrategy) -> None:
        """Initialize the UnsharpMasking5By5KernelFilter.

        Args:
            wrapped (ImageProcessingStrategy): The wrapped image processing strategy.
        """
        super().__init__(wrapped)

    def process(self, _frame: Image) -> UMat:
        """Process an image.

        Args:
            frame (UMat): The image to process.

        Returns:
            UMat: The processed image.
        """
        frame = super().process(_frame)
        array = -(1 / 256.0) * np.array(
            [
                [1, 4, 6, 4, 1],
                [4, 16, 24, 16, 4],
                [6, 24, -476, 24, 6],
                [4, 16, 24, 16, 4],
                [1, 4, 6, 4, 1],
            ],
            dtype="uint8",
        )
        input_kernel = cv2.UMat(array)  # type: ignore
        return cv2.filter2D(frame, -1, input_kernel)


class GaussianBlurKernelFilter(ImageProcessingDecorator):
    """A class representing a Gaussian blur filter for image processing."""

    def __init__(self, wrapped: ImageProcessingStrategy) -> None:
        """Initialize the GaussianBlurKernelFilter.

        Args:
            wrapped (ImageProcessingStrategy): The wrapped image processing strategy.
        """
        super().__init__(wrapped)

    def process(self, _frame: Image) -> UMat:
        """Process an image.

        Args:
            frame (UMat): The image to process.

        Returns:
            UMat: The processed image.
        """
        frame = super().process(_frame)
        array = (1 / 16.0) * np.array([[1, 2, 1], [2, 4, 2], [1, 2, 1]], dtype="uint8")
        input_kernel = cv2.UMat(array)  # type: ignore
        return cv2.filter2D(frame, -1, input_kernel)


class GaussianKernelFilter(ImageProcessingDecorator):
    """A class representing a Gaussian kernel filter for image processing."""

    def __init__(self, wrapped: ImageProcessingStrategy) -> None:
        """Initialize the GaussianKernelFilter.

        Args:
            wrapped (ImageProcessingStrategy): The wrapped image processing strategy.
        """
        super().__init__(wrapped)

    def process(self, _frame: Image) -> UMat:
        """Process an image.

        Args:
            frame (UMat): The image to process.

        Returns:
            UMat: The processed image.
        """
        frame = super().process(_frame)
        array = (1 / 159.0) * np.array(
            [
                [2, 4, 5, 4, 2],
                [4, 9, 12, 9, 4],
                [5, 12, 15, 12, 5],
                [4, 9, 12, 9, 4],
                [2, 4, 5, 4, 2],
            ],
            dtype="uint8",
        )
        input_kernel = cv2.UMat(array)  # type: ignore
        return cv2.filter2D(frame, -1, input_kernel)


class GaussianSmoothingFilter(ImageProcessingDecorator):
    """A class representing a Gaussian smoothing filter for image processing."""

    def __init__(self, wrapped: ImageProcessingStrategy) -> None:
        """Initialize the GaussianSmoothingFilter.

        Args:
            wrapped (ImageProcessingStrategy): The wrapped image processing strategy.
        """
        super().__init__(wrapped)

    def process(self, _frame: Image) -> UMat:
        """Process an image.

        Args:
            frame (UMat): The image to process.

        Returns:
            UMat: The processed image.
        """
        frame = super().process(_frame)
        array = (1 / 273) * np.array(
            [
                [1, 4, 7, 4, 1],
                [4, 16, 26, 16, 4],
                [7, 26, 41, 26, 7],
                [4, 16, 26, 16, 4],
                [1, 4, 7, 4, 1],
            ],
            dtype="uint8",
        )
        input_kernel = cv2.UMat(array)  # type: ignore
        return cv2.filter2D(frame, -1, input_kernel)


class LeftSobelKernelFilter(ImageProcessingDecorator):
    """A class representing a left Sobel kernel filter for image processing."""

    def __init__(self, wrapped: ImageProcessingStrategy) -> None:
        """Initialize the LeftSobelKernelFilter.

        Args:
            wrapped (ImageProcessingStrategy): The wrapped image processing strategy.
        """
        super().__init__(wrapped)

    def process(self, _frame: Image) -> UMat:
        """Process an image.

        Args:
            frame (UMat): The image to process.

        Returns:
            UMat: The processed image.
        """
        frame = super().process(_frame)
        array = np.array([[1, 0, -1], [2, 0, -2], [1, 0, -1]], dtype="uint8")
        input_kernel = cv2.UMat(array)  # type: ignore
        return cv2.filter2D(frame, -1, input_kernel)


class TopSobelKernelFilter(ImageProcessingDecorator):
    """A class representing a top Sobel kernel filter for image processing."""

    def __init__(self, wrapped: ImageProcessingStrategy) -> None:
        """Initialize the TopSobelKernelFilter.

        Args:
            wrapped (ImageProcessingStrategy): The wrapped image processing strategy.
        """
        super().__init__(wrapped)

    def process(self, _frame: Image) -> UMat:
        """Process an image.

        Args:
            frame (UMat): The image to process.

        Returns:
            UMat: The processed image.
        """
        frame = super().process(_frame)
        array = np.array([[1, 2, 1], [0, 0, 0], [-1, -2, -1]], dtype="uint8")
        input_kernel = cv2.UMat(array)  # type: ignore
        return cv2.filter2D(frame, -1, input_kernel)


class VerticalSobelKernelFilter(ImageProcessingDecorator):
    """A class representing a right Sobel kernel filter for image processing."""

    def __init__(self, wrapped: ImageProcessingStrategy) -> None:
        """Initialize the VerticalSobelKernelFilter.

        Args:
            wrapped (ImageProcessingStrategy): The wrapped image processing strategy.
        """
        super().__init__(wrapped)

    def process(self, _frame: Image) -> UMat:
        """Process an image.

        Args:
            frame (UMat): The image to process.

        Returns:
            UMat: The processed image.
        """
        frame = super().process(_frame)
        array = np.array([[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]], dtype="uint8")
        input_kernel = cv2.UMat(array)  # type: ignore
        return cv2.filter2D(frame, -1, input_kernel)


class HorizontalSobelKernelFilter(ImageProcessingDecorator):
    """A class representing a bottom Sobel kernel filter for image processing."""

    def __init__(self, wrapped: ImageProcessingStrategy) -> None:
        """Initialize the HorizontalSobelKernelFilter.

        Args:
            wrapped (ImageProcessingStrategy): The wrapped image processing strategy.
        """
        super().__init__(wrapped)

    def process(self, _frame: Image) -> UMat:
        """Process an image.

        Args:
            frame (UMat): The image to process.

        Returns:
            UMat: The processed image.
        """
        frame = super().process(_frame)
        array = np.array([[-1, -2, -1], [0, 0, 0], [1, 2, 1]])
        input_kernel = cv2.UMat(array)  # type: ignore
        return cv2.filter2D(frame, -1, input_kernel)


class LapaclacianKernelFilter(ImageProcessingDecorator):
    """A class representing a Laplacian custom filter for image processing."""

    def __init__(self, wrapped: ImageProcessingStrategy) -> None:
        """Initialize the LapaclacianKernelFilter.

        Args:
            wrapped (ImageProcessingStrategy): The wrapped image processing strategy.
        """
        super().__init__(wrapped)

    def process(self, _frame: Image) -> UMat:
        """Process an image.

        Args:
            frame (UMat): The image to process.

        Returns:
            UMat: The processed image.
        """
        frame = super().process(_frame)
        array = np.array([[0, 1, 0], [1, -4, 1], [0, 1, 0]])
        input_kernel = cv2.UMat(array)  # type: ignore
        return cv2.filter2D(frame, -1, input_kernel)


class LOGKernelFilter(ImageProcessingDecorator):
    """A class representing a Laplacian of Gaussian filter for image processing."""

    def __init__(self, wrapped: ImageProcessingStrategy) -> None:
        """Initialize the LOGKernelFilter.

        Args:
            wrapped (ImageProcessingStrategy): The wrapped image processing strategy.
        """
        super().__init__(wrapped)

    def process(self, _frame: Image) -> UMat:
        """Process an image.

        Args:
            frame (UMat): The image to process.

        Returns:
            UMat: The processed image.
        """
        frame = super().process(_frame)
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

    def process(self, _frame: Image) -> UMat:
        """Process an image.

        Args:
            frame (UMat): The image to process.

        Returns:
            UMat: The processed image.
        """
        frame = super().process(_frame)
        return cv2.Canny(frame, 100, 200)


class GrayscaleFilter(ImageProcessingDecorator):
    """A class representing a Grey Code filter for image processing."""

    def __init__(self, wrapped: ImageProcessingStrategy) -> None:
        """Initialize the GreyCodeKernelFilter.

        Args:
            wrapped (ImageProcessingStrategy): The wrapped image processing strategy.
        """
        super().__init__(wrapped)

    def process(self, frame: Image) -> UMat:
        """Process an image.

        Args:
            frame (UMat): The image to process.

        Returns:
            UMat: The processed image.
        """
        return cv2.cvtColor(super().process(frame), cv2.COLOR_BGR2GRAY)


class ContoursDetectionFilter(ImageProcessingDecorator):
    """A class representing an object detection filter for image processing."""

    def __init__(self, wrapped: ImageProcessingStrategy) -> None:
        """Initialize the GreyCodeKernelFilter.

        Args:
            wrapped (ImageProcessingStrategy): The wrapped image processing strategy.
        """
        super().__init__(wrapped)

    def process(self, _frame: Image) -> UMat:
        """Apply contour detection to the image.

        Args:
            frame (UMat): The image to process.

        Returns:
            UMat: The processed image.
        """
        frame = super().process(_frame)
        contours, _ = cv2.findContours(
            frame, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )
        output = cv2.cvtColor(frame, cv2.COLOR_GRAY2BGR)
        for countour in contours:
            if cv2.contourArea(countour) > 100:  # Filter out small contours
                x, y, w, h = cv2.boundingRect(countour)
                cv2.rectangle(output, (x, y), (w + x, h + y), (0, 255, 0), 1)
        return output


class HaarCascadeFaceDetectionFilter(ImageProcessingDecorator):
    """A class representing a Haar cascade face detection filter for image processing."""

    def __init__(self, wrapped: ImageProcessingStrategy) -> None:
        """Initialize the HaarCascadeFaceDetectionFilter.

        Args:
            wrapped (ImageProcessingStrategy): The wrapped image processing strategy.
        """
        super().__init__(wrapped)
        self.face_cascade = cv2.CascadeClassifier(
            "data/lbpcascade_frontalface.xml"  # type: ignore
        )

    def process(self, _frame: Image) -> UMat:
        """Process an image.

        Args:
            frame (UMat): The image to process.

        Returns:
            UMat: The processed image.
        """
        frame = super().process(_frame)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)
        for x, y, w, h in faces:
            cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
        return frame


class YUNetFaceDetectionFilter(ImageProcessingDecorator):
    """A class representing a YUnet DNN face detection filter for image processing."""

    def __init__(self, wrapped: ImageProcessingStrategy) -> None:
        """Initialize the YUNetFaceDetectionFilter.

        Args:
            wrapped (ImageProcessingStrategy): The wrapped image processing strategy.
        """
        super().__init__(wrapped)
        self.detector = cv2.FaceDetectorYN.create(
            "data/face_detection_yunet_2023mar.onnx",
            "",
            (0, 0),
            backend_id=cv2.dnn.DNN_BACKEND_DEFAULT,
            target_id=cv2.dnn.DNN_TARGET_OPENCL,
        )

    def process(self, _frame: Image) -> UMat:
        """Process an image.

        Args:
            frame (UMat): The image to process.

        Returns:
            UMat: The processed image.
        """
        # face_detection_yunet_2023mar.onnx
        frame = super().process(_frame)
        frame_mat = frame.get()
        heigh, width, _ = frame_mat.shape
        self.detector.setInputSize((width, heigh))

        _, faces = self.detector.detect(frame)

        if faces is None:  # type: ignore
            return frame

        try:
            for face in faces.get():
                # bounding box
                box = list(map(int, face[:4]))
                color = (0, 255, 0)
                cv2.rectangle(frame, box, color, 2)

                # confidence
                confidence = face[-1]
                confidence = "{:.2f}".format(confidence)
                position = (box[0], box[1] - 10)
                cv2.putText(
                    frame,
                    confidence,
                    position,
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    color,
                    1,
                    cv2.LINE_AA,
                )
        except TypeError:
            pass

        return frame
