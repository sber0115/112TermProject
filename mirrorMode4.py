#mirror mode should inherit funcitonality from the tracking logic
#the tracking logic should remain different from the tracking screenitself
#aka whatever is rendered using the tracking logic 

from pykinect2 import PyKinectV2
from pykinect2.PyKinectV2 import *
from pykinect2 import PyKinectRuntime
from sceneManager import SceneBase
from trackScreen4 import trackingRuntime

import ctypes, _ctypes, pygame, sys, math, time



if sys.hexversion >= 0x03000000:
    import _thread as thread
else:
    import thread


class mirrorModeRuntime(trackingRuntime):
    def __init__(self):
        pygame.init()
        super().__init__()
        

        (self.initialZ, self.currentZ) = (0,0)
        (self.initialX, self.currentX) = (0,0)
        (self.initialY, self.currentY) = (0,0)
        (self.zBarrier, self.withinZBarrier) = (0.03, False)
        (self.xBarrier, self.withinXBarrier) = (0.03, False)
        #(self.yBarrier, self.withinYBarrier) = ()

        (self.startMove, self.endMove) = (0,0)


       
    def run(self):
        # -------- Main Program Loop -----------
        while not self._done:


            #testingStuff = PyKinectV2.


        
            # --- Main event loop
            for event in pygame.event.get(): # User did something
                if event.type == pygame.QUIT: # If user clicked close
                    self._done = True # Flag that we are done so we exit this loop

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

                    #print("joint orientations", body.joint_orientations)




                    joints = body.joints 

                    orientations = body.joint_orientations

                    self.orientation = orientations[PyKinectV2.JointType_SpineMid].Orientation


                    vectorComponents = [self.orientation.x, self.orientation.y, self.orientation.z, self.orientation.w]

                    #print(vectorComponents)

                    rotation = super().calculateRotation(vectorComponents)

                    print("this is the angle", rotation)



                    #************************************************************
                    #this gets the z-distance from the middle of the kinect sensor
                    self.currentX = joints[PyKinectV2.JointType_SpineBase].Position.x
                    self.currentY = joints[PyKinectV2.JointType_SpineBase].Position.y
                    self.currentZ = joints[PyKinectV2.JointType_SpineBase].Position.z

                  


                    #have to have it as condtional because values reset every while loop 
                    #iteration

                    if math.isclose(abs(self.initialZ - self.currentZ), self.zBarrier, rel_tol = .5):
                        
                        font = pygame.font.SysFont("comicsansms", 72)

                        #serialStuff.moveBackward()

                        if self.initialZ - self.currentZ > 0:

                            text = font.render("Moving forward", True, (0, 128, 0))
                        else:
                            text = font.render("Moving backward", True, (0, 128, 0))

                        self._frame_surface.blit(text,(600,200))


                        if self.startMove == 0:
                            self.withinZBarrier = True
                            self.startMove = time.time()
                            print("starting time", self.startMove)

                    else:

                        if math.isclose(abs(self.initialZ - self.currentZ), .001, rel_tol = .10) and self.withinZBarrier:
                            
                            self.endMove = time.time()

                            print("ending time", self.endMove)

                            print("Duration of move", self.endMove - self.startMove)

                            self.withinZBarrier = False
                            self.startMove = 0
                            
                    

                    

                       

                    """elif -.05 < self.currentZ - self.initialZ < -.01:
                        font = pygame.font.SysFont("comicsansms", 72)
                        text = font.render("Moving forward", True, (0, 128, 0))

                        #serialStuff.moveForward()

                        self._frame_surface.blit(text,(600,200))"""

                   
                    
                    """if .02 < self.currentX - self.initialX < .06:
                        font = pygame.font.SysFont("comicsansms", 72)

                        #serialStuff.turnLeft()
                        text = font.render("Moving left", True, (255, 0, 0))
                        self._frame_surface.blit(text,(600,200))


                    elif -.06 < self.currentX - self.initialX < -.02:
                        font = pygame.font.SysFont("comicsansms", 72)
                        text = font.render("Moving right", True, (255, 0, 0))
                        #serialStuff.turnRight()

                        self._frame_surface.blit(text,(600,200))"""
                    
                   


                    joint_points = self._kinect.body_joints_to_color_space(joints)



            h_to_w = float(self._frame_surface.get_height()) / self._frame_surface.get_width()
            target_height = int(h_to_w * self._screen.get_width())
            surface_to_draw = pygame.transform.scale(self._frame_surface, (self._screen.get_width(), target_height));
            self._screen.blit(surface_to_draw, (0,0))
            surface_to_draw = None


            ##updating the distance attributes
            self.initialZ = self.currentZ
            self.initialX  = self.currentX
            self.currentY = self.currentY


            pygame.display.update()

            # --- Go ahead and update the screen with what we've drawn.
            pygame.display.flip()

            # --- Limit to 60 frames per second
            self._clock.tick(60)

        # Close our Kinect sensor, close the window and quit.
        self._kinect.close()
        pygame.quit()



game = mirrorModeRuntime();
game.run();

