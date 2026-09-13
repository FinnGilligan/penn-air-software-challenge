import math
import cv2
import numpy as np

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge

from shape_detector_msgs.msg import Detection


class ImageSubscriber(Node):

    def __init__(self):
        super().__init__("image_subscriber")

        self.subscription = self.create_subscription(
            Image,
            "camera/image",
            self.image_callback,
            10
        )

        self.detection_publisher = self.create_publisher(
            Detection,
            "detections",
            10
        )

        self.bridge = CvBridge()

        self.fx = 2564.3187
        self.fy = 2569.7027
        self.f = (self.fx + self.fy) / 2

        self.depth = 180

        self.font = cv2.FONT_HERSHEY_SIMPLEX
        self.font_scale = 1
        self.text_color = (0, 255, 0)
        self.text_thickness = 2

    def image_callback(self, message):

        img = self.bridge.imgmsg_to_cv2(
            message,
            desired_encoding="bgr8"
        )

        height, width = img.shape[:2]

        horizontal = cv2.absdiff(
            img[:-1, :-1],
            img[:-1, 1:]
        )

        vertical = cv2.absdiff(
            img[:-1, :-1],
            img[1:, :-1]
        )

        horizontal = np.max(horizontal, axis=2)
        vertical = np.max(vertical, axis=2)

        grayscale = cv2.cvtColor(
            img[:-1, :-1],
            cv2.COLOR_BGR2GRAY
        ).astype(np.float32)

        local_mean = cv2.blur(
            grayscale,
            (5, 5)
        )

        local_sqmean = cv2.blur(
            grayscale ** 2,
            (5, 5)
        )

        local_var = local_sqmean - local_mean ** 2

        mask = np.where(
            (horizontal <= 4)
            & (vertical <= 4)
            & (local_var <= 19),
            255,
            0
        ).astype(np.uint8)

        goofy_mask = cv2.inRange(
            img,
            (110, 70, 130),
            (160, 230, 180)
        )

        goofy_mask = goofy_mask[:-1, :-1]

        kernel = np.ones((7, 7), np.uint8)

        goofy_mask = cv2.morphologyEx(
            goofy_mask,
            cv2.MORPH_OPEN,
            kernel
        )

        kernel = np.ones((2, 2), np.uint8)

        mask = cv2.morphologyEx(
            mask,
            cv2.MORPH_OPEN,
            kernel
        )

        mask = cv2.bitwise_or(
            mask,
            goofy_mask
        )

        contours, _ = cv2.findContours(
            mask,
            cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE
        )

        contours = sorted(
            contours,
            key=cv2.contourArea,
            reverse=True
        )

        circle = None
        detections = []

        for contour in contours[:5]:

            area = cv2.contourArea(contour)
            perimeter = cv2.arcLength(contour, True)

            if perimeter == 0:
                continue

            circularity = (
                4 * math.pi * area
            ) / (
                perimeter * perimeter
            )

            coverage = area / (height * width)

            if coverage < 0.00675:
                continue

            moments = cv2.moments(contour)

            if moments["m00"] == 0:
                continue

            cx = moments["m10"] / moments["m00"]
            cy = moments["m01"] / moments["m00"]

            cv2.circle(
                img,
                (int(cx), int(cy)),
                25,
                (0, 0, 255),
                -1
            )

            cv2.putText(
                img,
                "center",
                (int(cx - 45), int(cy - 25)),
                self.font,
                self.font_scale,
                self.text_color,
                self.text_thickness
            )

            coordinates = (
                f"Coordinates: "
                f"[{int(cx * self.depth / self.fx)}, "
                f"{int(cy * self.depth / self.fy)}, "
                f"{int(self.depth)}]"
            )

            cv2.putText(
                img,
                coordinates,
                (int(cx - 185), int(cy + 50)),
                self.font,
                self.font_scale,
                self.text_color,
                self.text_thickness
            )

            if (
                circularity > 0.4
                and 0.0145 < coverage < 0.016
            ):
                circle = contour
                contour_to_draw = contour

            else:
                epsilon = 0.03 * perimeter
                contour_to_draw = cv2.approxPolyDP(
                    contour,
                    epsilon,
                    True
                )

            detection = Detection()

            detection.x = float(cx * self.depth / self.fx)
            detection.y = float(cy * self.depth / self.fy)
            detection.z = float(self.depth)

            for point in contour_to_draw:
                detection.outline_x.append(
                    float(point[0][0])
                )
                detection.outline_y.append(
                    float(point[0][1])
                )

            detections.append(detection)

            cv2.drawContours(
                img,
                [contour_to_draw],
                -1,
                (0, 0, 255),
                5
            )

        if circle is not None:

            cv2.drawContours(
                img,
                [circle],
                -1,
                (255, 0, 255),
                5
            )

            circle_perimeter = cv2.arcLength(
                circle,
                True
            )

            scale = (
                circle_perimeter /
                (2 * math.pi * 10)
            )

            self.depth = self.f / scale

        for detection in detections:
            self.detection_publisher.publish(detection)

        cv2.imshow(
            "Video",
            img
        )

        cv2.waitKey(1)


def main(args=None):

    rclpy.init(args=args)

    node = ImageSubscriber()

    rclpy.spin(node)

    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()
