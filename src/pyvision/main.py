import os

# TODO: without this, some camera like my logitech c922 take forever to initialize
# understand why and see if there's a better fix
os.environ["OPENCV_VIDEOIO_MSMF_ENABLE_HW_TRANSFORMS"] = "0"

import cv2
import pygame
import threading
import device
import tkinter as tk
import time
from tkinter import ttk

from pyvision.camera.opencv import OpenCVVideoStream
from pyvision.camera import VideoStreamProvider

WIDTH = 1280
HEIGHT = 720
FRAME_PER_SECONDS = 24

def get_video_backends() -> dict:
    idx = 0
    cameras = {}

    for camera in device.getDeviceList():
        cameras[str(camera[0])] = idx
        idx += 1

    return cameras

def image_loop(stream: VideoStreamProvider):
    clock = pygame.time.Clock()

    while stream.isOpened():
        frame = stream.read()
        camera_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        camera_surf = pygame.surfarray.make_surface(camera_image.transpose(1, 0, 2))
        screen.blit(camera_surf, (0, 0))
        pygame.display.update()
        time.sleep(0.01) # Avoid busy looping

def on_camera_select(*args):
    global cap, camera_opt, image_loop_thread
    idx = cameras.get(camera_opt.get())
    if idx is None:
        print("No camera selected")
        return
    if cap is not None:
        print(f"stopping camera {idx}")
        cap.stop()

    cap = OpenCVVideoStream(idx, WIDTH, HEIGHT, FRAME_PER_SECONDS).start()
    if not cap.isOpened():
        print(f"Failed to open camera index {idx}")
        return
    
    if image_loop_thread is not None and image_loop_thread.is_alive():
        image_loop_thread.join()

    image_loop_thread = threading.Thread(target=image_loop, args=(cap,))
    image_loop_thread.start()

if __name__ == "__main__":
    cap = None
    stop_event = None
    image_loop_thread = None

    print("OpenCV version: ", cv2.__version__)

    root = tk.Tk()
    root.title("Python OpenCV ML")
    root.geometry(f"{WIDTH}x{HEIGHT}")


    cameras = get_video_backends()
    if not cameras:
        print("No cameras found")
        exit(1)

    camera_opt = tk.StringVar(root)
    camera_opt.set("Select camera")

    top_frame = tk.Frame(root)
    top_frame.pack(side=tk.TOP, fill=tk.X)

    camera_menu = ttk.OptionMenu(top_frame, camera_opt, "Select camera", *cameras.keys())
    camera_menu.pack()

    pygame_frame = tk.Frame(root, width=WIDTH, height=HEIGHT)
    pygame_frame.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)

    root.update()  # Ensure that the frame is created before passing it to Pygame

    os.environ['SDL_WINDOWID'] = str(pygame_frame.winfo_id())
    os.environ['SDL_VIDEODRIVER'] = 'windib'
    pygame.display.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.NOFRAME)

    camera_opt.trace_add('write', on_camera_select)

    # Manually trigger the first selection if a camera is available
    if next(iter(cameras.keys()), "Select camera") != "Select camera":
        camera_opt.set(next(iter(cameras.keys())))

    def on_closing():
        if cap is not None:
            print("cap stopping...")
            cap.stop()
            print("cap stopped!")
        if image_loop_thread.is_alive():
            print("image_loop_thread stopping...")
            image_loop_thread.join()
            print("image_loop_thread stopped")
        root.destroy()
        pygame.quit()

    root.protocol("WM_DELETE_WINDOW", on_closing)

    # Run the main tkinter loop
    root.mainloop()
