from setuptools import find_packages, setup
import os
from glob import glob

package_name = 'shape_detector'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ("share/ament_index/resource_index/packages",
         ["resource/" + package_name]),
        ("share/" + package_name, ["package.xml"]),
        (os.path.join("share", package_name, "launch"),
         glob(os.path.join("launch", "*.launch.py"))),
        (os.path.join("share", package_name, "videos"),
         glob(os.path.join(package_name, "*.mp4"))),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='finn-gilligan',
    maintainer_email='finn-gilligan@todo.todo',
    description='TODO: Package description',
    license='TODO: License declaration',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            'hello_node = shape_detector.hello:main',
            'video_publisher = shape_detector.video_publisher:main',
            'image_subscriber = shape_detector.image_subscriber:main',
        ],
    },
)
