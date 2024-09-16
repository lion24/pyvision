"""This is the camera app module that will be used to display the camera feed in a tkinter window."""

import tkinter as tk
from tkinter import ttk
from typing import Any, Callable, Union

from pyvision.utils.observer import ConcreteSubject
from pyvision.views.root import Root
from pyvision.views.video import VideoView

CameraSelectionType = Union[tk.StringVar, str]
CameraSelectionCallback = Callable[[CameraSelectionType], None]


class View:
    """A class representing a view in the application.

    Args:
        width (int): The width of the view.
        height (int): The height of the view.
    """

    def __init__(self):
        """Initializes a new instance of the Main class.

        Args:
            width (int): The width of the main window.
            height (int): The height of the main window.
        """
        self.root = Root()
        self.camera_menu_view = CameraSelectionFrame(self.root)
        self.camera_menu_view.pack(side=tk.TOP, fill=tk.X)
        self.video_view = VideoView(self.root, width=1280, height=720)
        self.video_view.pack(fill=tk.BOTH, expand=True)

    def start_mainloop(self):
        """Starts the main loop of the view."""
        self.root.mainloop()


class MainView(tk.Frame):
    """A class representing a camera application that displays the camera feed in a tkinter window."""

    def __init__(self) -> None:
        """Initialize the CameraApp object."""
        self.camera_menu = None
        self.brightness = 255
        self.contrast = 127
        self.cameras = {"foo": 0}

        self.brightness_and_contrast_frame = ImageBrightnessAndContrastFrame(self)
        self.brightness_and_contrast_frame.pack()


class CameraSelectionFrame(tk.Frame):
    """A class representing the camera selection frame in the camera app.

    Attributes:
        cameras (dict): A dictionary of available cameras.

    """

    def __init__(self, master: tk.Tk, **kwargs: Any) -> None:
        """Initialize the CameraSelectionFrame object.

        Args:
            master (tk.Tk): The parent of the CameraSelectionFrame.
            **kwargs (Any): Additional keyword arguments.

        """
        super().__init__(master, **kwargs)
        self.camera_opt = tk.StringVar(self)
        self.camera_opt.set("Select camera")
        self.menu = ttk.OptionMenu(
            self,
            self.camera_opt,
            "Select camera",
            command=self.on_camera_select,
        )
        self.menu.pack()
        self.on_select_callback = None

    def on_camera_select(self, event: tk.StringVar):
        """Callback function called when a camera is selected from the dropdown menu.

        Args:
            event (tk.StringVar): The selected camera.

        """
        if self.on_select_callback:
            self.on_select_callback(event)

    def set_on_select_callback(self, callback: CameraSelectionCallback) -> None:
        """Set the callback function to be called when a camera is selected.

        Args:
            callback (Callable[[str], None]): The callback function.

        """
        self.on_select_callback = callback


class ImageBrightnessAndContrastFrame(tk.Frame, ConcreteSubject):
    """A class representing the image brightness and contrast frame in the camera app.

    Attributes:
        brightness (int): The brightness of the image.
        contrast (int): The contrast of the image.

    """

    def __init__(self, parent: MainView):
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
