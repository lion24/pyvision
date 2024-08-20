"""This module contains the VideoController class."""

import threading
from typing import Any, Tuple

from pyvision.models.camera import CameraModel
from pyvision.models.filters import (
    NoOpFilter,
    YUNetFaceDetectionFilter,
)
from pyvision.models.opencv_stream import READ_ERROR
from pyvision.models.stream import StreamModel
from pyvision.utils.fps import FPS
from pyvision.utils.observer import Observer, Subject
from pyvision.views.main import View


# The VideoController is an observer of the VideoModel and controls the video stream.
class VideoController(Observer):
    """The VideoController class controls the video stream and updates the frame."""

    def __init__(self, view: View, model: StreamModel, camera_model: CameraModel):
        """Initialize the VideoController.

        Args:
            view (VideoView): The view to update with the new frame.
            model (VideoModel): The model to observe for new frames.
            camera_model (CameraModel): The camera model to observe for camera changes.

        """
        self.view = view
        self.model = model
        self.camera_model = camera_model

        # To manage the camera
        self.camera_model.attach(self)

        self.stop_event: threading.Event = threading.Event()

        # subscribe to the model
        self.model.attach(self)

        # Instantiate the FPS counter
        self.fps = FPS(throttle_fps=self.model.fps)
        self.fps.attach(self)

        # Actions hastable to call the corresponding function based on the subject
        self.actions = {
            self.fps: lambda: self.view.video_view.update_fps(self.fps.get_fps()),
            self.model: lambda: self.view.video_view.update_frame(self.model.frame),
            self.camera_model: self.handle_camera_update,
        }

        # Add filters to the model
        self.model.add_filter(YUNetFaceDetectionFilter(NoOpFilter()).process)
        self._bind()

    def _bind(self):
        """Bind the view events to the controller methods."""
        self.view.root.protocol("WM_DELETE_WINDOW", self.stop)

        default_camera = self.camera_model.default_camera_name

        self.view.camera_menu_view.menu.set_menu(
            default_camera, *self.camera_model.cameras.keys()
        )

        self.view.camera_menu_view.set_on_select_callback(self.select_camera)

    def select_camera(self, camera_name: str):
        """Select a camera by its name.

        Args:
            camera_name (str): The name of the camera to select.

        """
        self.camera_model.select_camera(camera_name)

    def update(self):
        """Update the video stream frames.

        This method continuously reads frames from the video stream and updates the frame attribute.

        """
        while not self.stop_event.is_set():
            ret, frame = self.model.stream.read_frame()
            match ret:
                case READ_ERROR.NO_FRAME:
                    continue  # Allow some frame to be dropped (usefull when switching cameras)
                case READ_ERROR.NO_STREAM:
                    print("no stream")
                    self.stop_thread()
                    return
                case READ_ERROR.UNKNOWN_ERROR:
                    print("unknown error")
                    self.stop_thread()
                    return
                case READ_ERROR.NO_ERROR:
                    self.model.process(frame.get())
                    self.fps.update(throttle=True)

    def start(self):
        """Start the video stream.

        Returns:
            OpenCVVideoStream: The current instance of the OpenCVVideoStream object.

        """
        if self.stop_event.is_set():
            self.stop_event.clear()

        self.update_thread: threading.Thread = threading.Thread(target=self.update)
        self.update_thread.start()
        return self

    def stop_thread(self):
        """Stop the video stream."""
        print("stopping the video stream")
        self.stop_event.set()

        if self.update_thread.is_alive():
            print("waiting update_thread to join")
            self.update_thread.join()
            print("update_thread joined!")

    def stop(self):
        """Stop the video stream and destroy the view."""
        print("stopping the video stream and destroying the view")
        self.stop_thread()
        self.view.root.destroy()
        self.model.detach(self)
        self.camera_model.detach(self)
        self.fps.detach(self)
        self.model.release()

    def notify_update(
        self, subject: Subject, *args: Tuple[Any], **kwargs: dict[str, Any]
    ) -> None:
        """Called everytime to model change, hence when a new frame is available.

        The controller will instruct the view to repaint with the new frame.

        Args:
            subject (Subject): The subject that triggered the update.
            *args (Tuple[Any]): Additional arguments.
            **kwargs (dict[str, Any]): Additional keyword arguments.

        """
        # Call the appropriate action based on the subject
        # This is a way to avoid using if-elif-else statements
        # Since we know the subject is one of the keys in the actions dictionary
        # we can call the corresponding value (a function) using the subject as the key
        # and ignore the type check since we know the key is in the dictionary
        self.actions[subject]()  # type: ignore

    def handle_camera_update(self):
        """Handle the camera update event."""
        print("new camera update: ", self.camera_model.selected_camera)
        self.stop_thread()
        self.model.stream.update_stream_path(self.camera_model.selected_camera)
        self.start()
