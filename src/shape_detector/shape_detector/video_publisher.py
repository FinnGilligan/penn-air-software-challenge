import os

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import cv2

from ament_index_python.packages import get_package_share_directory


class VideoPublisher(Node):

    def __init__(self):
        super().__init__("video_publisher")

        self.publisher = self.create_publisher(
            Image,
            "camera/image",
            10
        )

        self.bridge = CvBridge()

        package_directory = get_package_share_directory(
            "shape_detector"
        )

        video_path = os.path.join(
            package_directory,
            "videos",
            "hard.mp4"
        )

        self.cap = cv2.VideoCapture(video_path)

        self.timer = self.create_timer(
            1 / 30,
            self.publish_frame
        )

    def publish_frame(self):
        ret, frame = self.cap.read()

        if not ret:
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            return

        message = self.bridge.cv2_to_imgmsg(
            frame,
            encoding="bgr8"
        )

        self.publisher.publish(message)


def main(args=None):
    rclpy.init(args=args)

    node = VideoPublisher()

    rclpy.spin(node)

    node.cap.release()
    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()
