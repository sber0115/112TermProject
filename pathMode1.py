#####copied code from the start screen --> this updating scheme can be used for the drawing path stuff
#to keep the drawn path on the screen --> don't reset the surface with the drawn circles on it at the end
#of the long while loop

from pykinect2 import PyKinectV2
from pykinect2.PyKinectV2 import *
from pykinect2 import PyKinectRuntime
from sceneManager import SceneBase
from trackScreen4 import trackingRuntime



import ctypes, _ctypes, pygame, sys, math


if sys.hexversion >= 0x03000000:
    import _thread as thread
else:
    import thread




class startScreenRuntime(trackingRuntime):
    def __init__(self):
        pygame.init()
        super().__init__()


        #surface to be drawn on for path mode
        self.pathScreen = pygame.Surface((self.screenWidth, self.screenHeight), pygame.SRCALPHA, 32)
        self.pathScreen.fill((255,255,255))


    def drawCirclesOnHands(self, joints, jointPoints, color, jointPart, body):

        print("should be drawn")
        end = (int(jointPoints[jointPart].x / 2), int(jointPoints[jointPart].y / 2))

        pygame.draw.circle(self.pathScreen, color, end, 25)
   


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
            
 
            if self._kinect.has_new_color_frame():
                            frame = self._kinect.get_last_color_frame()
                            self.draw_color_frame(frame, self._frame_surface)
                            frame = None

            # --- Cool! We have a body frame, so can get skeletons
            if self._kinect.has_new_body_frame(): 
                self._bodies = self._kinect.get_last_body_frame()


            if self._bodies is not None: 
             
                for i in range(0, self._kinect.max_body_count):
                    body = self._bodies.bodies[i]
                    if not body.is_tracked: 
                        continue 


                    joints = body.joints                    

                    joint_points = self._kinect.body_joints_to_color_space(joints)
                     

                    #draw with right hand and use left hand to signal end of line
                    if body.hand_right_state == 3:
                        self.drawCirclesOnHands(joints,joint_points,(0,0,255), PyKinectV2.JointType_HandRight, body)
 



            h_to_w = float(self._frame_surface.get_height()) / self._frame_surface.get_width()
            target_height = int(h_to_w * self._screen.get_width())
            surface_to_draw = pygame.transform.scale(self._frame_surface, (self._screen.get_width(), target_height));


            #self._screen.blit(surface_to_draw, (0,0))


            self._screen.blit(self.pathScreen,(0,0))


            
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


