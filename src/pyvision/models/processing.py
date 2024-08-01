"""A module that contains classes for processing images."""

from typing import Callable, List

import cv2


class ImageProcessor:
    """A class that applies filters to images."""

    def __init__(self):
        """Initialize the ImageProcessor object."""
        self.filters: List[Callable[[cv2.UMat], cv2.UMat]] = []

    def add_filter(self, filter_func: Callable[[cv2.UMat], cv2.UMat]) -> None:
        """Add a filter function to the list of filters.

        Args:
            filter_func: A callable that takes a cv2.UMat image as input and returns a filtered cv2.UMat image.
        """
        self.filters.append(filter_func)

    def process(self, frame: cv2.UMat) -> cv2.UMat:
        """Apply all the filters to the input frame.

        Args:
            frame: The input frame to be processed.

        Returns:
            The processed frame after applying all the filters.
        """
        for filter_func in self.filters:
            frame = filter_func(frame)
        return frame
