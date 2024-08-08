"""This module contains the Root class, which is a custom Tkinter root window."""

from tkinter import Tk
from typing import NotRequired, TypedDict

from typing_extensions import Unpack


class TkinterMainWindowSettings(TypedDict):
    """A dictionary type for the settings of the Tkinter main window."""

    resizable: NotRequired[bool]


class Root(Tk):
    """A custom Tkinter root window that inherits from tkinter.Tk.

    Args:
        title (str, optional): The title of the root window. Defaults to "PyVision".
        **kwargs: Additional keyword arguments to pass to the tkinter.Tk constructor.
    """

    def __init__(
        self,
        window_title: str = "Python OpenCV ML",
        **kwargs: Unpack[TkinterMainWindowSettings],
    ) -> None:
        """Initializes the Root.

        Args:
            window_title (str, optional): The title of the root window. Defaults to "PyVision".
            **kwargs: Additional keyword arguments to pass to the tkinter.Tk constructor.
        """
        super().__init__()
        self.title(window_title)
        _resizable = kwargs.get("resizable", False)
        if _resizable:
            self.resizable(_resizable, _resizable)
        self.update_idletasks()
