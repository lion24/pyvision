"""Main entry point for the application."""

import os

# TODO: without this, some camera like my logitech c922 takes forever to initialize
# understand why and see if there's a better fix
os.environ["OPENCV_VIDEOIO_MSMF_ENABLE_HW_TRANSFORMS"] = "0"

import cv2

from pyvision import utils
from pyvision.ui.camera_app import CameraApp

FRAME_PER_SECONDS = 32

if __name__ == "__main__":
    print("OpenCV version: ", cv2.__version__)
    print(cv2.getBuildInformation())

    # Get the list of available cameras
    cameras = utils.get_video_backends()
    if not cameras:
        print("No camera found")
        exit(1)

    app = CameraApp(1280, 720, FRAME_PER_SECONDS, cameras)
    app.mainloop()
