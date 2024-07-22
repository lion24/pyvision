"""Module containing the OpenCVVideoStream class."""

import threading

import cv2
from cv2 import VideoCapture

from pyvision.camera import VideoStreamProvider
from pyvision.camera.fps import FPS


@VideoStreamProvider.register
class OpenCVVideoStream:
    """Class representing a video stream using OpenCV."""

    def __init__(
        self, idx: int = 0, width: int = 960, height: int = 540, desired_fps: int = 24
    ) -> None:
        """Initialize the OpenCVVideoStream object.

        Args:
            idx (int): Index of the video capture device.
            width (int): Width of the video frame.
            height (int): Height of the video frame.
            desired_fps (int): Desired frames per second.

        """
        self.idx = idx
        self.width = width
        self.height = height
        self.stop_event: threading.Event = threading.Event()
        self.update_thread: threading.Thread = threading.Thread(target=self.update)
        self.stream: None | VideoCapture = cv2.VideoCapture(idx, cv2.CAP_MSMF)
        self.stream.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        self.stream.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
        print("aperture: ", cv2.CAP_PROP_EXPOSURE)
        # self.stream.set(cv2.CAP_PROP_EXPOSURE, -6)
        print("aperture: ", cv2.CAP_PROP_EXPOSURE)

        max_supported_fps = self.stream.get(cv2.CAP_PROP_FPS)
        if desired_fps > max_supported_fps:
            print(
                f"You request more FPS that the backend actually support. falling back to {max_supported_fps}"
            )
        self.desired_fps = min(desired_fps, int(max_supported_fps))

        # Read and store the first frame
        (success, self.frame) = self.stream.read()
        if not success:
            print("init failed to read from stream")

    def update(self):
        """Update the video stream frames.

        This method continuously reads frames from the video stream and updates the frame attribute.

        """
        fps = FPS(self.desired_fps)

        while not self.stop_event.is_set():
            if self.stream is not None and self.stream.isOpened():
                ret, frame = self.stream.read()
                if not ret:
                    print("failed to read one frame")

                fps.update(True)
                cv2.putText(
                    frame,
                    "{:.0f} frame/s".format(fps.get_fps()),
                    (self.width - 180, self.height - 40),
                    cv2.FONT_HERSHEY_TRIPLEX,
                    1.0,
                    (0, 255, 0),
                    1,
                )
                self.frame = frame

    def start(self):
        """Start the video stream.

        Returns:
            OpenCVVideoStream: The current instance of the OpenCVVideoStream object.

        """
        if self.stop_event.is_set():
            self.stop_event.clear()

        self.update_thread.start()
        return self

    def read(self):
        """Read the current frame from the video stream.

        Returns:
            numpy.ndarray: The current frame of the video stream.

        """
        return self.frame

    def stop(self):
        """Stop the video stream."""
        if self.update_thread and self.update_thread.is_alive():
            self.stop_event.set()
            print("waiting update_thread to join")
            self.update_thread.join()
            print("update_thread joined!")

        if self.stream:
            self.stream.release()
            self.stream = None

    def isOpened(self) -> bool:
        """Check if the video stream is opened.

        Returns:
            bool: True if the video stream is opened, False otherwise.

        """
        return self.stream.isOpened() if self.stream else False
