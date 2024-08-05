"""Main controller class for the application."""

from typing import TypedDict

from pyvision.controllers.video import VideoController
from pyvision.models.camera import CameraModel
from pyvision.models.opencv_stream import OpenCVVideoStream
from pyvision.models.stream import StreamModel
from pyvision.views.main import View


class AppConfig(TypedDict):
    """Configuration settings for the application."""

    stream_provider: OpenCVVideoStream
    camera_model: CameraModel


class Controller:
    """Main controller class for the application."""

    def __init__(self, config: AppConfig):
        """Initialize the Controller object.

        Args:
            config (AppConfig): Configuration settings for the application.
        """
        self.config = config
        self.view = View()  # This hold all the views from the application

        self.stream_model = StreamModel(config.get("stream_provider"))
        self.camera_model = config.get("camera_model")
        self.video_controller = VideoController(
            self.view, self.stream_model, self.camera_model
        )

    def run(self):
        """Run the application."""
        self.video_controller.start()
        self.view.start_mainloop()
