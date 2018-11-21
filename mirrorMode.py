#mirror mode should inherit funcitonality from the tracking logic
#the tracking logic should remain different from the tracking screenitself
#aka whatever is rendered using the tracking logic 

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


class MirroringRuntime(SceneBase):
    def __init__(self):
        pygame.init()
        SceneBase.__init__(self)

        pygame.display.set_caption('Robo Dance Club')

        # Used to manage how fast the screen updates
        self._clock = pygame.time.Clock()

        # Set the width and height of the screen [width, height]
        self._infoObject = pygame.display.Info()
        self._screen = pygame.display.set_mode((self._infoObject.current_w >> 1, self._infoObject.current_h >> 1), 
                                               pygame.HWSURFACE|pygame.DOUBLEBUF|pygame.RESIZABLE, 32)

        # Loop until the user clicks the close button.
        self._done = False


        # Kinect runtime object, we want only color and body frames 
        self._kinect = PyKinectRuntime.PyKinectRuntime(PyKinectV2.FrameSourceTypes_Color | PyKinectV2.FrameSourceTypes_Body)

        # back buffer surface for getting Kinect color frames, 32bit color, width and height equal to the Kinect color frame size
        self._frame_surface = pygame.Surface((self._kinect.color_frame_desc.Width, self._kinect.color_frame_desc.Height), 0, 32)

        # here we will store skeleton data 
        self._bodies = None


        #**********************************
        #initializing distance as zero and then updating it
        #at the end of every screen refresh

        #use screenWidth and screenHeight in the SceneBase functions that are being overwritten
        (self.screenWidth, self.screenHeight) = pygame.display.get_surface().get_size()
        print(self.screenWidth, self.screenHeight)
        self.initialDistance = 0
        self.distance = 0
        #****************************************



    #*********************************
    #this function draws circles at the locations of the hands --> going to be used later as indicators of 
    #menu selection and stuff


    #replace with robot hands eventually when implementing same functionality in the startScreen
    def drawCirclesOnHands(self, joints, jointPoints, color, joint1):
     
        joint1State = joints[joint1].TrackingState

        end = (int(jointPoints[joint1].x), int(jointPoints[joint1].y))

        pygame.draw.circle(self._frame_surface, color, end, 40)


    def returnToMenu():
        pass


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

                elif event.type == pygame.VIDEORESIZE: # window resized
                    self._screen = pygame.display.set_mode(event.dict['size'], 
                                               pygame.HWSURFACE|pygame.DOUBLEBUF|pygame.RESIZABLE, 32)
                    

           

            # --- Game logic should go here

            # --- Getting frames and drawing  
            # --- Woohoo! We've got a color frame! Let's fill out back buffer surface with frame's data 
            if self._kinect.has_new_color_frame():
                frame = self._kinect.get_last_color_frame()
                self.draw_color_frame(frame, self._frame_surface)
                frame = None

            # --- Cool! We have a body frame, so can get skeletons
            if self._kinect.has_new_body_frame(): 
                self._bodies = self._kinect.get_last_body_frame()

            # --- draw skeletons to _frame_surface
            if self._bodies is not None: 
             
                for i in range(0, self._kinect.max_body_count):
                    body = self._bodies.bodies[i]
                    if not body.is_tracked: 
                        continue 


                    joints = body.joints 


                    #************************************************************
                    #this gets the z-distance from the middle of the kinect sensor
                    self.distance = joints[PyKinectV2.JointType_SpineBase].Position.z
                    


                    #using these magic numbers because small changes
                    #in the z position can occur even while standing still
                    if .02 < self.distance - self.initialDistance < .06:
                        font = pygame.font.SysFont("comicsansms", 72)
                        text = font.render("Moving backward", True, (0, 128, 0))
                        self._frame_surface.blit(text,(600,200))
                     

                    elif -.06 < self.distance - self.initialDistance < -.02:
                        font = pygame.font.SysFont("comicsansms", 72)
                        text = font.render("Moving forward", True, (0, 128, 0))
                        self._frame_surface.blit(text,(600,200))


                    #************************************************************
                    
                    
                    # convert joint coordinates to color space 
                    joint_points = self._kinect.body_joints_to_color_space(joints)

                    
                    #self.draw_body(joints, joint_points, SKELETON_COLORS[i])

                    self.drawCirclesOnHands(joints, joint_points, (0,0,255), PyKinectV2.JointType_HandRight)

                    self.drawCirclesOnHands(joints, joint_points, (0,0,255),  PyKinectV2.JointType_HandLeft)
                    

                    #************************************************* 
                    ##hand states are enumerated --> 3 is closed
                    #MOVE THIS TO TRACKING MODE WHEN FINSIHED WITH THIS FILE
                    if body.hand_right_state == 3:
                 
                        font = pygame.font.SysFont("comicsansms", 72)
                        text = font.render("The right hand was closed", True, (0, 128, 0))
                        self._frame_surface.blit(text,(600,200))

                    if body.hand_left_state == 3:
                 
                        font = pygame.font.SysFont("comicsansms", 72)
                        text = font.render("The left hand was closed", True, (0, 128, 0))
                        self._frame_surface.blit(text,(100,200))
                    #*******************************************************************
         

            # --- copy back buffer surface pixels to the screen, resize it if needed and keep aspect ratio
            # --- (screen size may be different from Kinect's color frame size) 
            h_to_w = float(self._frame_surface.get_height()) / self._frame_surface.get_width()
            target_height = int(h_to_w * self._screen.get_width())
            surface_to_draw = pygame.transform.scale(self._frame_surface, (self._screen.get_width(), target_height));
            self._screen.blit(surface_to_draw, (0,0))
            surface_to_draw = None

            ##updating that distance attribute
            self.initialDistance = self.distance

            pygame.display.update()

            # --- Go ahead and update the screen with what we've drawn.
            pygame.display.flip()

            # --- Limit to 60 frames per second
            self._clock.tick(60)

        # Close our Kinect sensor, close the window and quit.
        self._kinect.close()
        pygame.quit()



game = MirroringRuntime();
game.run();

