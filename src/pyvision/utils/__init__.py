"""This module contains utility functions for the pyvision package."""

import device


def get_video_backends() -> dict:
    """Get the available video backends on the system.

    Returns:
        A dictionary mapping the backend names to their corresponding indices.
    """
    idx = 0
    cameras = {}

    for camera in device.getDeviceList():
        cameras[str(camera[0])] = idx
        idx += 1

    return cameras
