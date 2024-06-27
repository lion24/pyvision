import cv2
import threading

from pyvision.camera import VideoStreamProvider
from cv2 import VideoCapture



@VideoStreamProvider.register
class OpenCVVideoStream:
    def __init__(self, idx=0, width=960, height=540):
        self.idx = idx
        self.width = width
        self.height = height
        self.stop_event: threading.Event = threading.Event()
        self.update_thread : threading.Thread = None
        self.stream: VideoCapture = VideoCapture(idx)
        self.stream.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        self.stream.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

        # Read and store the first frame
        (success, self.frame) = self.stream.read()
        if not success:
            print("init failed to read from stream")

    def update(self):
        while not self.stop_event.is_set():
            if self.stream is not None and self.stream.isOpened():
                start_time = self.stream.get(cv2.CAP_PROP_POS_MSEC)
                ret, self.frame = self.stream.read()
                if not ret:
                    print("failed to read one frame")
                
                end_time = self.stream.get(cv2.CAP_PROP_POS_MSEC)
                elapsed = end_time - start_time
                print(f"read one frame in {elapsed} miliseconds")

                if elapsed > 100:
                    print("timeout reading frame")
                    continue

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