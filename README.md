# PennAiR Software Challenge
Software challenge for PennAiR application. Shape detection using Python and OpenCV, along with ROS2 nodes.
This project detects colored and greyscale shapes in images and video, determines their centers and outlines, estimates 3D positions relative to a camera, and publishes the detection through ROS2.

# Approach:
The detection algorithm uses OpenCV and NumPy. The algorithm I settled on for the background agnosticism portion of the challenge uses neighboring pixel differences and local variance to separate the shapes from a noisy black-and-white background.

After detecting the shapes, the program uses built-in OpenCV contour and moment functions to determine the outlines and centers of the shapes.

The circle is used as a reference for estimating the distance of the shapes from the camera. Using the given intrinsic matrix for the camera and the dimensions of the circle, the depth of the plane on which the shapes are moving can be calculated. The pixel coordinates of each shape's center can then be converted into 3D coordinates.

More information on the approach can be found in [reports/shape_detection_report.md](reports/shape_detection_report.md)

# ROS 2
The project is implemented as an ROS 2 package and was tested using ROS 2 Jazzy.

The system consists of:

video_publisher - publishes frames of the given video as ROS 2 messages  
image_subscriber - receives the images, detects shapes, calculates 3D coordinates, and publishes these detections and calculations

The launch file starts both nodes:

```text
ros2 launch shape_detector shape_detection.launch.py
```
Detections are published on /detections, with the custom detection message containing a float64 x, float64 y, float64 z, float64[] outline_x, and float64[] outline_y. Each detection contains the 3D coordinates of the center of each shape and the pixel coordinates describing the shape's outline.

The detections can be inspected with:

```text
ros2 topic echo /detections
```

# Running the Project
After installing ROS 2 Jazzy and the required dependencies (cv_bridge, NumPy, OpenCV), create a ROS 2 workspace:

```bash
mkdir -p ~/ros2_ws/src
```

Clone this repository:

```bash
cd ~/ros2_ws/src
git clone https://github.com/FinnGilligan/penn-air-software-challenge.git
```

Move the packages into the workspace's src directory:

```bash
cd penn-air-software-challenge
cp -R src/* ~/ros2_ws/src/
```

Build the workspace:

```bash
cd ~/ros2_ws
colcon build
```

Source ROS 2 and the newly built workspace:

```bash
source /opt/ros/jazzy/setup.bash
source install/setup.bash
```

And finally, launch the shape detection system:

```bash
ros2 launch shape_detector shape_detection.launch.py
```

To view the published detections:

```bash
ros2 topic echo /detections
```

# Results
The [media/](media/) directory contains the input videos, processed videos, and processed images demonstrating the detection output.

Input\
The original challenge videos are located in [media/input/](media/input/).

Processed Results\
Processed videos and images are located in [media/processed/](media/processed/) and [media/images/](media/images/).

# Technical Report
The full technical report describing the reasoning behind the final iteration of the detection algorithm is available here: [reports/shape_detection_report.md](reports/shape_detection_report.md)
