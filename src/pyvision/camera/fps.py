from datetime import datetime

class FPS:
    def __init__(self):
        self._start : datetime = None
        self._end : datetime = None
        self.num_frames = 0

    def start(self):
        self._start = datetime.now()
        return self
    
    def stop(self):
        self._end = datetime.now()
    
    def update(self):
        self.num_frames += 1

    def elapsed(self):
        return (self._end - self._start).total_seconds()
    
    def fps(self):
        return self.num_frames / self.elapsed()