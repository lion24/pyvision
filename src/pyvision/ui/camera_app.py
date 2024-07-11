"""This is the camera app module that will be used to display the camera feed in a tkinter window."""

import tkinter as tk
from tkinter import ttk
from typing import Any, Tuple

import cv2
import pygame

from pyvision.camera.opencv import OpenCVVideoStream
from pyvision.ui.pygame_frame import PygameFrame
from pyvision.utils.observer import Observer, Subject


class CameraApp(tk.Tk, Observer):
    """A class representing a camera application that displays the camera feed in a tkinter window.

    Attributes:
        width (int): The width of the camera feed window.
        height (int): The height of the camera feed window.
        frame_rate (int): The frame rate of the camera feed.
        cap (VideoStreamProvider | None): The VideoStreamProvider object representing the camera feed.
        cameras (dict): A dictionary of available cameras.

    """

    def __init__(
        self, width: int, height: int, frame_rate: int, cameras: dict[str, int]
    ) -> None:
        """Initialize the CameraApp object.

        Args:
            width (int): The width of the camera feed window.
            height (int): The height of the camera feed window.
            frame_rate (int): The frame rate of the camera feed.
            cameras (dict[str, int]): A dictionary of available cameras.

        """
        super().__init__()
        self.title("Python OpenCV ML")
        self.geometry(f"{width}x{height}")
        self.width = width
        self.height = height
        self.frame_rate = frame_rate
        self.cap = None
        self.cameras = cameras
        self.camera_menu = None
        self.init_ui()
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    def init_ui(self) -> None:
        """Initialize the user interface of the camera app."""
        self.camera_menu = CameraSelectionFrame(self, self.cameras)
        self.pygame_frame = PygameFrame(
            self, width=self.width, height=self.height, fps=self.frame_rate
        )
        self.pygame_frame.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)
        self.pygame_frame.attach(self)

        initial_camera = next(iter(self.cameras.keys()), None)
        if initial_camera:
            self.camera_menu.camera_opt.set(initial_camera)

    def on_camera_select(self, *args: Any) -> None:
        """Callback function called when a camera is selected from the dropdown menu.

        Args:
            *args (Any): Additional arguments.

        """
        if self.camera_menu is None:
            return

        idx = self.camera_menu.get_selected_camera()
        if idx == -1:
            print("No camera selected")
            return
        if self.cap is not None:
            print(f"Stopping camera {self.cap}")
            self.cap.stop()
        cap = OpenCVVideoStream(idx, self.width, self.height, self.frame_rate).start()
        if not cap.isOpened():
            print(f"Failed to open camera index {idx}")
            return
        self.cap = cap

    def on_closing(self) -> None:
        """Callback function called when the camera app window is closed."""
        if self.cap is not None:
            print("cap stopping...")
            self.cap.stop()
            print("cap stopped!")
        self.pygame_frame.detach(self)
        self.destroy()
        pygame.quit()

    def notify_update(
        self, subject: Subject, *args: Tuple[Any], **kwargs: dict[str, Any]
    ) -> None:
        """Called every time an update from the pygame frame is requested.

        This call will have the effect of refreshing the image displayed.

        Args:
            subject (PygameFrame): The subject that triggered the update.
            *args (Tuple[Any]): Additional arguments.
            **kwargs (dict[str, Any]): Additional keyword arguments.

        """
        if isinstance(subject, CameraSelectionFrame):
            print("Camera selected")
            self.on_camera_select(*args)

        if self.cap is not None and self.cap.isOpened():
            frame = self.cap.read()
            camera_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            camera_surf: pygame.Surface = pygame.surfarray.make_surface(  # type: ignore
                camera_image.transpose(1, 0, 2)
            )
            self.pygame_frame.screen.blit(camera_surf, (0, 0))
            pygame.display.update()


class CameraSelectionFrame(tk.Frame):
    """A class representing the camera selection frame in the camera app.

    Attributes:
        cameras (dict): A dictionary of available cameras.

    """

    def __init__(self, parent: CameraApp, cameras: dict[str, int]):
        """Initialize the CameraSelectionFrame object.

        Args:
            parent (CameraApp): The parent camera app.
            cameras (dict[str, int]): A dictionary of available cameras.

        """
        super().__init__(parent)

        self.cameras = cameras

        self.pack(side=tk.TOP, fill=tk.X)
        self.camera_opt = tk.StringVar(self)
        self.camera_opt.set("Select camera")
        self.menu = ttk.OptionMenu(
            self, self.camera_opt, "Select camera", *self.cameras.keys()
        )
        self.menu.pack()

        self.camera_opt.trace_add("write", parent.on_camera_select)
        if next(iter(self.cameras.keys()), "Select camera") != "Select camera":
            self.camera_opt.set(next(iter(self.cameras.keys())))

    def get_selected_camera(self) -> int:
        """Get the selected camera index.

        Returns:
            int: The selected camera index.

        """
        return self.cameras.get(self.camera_opt.get(), -1)
