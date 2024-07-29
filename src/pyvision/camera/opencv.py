"""Module containing the OpenCVVideoStream class."""

import threading
import time
from queue import Empty, Queue
from typing import Any, List, Optional

import cv2
from cv2 import VideoCapture

from pyvision.camera import VideoStreamProvider
from pyvision.camera.fps import FPS


@VideoStreamProvider.register
class OpenCVVideoStream:
    """Class representing a video stream using OpenCV."""

    def __init__(
        self,
        idx: int = 0,
        width: int = 960,
        height: int = 540,
        desired_fps: int = 24,
        queuesize: int = 128,
    ) -> None:
        """Initialize the OpenCVVideoStream object.

        Args:
            idx (int): Index of the video capture device.
            width (int): Width of the video frame.
            height (int): Height of the video frame.
            desired_fps (int): Desired frames per second.
            queuesize (int): Size of the queue storing the video frames.

        """
        self.idx = idx
        self.width = width
        self.height = height
        self.count = 0
        self.stop_event: threading.Event = threading.Event()
        self.update_thread: threading.Thread = threading.Thread(target=self.update)
        self.stream: VideoCapture = cv2.VideoCapture(idx, cv2.CAP_MSMF)
        self.stream.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        self.stream.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
        print("current exposure: ", self.stream.get(cv2.CAP_PROP_EXPOSURE))
        self.stream.set(cv2.CAP_PROP_EXPOSURE, 0)

        max_supported_fps = self.stream.get(cv2.CAP_PROP_FPS)
        if desired_fps > max_supported_fps:
            print(
                f"You request more FPS that the backend actually support. falling back to {max_supported_fps}"
            )
        desired_fps = min(desired_fps, int(max_supported_fps))
        self.fps = FPS(desired_fps)

        self.Q: Queue[int] = Queue(maxsize=queuesize)

        self.frames: List[Optional[cv2.UMat]] = [None] * queuesize
        for i in range(queuesize):
            self.frames[i] = cv2.UMat(self.height, self.width, cv2.CV_8UC3)

    def update(self):
        """Update the video stream frames.

        This method continuously reads frames from the video stream and updates the frame attribute.

        """
        while not self.stop_event.is_set():
            if self.stream.isOpened() and not self.Q.full():
                self.count += 1
                target = (self.count - 1) % self.Q.maxsize
                grabbed = self.stream.grab()
                if not grabbed:
                    self.stop()
                    return

                self.stream.retrieve(self.frames[target])

                if not self.Q.empty():
                    try:
                        self.Q.get_nowait()
                    except Empty:
                        pass

                self.Q.put(target)

                self.fps.update(False)

    def start(self):
        """Start the video stream.

        Returns:
            OpenCVVideoStream: The current instance of the OpenCVVideoStream object.

        """
        if self.stop_event.is_set():
            self.stop_event.clear()

        self.update_thread.start()
        return self

    def read(self) -> cv2.UMat | None:
        """Read the current frame from the video stream.

        Returns:
            numpy.ndarray: The current frame of the video stream.

        """
        while (not self.more()) and (not self.stop_event.is_set()):
            time.sleep(0.1)

        # return the next frame in the queue
        return self.frames[self.Q.get()]

    def more(self):
        """Check if there are more frames to read."""
        return self.Q.qsize() > 0

    def stop(self):
        """Stop the video stream."""
        if self.update_thread and self.update_thread.is_alive():
            self.stop_event.set()
            print("waiting update_thread to join")
            self.update_thread.join()
            print("update_thread joined!")

        if self.stream:
            self.stream.release()

    def info(self) -> dict[str, Any]:
        """Return the information about the video stream.

        Returns:
            dict[str, int]: The information about the video stream.

        """
        return {
            "width": self.width,
            "height": self.height,
            "fps": self.fps.get_fps(),
            "idx": self.idx,
        }

    def isOpened(self) -> bool:
        """Check if the video stream is opened.

        Returns:
            bool: True if the video stream is opened, False otherwise.

        """
        return self.stream.isOpened() if self.stream else False
