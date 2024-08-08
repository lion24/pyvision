"""A module that contains the VideoModel class."""

from typing import Callable, List

import cv2
from typing_extensions import Unpack

from pyvision.models.opencv_stream import OpenCVCameraSettings, OpenCVVideoStream
from pyvision.utils.observer import ConcreteSubject


class VideoModel(ConcreteSubject):
    """A class that applies filters to images."""

    def __init__(self, **camera_settings: Unpack[OpenCVCameraSettings]) -> None:
        """Initialize the VideoModel object."""
        ConcreteSubject.__init__(self)
        self.filters: List[Callable[[cv2.UMat], cv2.UMat]] = []
        self.stream = OpenCVVideoStream(**camera_settings)
        self.width = self.stream.width
        self.height = self.stream.height
        self.fps = self.stream.fps
        self.frame = cv2.UMat(self.height, self.width, cv2.CV_8UC3)

    def add_filter(self, filter_func: Callable[[cv2.UMat], cv2.UMat]) -> None:
        """Add a filter function to the list of filters.

        Args:
            filter_func: A callable that takes a cv2.UMat image as input and returns a filtered cv2.UMat image.
        """
        self.filters.append(filter_func)

    def process(self, frame: cv2.UMat):
        """Apply all the filters to the input frame.

        Args:
            frame: The input frame to be processed.

        Returns:
            The processed frame after applying all the filters.
        """
        for filter_func in self.filters:
            self.frame = filter_func(frame)

        self.notify()

    def release(self) -> None:
        """Release the video stream."""
        self.stream.release()

    def update_frame(self, frame: cv2.UMat) -> None:
        """Updates the current frame.

        Args:
            frame (cv2.UMat): The new frame to be set as the current frame.
        """
        ret, frame = self.stream.read_frame()
        if ret:
            self.frame = frame
