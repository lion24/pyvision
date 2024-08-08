"""Main controller class for the application."""

from typing import TypedDict

from pyvision.controllers.video import VideoController
from pyvision.models.opencv_stream import OpenCVCameraSettings
from pyvision.models.video import VideoModel
from pyvision.views.main import View


class AppConfig(TypedDict):
    """Configuration settings for the application."""

    camera_settings: OpenCVCameraSettings


class Controller:
    """Main controller class for the application."""

    def __init__(self, config: AppConfig):
        """Initialize the Controller object.

        Args:
            config (AppConfig): Configuration settings for the application.
        """
        self.config = config
        self.view = View()  # This hold all the views from the application
        self.model = VideoModel(**self.config.get("camera_settings"))
        self.video_controller = VideoController(self.view, self.model)

    def run(self):
        """Run the application."""
        self.video_controller.start()
        self.view.start_mainloop()
