from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    return LaunchDescription([
        Node(
            package="shape_detector",
            executable="video_publisher",
            output="screen"
        ),

        Node(
            package="shape_detector",
            executable="image_subscriber",
            output="screen"
        )
    ])
