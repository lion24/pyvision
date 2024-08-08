"""This module defines a custom Pygame frame that inherits from tkinter Frame and ConcreteSubject."""

import os
import tkinter as tk
from typing import Any

import cv2
import pygame


class VideoView(tk.Frame):
    """A custom Pygame frame that inherits from tkinter Frame and ConcreteSubject."""

    def __init__(
        self,
        master: tk.Tk,
        **kwargs: Any,
    ) -> None:
        """Initializes the PygameFrame.

        Args:
            master (tk.Tk): The parent of the PygameFrame (the root view generally).
            **kwargs: Additional keyword arguments to pass to the tkinter Frame constructor.
        """
        super().__init__(master, **kwargs)
        """Initializes the Pygame library and sets up the Pygame display."""
        self._master = master
        pygame.init()
        os.environ["SDL_WINDOWID"] = str(self.winfo_id())
        os.environ["SDL_VIDEODRIVER"] = "windib"
        pygame.display.init()
        flags = pygame.FULLSCREEN | pygame.NOFRAME
        self.screen = pygame.display.set_mode(
            (self.winfo_width(), self.winfo_height()), flags
        )
        self.fps_surface = None

    @property
    def parent(self) -> tk.Tk:
        """Returns the parent of the PygameFrame.

        Returns:
            tk.Tk: The parent of the PygameFrame.
        """
        return self._master

    def set_pygame_viewport_size(self, width: int, height: int):
        """Sets the size of the Pygame viewport.

        Args:
            width (int): The width of the viewport.
            height (int): The height of the viewport.
        """
        if self.screen:
            self.screen = pygame.display.set_mode((width, height))

    def destroy(self):
        """Destroys the Pygame display."""
        pygame.display.quit()

    def update_frame(self, frame: cv2.UMat) -> None:
        """Called by the controller when a new update is available.

        Args:
            frame (cv2.UMat): The frame to be updated.
        """
        # print(f"Updating frame: {frame}")
        processed_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        camera_surf: pygame.Surface = pygame.surfarray.make_surface(  # type: ignore
            processed_frame.get().transpose((1, 0, 2))
        )
        self.screen.blit(camera_surf, (0, 0))
        if self.fps_surface:
            self.screen.blit(self.fps_surface, (10, 10))
        pygame.display.update()

    def update_fps(self, fps: int) -> None:
        """Updates the frames per second display.

        Args:
            fps (int): The frames per second to be displayed.
        """
        font = pygame.font.Font(None, 36)
        fps_text = font.render(f"{fps} FPS", True, (0, 255, 0))
        self.fps_surface = fps_text
