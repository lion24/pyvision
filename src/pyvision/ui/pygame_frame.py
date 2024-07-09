"""This module defines a custom Pygame frame that inherits from tkinter Frame and ConcreteSubject."""

import os
import tkinter as tk
from typing import Any, Optional

import pygame

from pyvision.utils.observer import ConcreteSubject


class PygameFrame(tk.Frame, ConcreteSubject):
    """A custom Pygame frame that inherits from tkinter Frame and ConcreteSubject.

    Args:
        master (tkinter.Tk, optional): The master widget. Defaults to None.
        width (int, optional): The width of the frame. Defaults to 1280.
        height (int, optional): The height of the frame. Defaults to 720.
        fps (int, optional): The frames per second for updating the frame. Defaults to 30.
        **kwargs: Additional keyword arguments to pass to the tkinter Frame constructor.
    """

    def __init__(
        self,
        master: Optional[tk.Tk] = None,
        width: int = 1280,
        height: int = 720,
        fps: int = 30,
        **kwargs: Any,
    ) -> None:
        """Initializes the PygameFrame.

        Args:
            master (tkinter.Tk, optional): The master widget. Defaults to None.
            width (int, optional): The width of the frame. Defaults to 1280.
            height (int, optional): The height of the frame. Defaults to 720.
            fps (int, optional): The frames per second for updating the frame. Defaults to 30.
            **kwargs: Additional keyword arguments to pass to the tkinter Frame constructor.
        """
        super().__init__(master, width=width, height=height, **kwargs)
        ConcreteSubject.__init__(self)
        self.width = width
        self.height = height
        self.fps = fps

        self.init_pygame()

    def init_pygame(self):
        """Initializes the Pygame library and sets up the Pygame display."""
        os.environ["SDL_WINDOWID"] = str(self.winfo_id())
        os.environ["SDL_VIDEODRIVER"] = "windib"
        pygame.display.init()
        flags = pygame.FULLSCREEN | pygame.NOFRAME
        self.screen = pygame.display.set_mode((self.width, self.height), flags)
        self.after(100, self.update_pygame)

    def update_pygame(self):
        """Updates the Pygame display and notifies the observers."""
        pygame.display.flip()
        self.notify()
        self.after(1000 // self.fps, self.update_pygame)
