"""This module contains the CameraModel class."""

from pyvision import device
from pyvision.utils.observer import ConcreteSubject


class CameraModel(ConcreteSubject):
    """A class representing a camera model. This class extends the ConcreteSubject class and provides functionality for managing cameras.

    Attributes:
        cameras (list): A list of available video backends.
        selected_camera (str): The name of the selected camera.

    Methods:
        update_cameras(): Updates the list of available video backends and notifies the observers.
        select_camera(camera_name: str): Selects a camera based on its name and notifies the observers.
    """

    def __init__(self):
        """Initializes the CameraModel class by calling the parent class constructor."""
        ConcreteSubject.__init__(self)
        self.cameras = self.get_video_backends()
        self.selected_camera = 0

    @property
    def default_camera_name(self) -> str:
        """Returns the name of the default camera.

        Returns:
            str: The name of the default camera.
        """
        return [
            value for value, key in self.cameras.items() if key == self.selected_camera
        ][0]

    def update_cameras(self):
        """Updates the list of available video backends and notifies the observers."""
        self.cameras = self.get_video_backends()
        self.notify()

    def select_camera(self, camera_name: str):
        """Selects a camera based on its name and notifies the observers.

        Args:
            camera_name (str): The name of the camera to select.
        """
        self.selected_camera = self.cameras.get(camera_name, -1)
        self.notify()

    def get_video_backends(self) -> dict[str, int]:
        """Get the available video backends on the system.

        Returns:
            A dictionary mapping the backend names to their corresponding indices.
        """
        idx = 0
        cameras: dict[str, int] = {}

        for camera in device.getDeviceList():
            cameras[str(camera[0])] = idx
            idx += 1

        return cameras


if __name__ == "__main__":
    model = CameraModel()
    print(f"camera: {model.cameras}")
