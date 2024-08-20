"""Main entry point for the application."""

import os

# TODO: without this, some camera like my logitech c922 takes forever to initialize
# understand why and see if there's a better fix
os.environ["OPENCV_VIDEOIO_MSMF_ENABLE_HW_TRANSFORMS"] = "0"

import cv2

from pyvision.controllers.main import AppConfig, Controller
from pyvision.models.camera import CameraModel
from pyvision.models.opencv_stream import OpenCVVideoStream, StreamSettings

FRAME_PER_SECONDS = 30

if __name__ == "__main__":
    print("OpenCV version: ", cv2.__version__)
    print(cv2.getBuildInformation())

    cv2.ocl.setUseOpenCL(True)
    if cv2.ocl.haveOpenCL():
        print("OpenCL is available")

    stream_settings: StreamSettings = {
        "path": 0,
        "width": 1280,
        "height": 720,
        "desired_fps": FRAME_PER_SECONDS,
    }

    app_config: AppConfig = {
        "camera_model": CameraModel(),
        "stream_provider": OpenCVVideoStream(**stream_settings),
    }

    app = Controller(app_config)
    app.run()
