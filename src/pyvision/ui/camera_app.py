"""This is the camera app module that will be used to display the camera feed in a tkinter window."""

import tkinter as tk
from tkinter import ttk
from typing import Any, Tuple

import cv2
import pygame
from cv2.typing import MatLike

from pyvision.camera.opencv import OpenCVVideoStream
from pyvision.models import ImageProcessingStrategy
from pyvision.models.filters import (
    EdgeDetectionKernelFilter,
    NoOpFilter,
)
from pyvision.ui.pygame_frame import PygameFrame
from pyvision.utils.observer import ConcreteSubject, Observer, Subject


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
        # +60 for the brightness and contrast frame
        # TODO dynamically adjust the height of the window
        self.geometry(f"{width}x{height+60}")
        self.width = width
        self.height = height
        self.frame_rate = frame_rate
        self.cap = None
        self.cameras = cameras
        self.camera_menu = None
        self.brightness = 255
        self.contrast = 127
        self.init_ui()
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        # set default processing strategy
        self.processing_strategy: ImageProcessingStrategy = EdgeDetectionKernelFilter(
            NoOpFilter()
        )

    def init_ui(self) -> None:
        """Initialize the user interface of the camera app."""
        self.camera_menu = CameraSelectionFrame(self, self.cameras)
        self.brightness_and_contrast_frame = ImageBrightnessAndContrastFrame(self)
        self.brightness_and_contrast_frame.pack()
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
        """Called every time an update from a subject is requested.

        This call will have the effect of refreshing the image displayed.

        Args:
            subject (Subject): The subject that triggered the update.
            *args (Tuple[Any]): Additional arguments.
            **kwargs (dict[str, Any]): Additional keyword arguments.

        """
        if isinstance(subject, CameraSelectionFrame):
            print("Camera selected")
            self.on_camera_select(*args)
        elif isinstance(subject, ImageBrightnessAndContrastFrame):
            print(
                f"Brightness and contrast updated {self.brightness} : {self.contrast}"
            )
            self.brightness = self.brightness_and_contrast_frame.get_brightness()
            self.contrast = self.brightness_and_contrast_frame.get_contrast()

        if self.cap is not None and self.cap.isOpened():
            frame = self.cap.read()
            frame = self.adjust_brightness_contrast(
                frame, self.brightness, self.contrast
            )
            processed_frame = self.processing_strategy.process(frame)
            cv2.putText(
                processed_frame,
                "{:.0f} frame/s".format(self.cap.info()["fps"]),
                (self.width - 180, self.height - 40),
                cv2.FONT_HERSHEY_TRIPLEX,
                1.0,
                (0, 255, 0),
                1,
            )
            processed_frame = cv2.cvtColor(processed_frame, cv2.COLOR_BGR2RGB)
            camera_surf: pygame.Surface = pygame.surfarray.make_surface(  # type: ignore
                processed_frame.transpose((1, 0, 2))
            )
            self.pygame_frame.screen.blit(camera_surf, (0, 0))

    def adjust_brightness_contrast(
        self, frame: MatLike, brightness: int = 255, contrast: int = 127
    ) -> MatLike:
        """Adjusts the brightness and contrast of an input frame.

        Args:
            frame (MatLike): The input frame to adjust.
            brightness (int, optional): The brightness value. Defaults to 255.
            contrast (int, optional): The contrast value. Defaults to 127.

        Returns:
            MatLike: The adjusted frame.
        """
        brightness = int(
            (brightness - 0) * (255 - (-255)) / (510 - 0) + (-255)
        )  # Normalize brightness
        contrast = int(
            (contrast - 0) * (127 - (-127)) / (254 - 0) + (-127)
        )  # Normalize contrast

        if brightness != 0:
            if brightness > 0:
                shadow = brightness
                max = 255
            else:
                shadow = 0
                max = 255 + brightness

            al_pha = (max - shadow) / 255
            ga_mma = shadow

            # The function addWeighted calculates
            # the weighted sum of two arrays
            cal = cv2.addWeighted(frame, al_pha, frame, 0, ga_mma)
        else:  # type: ignore
            cal = frame

        if contrast != 0:
            Alpha = float(131 * (contrast + 127)) / (127 * (131 - contrast))
            Gamma = 127 * (1 - Alpha)

            # The function addWeighted calculates
            # the weighted sum of two arrays
            cal = cv2.addWeighted(cal, Alpha, cal, 0, Gamma)

        return cal

    def on_brightness_change(self, event: Any) -> None:
        """Callback function called when the brightness scale is changed.

        Args:
            event (tk.Event): The event object.

        """
        self.brightness = self.brightness_and_contrast_frame.get_brightness()
        self.notify_update(self.brightness_and_contrast_frame)

    def on_contrast_change(self, event: Any) -> None:
        """Callback function called when the brightness scale is changed.

        Args:
            event (tk.Event): The event object.

        """
        self.contrast = self.brightness_and_contrast_frame.get_contrast()
        self.notify_update(self.brightness_and_contrast_frame)


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


class ImageBrightnessAndContrastFrame(tk.Frame, ConcreteSubject):
    """A class representing the image brightness and contrast frame in the camera app.

    Attributes:
        brightness (int): The brightness of the image.
        contrast (int): The contrast of the image.

    """

    def __init__(self, parent: CameraApp):
        """Initialize the ImageBrightnessAndContrastFrame object.

        Args:
            parent (CameraApp): The parent camera app.

        """
        super().__init__(parent)
        ConcreteSubject.__init__(self)
        self.pack(side=tk.TOP, fill=tk.X)

        # Configure grid layout to expand
        self.columnconfigure(1, weight=1)
        self.columnconfigure(3, weight=1)

        self.brightness_label = tk.Label(self, text="Brightness")
        self.brightness_label.grid(row=0, column=0, padx=10, pady=5, sticky="e")

        self.brightness_scale = ttk.Scale(
            self, from_=0, to=2 * 255, orient=tk.HORIZONTAL
        )
        self.brightness_scale.set(255)  # type: ignore
        self.brightness_scale.grid(row=0, column=1, padx=10, pady=5, sticky="ew")

        self.contrast_label = tk.Label(self, text="Contrast")
        self.contrast_label.grid(row=0, column=2, padx=10, pady=5, sticky="e")

        self.contrast_scale = ttk.Scale(self, from_=0, to=2 * 127, orient=tk.HORIZONTAL)
        self.contrast_scale.set(127)  # type: ignore
        self.contrast_scale.grid(row=0, column=3, padx=10, pady=5, sticky="ew")

        self.brightness_scale.bind("<ButtonRelease-1>", parent.on_brightness_change)
        self.contrast_scale.bind("<ButtonRelease-1>", parent.on_contrast_change)

    def get_brightness(self) -> int:
        """Get the brightness value.

        Returns:
            int: The brightness value.

        """
        return int(self.brightness_scale.get())

    def get_contrast(self) -> int:
        """Get the contrast value.

        Returns:
            int: The contrast value.

        """
        return int(self.contrast_scale.get())
