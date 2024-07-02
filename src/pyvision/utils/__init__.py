import device


def get_video_backends() -> dict:
    idx = 0
    cameras = {}

    for camera in device.getDeviceList():
        cameras[str(camera[0])] = idx
        idx += 1

    return cameras
