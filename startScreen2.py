from pykinect2 import PyKinectV2
from pykinect2.PyKinectV2 import *
from pykinect2 import PyKinectRuntime
from sceneManager import SceneBase


import ctypes
import _ctypes
import pygame
import sys
import math


if sys.hexversion >= 0x03000000:
    import _thread as thread
else:
    import thread


class startScreenRuntime(SceneBase):
    def __init__(self):
        pygame.init()
        SceneBase.__init__(self)

        pygame.display.set_caption('Robo Dance Club')

        # Used to manage how fast the screen updates
        self._clock = pygame.time.Clock()


        self._screen = pygame.display.set_mode((960,540))

        # Loop until the user clicks the close button.
        self._done = False



        # Kinect runtime object, we want only color and body frames 
        self._kinect = PyKinectRuntime.PyKinectRuntime(PyKinectV2.FrameSourceTypes_Color | PyKinectV2.FrameSourceTypes_Body)


      
        # here we will store skeleton data 
        self._bodies = None


        #****************************** menu background onto the screen
        self.background = pygame.image.load("images/menu.png")

        self.background = pygame.transform.scale(self.background,(960,540))
        #*********************************************************************


        #*************************should draw circles where your hands are on the menu
    def drawCirclesOnHands(self, joints, jointPoints, color, joint1):
        joint1State = joints[joint1].TrackingState

        end = (int(jointPoints[joint1].x), int(jointPoints[joint1].y))

        print(end)

        pygame.draw.circle(self.background, color, end, 40)
   

    #*******************************************************************************************************


       
    def run(self):
        # -------- Main Program Loop -----------
        while not self._done:
        
            # --- Main event loop
            for event in pygame.event.get(): # User did something
                if event.type == pygame.QUIT: # If user clicked close
                    self._done = True # Flag that we are done so we exit this loop
            

            
            self._screen.blit(self.background, (0,0))
         
            
            # --- Cool! We have a body frame, so can get skeletons
            if self._kinect.has_new_body_frame(): 
                self._bodies = self._kinect.get_last_body_frame()


            if self._bodies is not None: 
             
                for i in range(0, self._kinect.max_body_count):
                    body = self._bodies.bodies[i]
                    if not body.is_tracked: 
                        continue 


                    joints = body.joints                    


                    #************************************************************
                    # convert joint coordinates to color space 
                    joint_points = self._kinect.body_joints_to_color_space(joints)
                     
                    self.drawCirclesOnHands(joints,joint_points,(0,0,255), PyKinectV2.JointType_HandRight)
                  
      


            pygame.display.update()

            # --- Go ahead and update the screen with what we've drawn.
            pygame.display.flip()

            # --- Limit to 60 frames per second
            self._clock.tick(60)

        # Close our Kinect sensor, close the window and quit.
        self._kinect.close()
        pygame.quit()



game = startScreenRuntime();
game.run();

