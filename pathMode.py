#####copied code from the start screen --> this updating scheme can be used for the drawing path stuff
#to keep the drawn path on the screen --> don't reset the surface with the drawn circles on it at the end
#of the long while loop

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


        #self._screen = pygame.display.set_mode((960,540))

        
        # Set the width and height of the screen [width, height]
        self._infoObject = pygame.display.Info()
        self._screen = pygame.display.set_mode((self._infoObject.current_w >> 1, self._infoObject.current_h >> 1), 
                                               pygame.HWSURFACE|pygame.DOUBLEBUF|pygame.RESIZABLE, 32)


        # Loop until the user clicks the close button.
        self._done = False

      


        # Kinect runtime object, we want only color and body frames 
        self._kinect = PyKinectRuntime.PyKinectRuntime(PyKinectV2.FrameSourceTypes_Color | PyKinectV2.FrameSourceTypes_Body)


        
        self._frame_surface = pygame.Surface((self._kinect.color_frame_desc.Width, self._kinect.color_frame_desc.Height), pygame.SRCALPHA, 32)
        self._frame_surface = self._frame_surface.convert_alpha()


        # here we will store skeleton data 
        self._bodies = None

        #****************************** menu background onto the screen
        self.background = pygame.image.load("images/menu.png")

        self.background = pygame.transform.scale(self.background,(940,540))
        #*********************************************************************


        #*************************should draw circles where your hands are on the menu
    def drawCirclesOnHands(self, joints, jointPoints, color, joint1):
        joint1State = joints[joint1].TrackingState

        end = (int(jointPoints[joint1].x), int(jointPoints[joint1].y))

        print(end)

        pygame.draw.circle(self._frame_surface, color, end, 40)
    #*******************************************************************************************************



    def draw_color_frame(self, frame, target_surface):
        target_surface.lock()
        address = self._kinect.surface_as_array(target_surface.get_buffer())
        ctypes.memmove(address, frame.ctypes.data, frame.size)
        del address
        target_surface.unlock()




       
    def run(self):
        # -------- Main Program Loop -----------
        while not self._done:
        
            # --- Main event loop
            for event in pygame.event.get(): # User did something
                if event.type == pygame.QUIT: # If user clicked close
                    self._done = True # Flag that we are done so we exit this loop
            

            
            
            """if self._kinect.has_new_color_frame():
                            frame = self._kinect.get_last_color_frame()
                            self.draw_color_frame(frame, self._frame_surface)
                            frame = None"""

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
                     
                    self.drawCirclesOnHands(joints,joint_points,(0,0,100), PyKinectV2.JointType_HandRight)
                    self.drawCirclesOnHands(joints,joint_points,(0,0,100), PyKinectV2.JointType_HandLeft)
            

            self._screen.blit(self.background, (0,0))

           

            h_to_w = float(self._frame_surface.get_height()) / self._frame_surface.get_width()
            target_height = int(h_to_w * self._screen.get_width())
            surface_to_draw = pygame.transform.scale(self._frame_surface, (self._screen.get_width(), target_height));
            self._screen.blit(surface_to_draw, (0,0))

           

            surface_to_draw = None
      


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


