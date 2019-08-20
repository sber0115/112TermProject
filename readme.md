# Motion Controlled Car

# Project Description:

This is a pretty cool robot car that dances with you. It's powered by an Arduino that has a blutetooth module on it; I'm using serial communication to be able to send commands to it. It'll miror your movements and orientation (as long as you don't turn a complete 180 degrees) while in mirrorMode. There's a cool starting screen in which you can feel like a robot yourself. In path mode, a canvas is at your disposal; you'll be able to draw out a linear path that the robot will follow as soon as you close your left hand.

# Running the Project:

Unfortunately I wasn't able to get mode transitions working; pretty sure the problem had to do with initialization of multiple screens because trackingRuntime was a superclass.

You can run each "screen" individually by just executing the mode files like "startScreen" and "pathMode". "MirrorMode" works as well.  

[![Youtube Video Thumbnail](https://img.youtube.com/vi/x6Naf4uirCo/0.jpg)](https://www.youtube.com/watch?v=x6Naf4uirCo)

# Libraries that need to be installed:
pyserial
pygame
pykinect2

for installation of pykinect2 refer to Fletcher's guide 
--> https://github.com/sebastianBernal0115/kinect_python

or refer to this
--> https://github.com/Kinect/PyKinect2

for pyserial installation 
--> https://pypi.org/project/pyserial/

pip install pyserial through the terminal while having admin rights

for pygame installation
-->

would've used the module manager but this worked fine
