"""Class to calculate frames per second (FPS)."""

import time
import timeit
from collections import deque
from typing import Deque

from pyvision.utils.observer import ConcreteSubject


class FPS(ConcreteSubject):
    """Class to calculate frames per second (FPS).

    This class provides methods to calculate the frames per second (FPS) of a process.
    It can be used to measure the performance of a video processing pipeline or any other process
    that involves processing frames at a certain rate.

    Attributes:
        prev_time (float): The previous time at which the update method was called.
        delta_time (float): The time difference between the last two frames.
        fps (float): The current frames per second (FPS) calculated by the update method.
        delta_times (deque): A deque to store recent delta_time values for smoothing.
        max_samples (int): Maximum number of samples to keep in the deque.
    """

    def __init__(self, max_fps: int = 30, max_samples: int = 10):
        """Initialize the FPS object.

        Args:
            max_fps (int): The desired FPS to throttle the update method (default: 30).
            max_samples (int): Maximum number of samples to keep in the deque for smoothing (default: 10).
        """
        if not isinstance(max_fps, int) or not isinstance(max_samples, int):  # type: ignore
            raise TypeError(
                f"max_fps and max_samples must be integers, got {type(max_fps)} and {type(max_samples)}"
            )

        if max_fps <= 0 or max_samples <= 0:
            raise ValueError("max_fps and max_samples must be greater than 0")

        ConcreteSubject.__init__(self)
        self.prev_time = timeit.default_timer()
        self.delta_time = 0.0
        self.max_fps = max_fps
        self.fps = 0
        self.delta_times: Deque[float] = deque(maxlen=max_samples)

    def update_time(self):
        """Update the current time and calculate the time difference."""
        current_time = timeit.default_timer()
        self.delta_time = current_time - self.prev_time
        self.prev_time = current_time

        # Apply saturation: self.delta_time should be ]0, 1/max_fps]
        min_delta_time = 1 / self.max_fps
        max_delta_time = 1.0  # 1 second
        self.delta_time = max(min_delta_time, min(self.delta_time, max_delta_time))

        # assert that the average delta time is within the desired range
        assert min_delta_time < self.delta_time <= max_delta_time

        self.delta_times.append(self.delta_time)

    def update(self, throttle: bool = False):
        """Update the FPS calculation.

        This method should be called each time a frame is processed to update the FPS calculation.
        It updates the current time, calculates the time difference, and updates the FPS value.

        Args:
            throttle (bool): Whether to throttle the FPS based on the desired FPS (default: False).
        """
        self.update_time()
        self.fps = 1.0 / (sum(self.delta_times) / len(self.delta_times))

        if throttle:
            sleep_time = (1.0 / self.max_fps) - self.delta_time
            if sleep_time > 0.0:
                time.sleep(sleep_time)

        self.notify()

    def get_fps(self) -> int:
        """Get the current frames per second (FPS).

        Returns:
            float: The current FPS.
        """
        return int(self.fps)
