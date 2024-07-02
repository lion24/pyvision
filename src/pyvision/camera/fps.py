import time
import timeit


class FPS:
    def __init__(self, throttle_fps: int = 30):
        self.prev_time = timeit.default_timer()
        self.total_time = 0.0
        self.num_frames = 0
        self.throttle_fps = throttle_fps
        self.fps = 0

    def update_time(self):
        current_time = timeit.default_timer()
        self.delta_time = current_time - self.prev_time
        self.total_time += self.delta_time
        self.prev_time = current_time

    def update(self, throttle: bool = False):
        self.update_time()
        self.num_frames += 1
        self.fps = self.num_frames / self.total_time

        if throttle:
            sleep_time = (1.0 / self.throttle_fps) - self.delta_time
            if sleep_time > 0.0:
                time.sleep(sleep_time)
                self.update_time()

    def get_fps(self):
        return self.fps
