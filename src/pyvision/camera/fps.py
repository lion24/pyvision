"""Class to calculate frames per second (FPS)."""

import time
import timeit


class FPS:
    """Class to calculate frames per second (FPS).

    This class provides methods to calculate the frames per second (FPS) of a process.
    It can be used to measure the performance of a video processing pipeline or any other process
    that involves processing frames at a certain rate.

    Attributes:
        prev_time (float): The previous time at which the update method was called.
        total_time (float): The total time elapsed since the FPS object was created.
        num_frames (int): The number of frames processed since the FPS object was created.
        throttle_fps (int): The desired FPS to throttle the update method.
        fps (float): The current frames per second (FPS) calculated by the update method.
    """

    def __init__(self, throttle_fps: int = 30):
        """Initialize the FPS object.

        Args:
            throttle_fps (int): The desired FPS to throttle the update method (default: 30).
        """
        self.prev_time = timeit.default_timer()
        self.total_time = 0.0
        self.num_frames = 0
        self.throttle_fps = throttle_fps
        self.fps = 0

    def update_time(self):
        """Update the current time and calculate the time difference."""
        current_time = timeit.default_timer()
        self.delta_time = current_time - self.prev_time
        self.total_time += self.delta_time
        self.prev_time = current_time

    def update(self, throttle: bool = False):
        """Update the FPS calculation.

        This method should be called each time a frame is processed to update the FPS calculation.
        It updates the current time, calculates the time difference, and updates the FPS value.

        Args:
            throttle (bool): Whether to throttle the FPS based on the desired FPS (default: False).
        """
        self.update_time()
        self.num_frames += 1
        self.fps = self.num_frames / self.total_time

        if throttle:
            sleep_time = (1.0 / self.throttle_fps) - self.delta_time
            if sleep_time > 0.0:
                time.sleep(sleep_time)
                self.update_time()

    def get_fps(self):
        """Get the current frames per second (FPS).

        Returns:
            float: The current FPS.
        """
        return self.fps
