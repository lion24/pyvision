"""A module implementing the YOLO object detection algorithm."""

import math
from typing import List

import cv2
import numpy as np
from ultralytics import YOLO  # type: ignore
from ultralytics.engine.results import Results  # type: ignore

from pyvision.models import Image, ImageProcessingDecorator, ImageProcessingStrategy


class YoloObjectDetection(ImageProcessingDecorator):
    """A class implementing the YoLo detection algorithm."""

    def __init__(self, wrapped: ImageProcessingStrategy, model: YOLO) -> None:
        """Initialize the YoloObjectDetection.

        Args:
            wrapped (ImageProcessingStrategy): The wrapped image processing strategy.
            model (YOLO): The YOLO model to use for object detection.
        """
        super().__init__(wrapped)
        self.model = model
        coco = open("coco/coco.names", "r")
        self.classes = [cls.strip() for cls in coco.readlines()]
        coco.close()
        self.colors = np.random.uniform(0, 255, size=(len(self.classes), 3))

    def process(self, _frame: Image) -> cv2.UMat:
        """Process the image with the YoloObjectDetection algorithm.

        Args:
            image (Image): The image to process.

        Returns:
            cv2.UMat: The processed image.
        """
        # return super().process(_frame)

        frame = super().process(_frame).get()
        results: List[Results] = self.model(frame, stream=True)
        for r in results:
            boxes = r.boxes  # type: ignore

            if boxes is not None:
                for box in boxes:  # type: ignore
                    x1, y1, x2, y2 = box.xyxy[0]  # type: ignore
                    x1, y1, x2, y2 = (
                        int(x1),
                        int(y1),
                        int(x2),
                        int(y2),
                    )  # convert to int values

                    cls = int(box.cls[0])  # type: ignore

                    # put box in cam
                    confidence = math.ceil((box.conf[0] * 100)) / 100  # type: ignore
                    self.draw_bounding_box(frame, cls, confidence, x1, y1, x2, y2)
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 0, 255), 3)

        return cv2.UMat(frame)  # type: ignore

    def draw_bounding_box(
        self,
        img: Image,
        class_id: int,
        confidence: float,
        x: int,
        y: int,
        x_plus_w: int,
        y_plus_h: int,
    ):
        """Draws bounding boxes on the input image based on the provided arguments.

        Args:
            img (numpy.ndarray): The input image to draw the bounding box on.
            class_id (int): Class ID of the detected object.
            confidence (float): Confidence score of the detected object.
            x (int): X-coordinate of the top-left corner of the bounding box.
            y (int): Y-coordinate of the top-left corner of the bounding box.
            x_plus_w (int): X-coordinate of the bottom-right corner of the bounding box.
            y_plus_h (int): Y-coordinate of the bottom-right corner of the bounding box.
        """
        label = f"{self.classes[class_id]} ({confidence:.2f})"
        color = self.colors[class_id]
        cv2.rectangle(img, (x, y), (x_plus_w, y_plus_h), color, 2)
        cv2.putText(
            img, label, (x - 10, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2
        )
