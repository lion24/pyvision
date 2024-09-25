"""Module containing the OpenCVVideoStream class."""

import threading
from enum import Enum
from typing import Tuple, TypedDict, Union

import cv2
from cv2 import VideoCapture
from typing_extensions import Unpack


class StreamSettings(TypedDict):
    """TypedDict representing the settings for an OpenCV camera."""

    path: Union[int, str]
    width: int
    height: int
    desired_fps: int


class ReadError(Enum):
    """Enum representing the read error states."""

    NO_ERROR = 0
    NO_FRAME = 1
    NO_STREAM = 2
    UNKNOWN_ERROR = 3


class OpenCVVideoStream(threading.Thread):
    """Class representing an OpenCV video stream."""

    def __init__(self, **kwargs: Unpack[StreamSettings]) -> None:
        """Initialize the OpenCVVideoStream object.

        Args:
            **kwargs: Additional camera settings.

        """
        super().__init__()

        path = kwargs.get("path", 0)
        self.width = kwargs.get("width", 960)
        self.height = kwargs.get("height", 540)
        self.desired_fps = kwargs.get("desired_fps", 24)
        self.running = False
        self.frame = cv2.UMat(
            self.height, self.width, cv2.CV_8UC3, cv2.USAGE_ALLOCATE_DEVICE_MEMORY
        )
        self.update_stream_path(path)
        self.read_lock = threading.Lock()

    def update_stream_path(self, path: Union[int, str]) -> cv2.VideoCapture:
        """Update the stream path and configure the video capture object.

        Args:
            path (Union[int, str]): The path to the video file or the index of the camera.

        Returns:
            cv2.VideoCapture: The updated video capture object.

        """
        self.path = path

        self.stream: VideoCapture = cv2.VideoCapture(self.path, cv2.CAP_MSMF)
        self.stream.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
        self.stream.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
        max_supported_fps = self.stream.get(cv2.CAP_PROP_FPS)
        print(f"Max supported FPS: {max_supported_fps}")
        if self.desired_fps > max_supported_fps:
            print(
                f"You request more FPS that the backend actually support. falling back to {max_supported_fps}"
            )
        self.fps = min(self.desired_fps, int(max_supported_fps))
        self.stream.set(cv2.CAP_PROP_FPS, self.fps)

        return self.stream

    def read_frame(self) -> Tuple[ReadError, cv2.UMat]:
        """Read a frame from the video stream.

        Returns:
            A tuple containing a boolean indicating if the frame was successfully read and the frame itself.

        """
        with self.read_lock:
            if not self.frame:
                return ReadError.NO_FRAME, self.frame
            return ReadError.NO_ERROR, self.frame

    def run(self) -> None:
        """Start the video stream."""
        self.running = True
        while self.running:
            grabbed = self.stream.grab()
            if grabbed:
                with self.read_lock:
                    self.stream.retrieve(self.frame)

    def stop(self) -> None:
        """Stop the video stream."""
        self.running = False
        self.join()

    def release(self) -> None:
        """Release the video stream."""
        print("releasing the stream")
        self.stop()
        if self.stream:
            self.stream.release()
