import os

# TODO: without this, some camera like my logitech c922 take forever to initialize
# understand why and see if there's a better fix
os.environ["OPENCV_VIDEOIO_MSMF_ENABLE_HW_TRANSFORMS"] = "0"

import cv2
import pygame
import tkinter as tk
from tkinter import ttk

import pyvision.utils as utils

from pyvision.ui.pygame_frame import PygameFrame
from pyvision.camera.opencv import OpenCVVideoStream
from pyvision.utils.observer import Observer

class CameraApp(tk.Tk, Observer):
    def __init__(self, width, height, frame_rate):
        super().__init__()
        self.title("Python OpenCV ML")
        self.geometry(f"{width}x{height}")
        self.width = width
        self.height = height
        self.frame_rate = frame_rate

        self.cap = None

        self.cameras = utils.get_video_backends()
        if not self.cameras:
            print("No cameras found")
            exit(1)

        self.init_ui()
        #self.camera_opt.set(next(iter(self.cameras.keys()), "Select camera"))

        # Attach an observer to receive updates and update the display
        self.pygame_frame.attach(self)

        self.camera_opt.trace_add('write', self.on_camera_select)

        # Manually trigger the first selection if a camera is available
        if next(iter(self.cameras.keys()), "Select camera") != "Select camera":
            self.camera_opt.set(next(iter(self.cameras.keys())))
        
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    def init_ui(self):
        self.top_frame = tk.Frame(self)
        self.top_frame.pack(side=tk.TOP, fill=tk.X)

        self.camera_opt = tk.StringVar(self)
        self.camera_opt.set("Select camera")

        self.camera_menu = ttk.OptionMenu(self.top_frame, self.camera_opt, "Select camera", *self.cameras.keys())
        self.camera_menu.pack()

        self.pygame_frame = PygameFrame(self, width=self.width, height=self.height, fps=self.frame_rate)
        self.pygame_frame.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)

    def on_camera_select(self, *args):
        idx = self.cameras.get(self.camera_opt.get())
        if idx is None:
            print("No camera selected")
            return
        if self.cap is not None:
            print(f"stopping camera {idx}")
            self.cap.stop()

        cap = OpenCVVideoStream(idx, self.width, self.height, self.frame_rate).start()
        if not cap.isOpened():
            print(f"Failed to open camera index {idx}")
            return

        self.cap = cap

    def on_closing(self):
        if self.cap is not None:
            print("cap stopping...")
            self.cap.stop()
            print("cap stopped!")

        self.pygame_frame.detach(self)
        self.destroy()
        pygame.quit()

    def update(self, subject):
        """
        called everytime an update from the pygame frame is requested
        This call will have the effect to refresh the image displayed
        """
        if self.cap.isOpened():
            frame = self.cap.read()
            camera_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            camera_surf = pygame.surfarray.make_surface(camera_image.transpose(1, 0, 2))
            self.pygame_frame.screen.blit(camera_surf, (0, 0))