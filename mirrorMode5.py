from trackingInit import *
from userAndRobot import *


import ctypes, _ctypes, pygame, sys, math, time



if sys.hexversion >= 0x03000000:
    import _thread as thread
else:
    import thread


class mirrorModeRuntime(trackingRuntime):
    def __init__(self):
        pygame.init()
        super().__init__()  
        

     
    def run(self):
        # -------- Main Program Loop -----------

        robot = Robot()

        #parameters to set initial and current 
        user = User()


        while not self._done:



            for event in pygame.event.get(): 
                if event.type == pygame.QUIT: 
                    self._done = True 

                elif event.type == pygame.VIDEORESIZE: # window resized
                    self._screen = pygame.display.set_mode(event.dict['size'], 
                                               pygame.HWSURFACE|pygame.DOUBLEBUF|pygame.RESIZABLE, 32)
                    

           
            if self._kinect.has_new_color_frame():
                frame = self._kinect.get_last_color_frame()
                self.draw_color_frame(frame, self._frame_surface)
                frame = None

          
            if self._kinect.has_new_body_frame(): 
                self._bodies = self._kinect.get_last_body_frame()

          
            if self._bodies is not None: 
             
                for i in range(0, self._kinect.max_body_count):
                    body = self._bodies.bodies[i]
                    if not body.is_tracked: 
                        continue 

                    joints = body.joints 


                    #body only exists in this while loop if body is detected
                    #so put orientation stuff here
                    orientations = body.joint_orientations

                    user.orientation = orientations[PyKinectV2.JointType_SpineMid].Orientation


                    vectorComponents = [user.orientation.x, user.orientation.y, user.orientation.z, user.orientation.w]


                    #finds the yaw rotation of the mid spine joint
                    user.calculateRotation(vectorComponents)

                    user.rotationHandling(robot)

                    #this gets the z-distance from the middle of the kinect sensor
                    user.currentX = joints[PyKinectV2.JointType_SpineBase].Position.x
                    user.currentZ = joints[PyKinectV2.JointType_SpineBase].Position.z


                    joint_points = self._kinect.body_joints_to_color_space(joints)


                    #if either of these durations return none then the user is moving
                    #in the other "direction", either front/back or side to side
                    moveTime = user.movementHandling()


                    if moveTime != None:
                        robot.displacementCommand(moveTime)
                        robot.executeCommand()
                        


                    

            h_to_w = float(self._frame_surface.get_height()) / self._frame_surface.get_width()
            target_height = int(h_to_w * self._screen.get_width())
            surface_to_draw = pygame.transform.scale(self._frame_surface, (self._screen.get_width(), target_height));
            self._screen.blit(surface_to_draw, (0,0))
            surface_to_draw = None


            ##updating the user distance attributes
            user.initialZ = user.currentZ
            user.initialX  = user.currentX
            


            pygame.display.update()

            # --- Go ahead and update the screen with what we've drawn.
            pygame.display.flip()

            # --- Limit to 60 frames per second
            self._clock.tick(60)

        # Close our Kinect sensor, close the window and quit.
        self._kinect.close()
        pygame.quit()

game = mirrorModeRuntime()
game.run()
