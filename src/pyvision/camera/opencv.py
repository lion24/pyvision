import os

# TODO: without this, some camera like my logitech c922 take forever to initialize
# understand why and see if there's a better fix
os.environ["OPENCV_VIDEOIO_MSMF_ENABLE_HW_TRANSFORMS"] = "0"

import threading

import cv2
from cv2 import VideoCapture

from pyvision.camera import VideoStreamProvider
from pyvision.camera.fps import FPS


@VideoStreamProvider.register
class OpenCVVideoStream:
    def __init__(self, idx=0, width=960, height=540, desired_fps=24):
        self.idx = idx
        self.width = width
        self.height = height
        self.stop_event: threading.Event = threading.Event()
        self.update_thread: threading.Thread = None
        self.stream: VideoCapture = cv2.VideoCapture(idx, cv2.CAP_MSMF)
        self.stream.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        self.stream.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

        max_supported_fps = self.stream.get(cv2.CAP_PROP_FPS)
        if desired_fps > max_supported_fps:
            print(
                f"You request more FPS that the backend actually support. falling back to {max_supported_fps}"  # noqa
            )
        self.desired_fps = min(desired_fps, self.stream.get(cv2.CAP_PROP_FPS))

        # Read and store the first frame
        (success, self.frame) = self.stream.read()
        if not success:
            print("init failed to read from stream")

    def update(self):
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
        if self.stop_event.is_set():
            self.stop_event.clear()

        self.update_thread = threading.Thread(target=self.update)
        self.update_thread.start()
        return self

    def read(self):
        return self.frame

    def stop(self):
        if self.update_thread is not None and self.update_thread.is_alive():
            self.stop_event.set()
            print("waiting update_thread to join")
            self.update_thread.join()
            print("update_thread joined!")

        if self.stream is not None:
            self.stream.release()
            self.stream = None

    def isOpened(self) -> bool:
        return self.stream.isOpened() if self.stream else None
