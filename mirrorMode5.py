#mirror mode should inherit funcitonality from the tracking logic
#the tracking logic should remain different from the tracking screenitself
#aka whatever is rendered using the tracking logic 

from pykinect2 import PyKinectV2
from pykinect2.PyKinectV2 import *
from pykinect2 import PyKinectRuntime
from sceneManager import SceneBase
from trackScreen4 import trackingRuntime

import ctypes, _ctypes, pygame, sys, math, time, serialStuff



if sys.hexversion >= 0x03000000:
    import _thread as thread
else:
    import thread


class mirrorModeRuntime(trackingRuntime):
    def __init__(self):
        pygame.init()
        super().__init__()


        #used in condtionals for movement handling
        #change them whenever certain commands are executed

        #first element to check whether turned and 
        #the string specifies the direction turned in
        self.userTurned = [False, ""]
        self.robotTurned = [False, ""]
        

        #used to track changes in position
        (self.initialZ, self.currentZ) = (0,0)
        (self.initialX, self.currentX) = (0,0)
     

        #average change in position and boolen for whether or not player had already started moving
        (self.barrier, self.withinBarrier) = (0.03, False)
        
         
        #to keep track of the movement's duration 
        (self.startMove, self.endMove) = (0,0)


        self.moveDuration = 0


        #build up the string and when it needs to be sent to the arduino
        #then add the start and end markers 
        self.commandString = ""



    def rotationHandling():
        pass 





    def movementHandling(self, initialVal, currentVal, userRotated):
        direction = None

        #this is about the average change in distance from sensor 
        #that elicits movement forward and backward
        if math.isclose(abs(initialVal - currentVal), self.barrier, rel_tol = .5):
                 
            if initialVal - currentVal > 0:
                #all motors going to be going forward in arduino code
                direction = "backward"
               
            else:
                #all motors going to be going backward in arduino code
                direction = "forward"
                

            #detecting the start of some movement aka when user in within some movement "speed"
            if self.startMove == 0:
             
                self.withinBarrier = True
                self.startMove = time.time()
                           
        else:

            #if the user is still after having started moving
            if math.isclose(abs(initialVal - currentVal), .001, rel_tol = .10) and self.withinBarrier:
                            
                self.endMove = time.time()

                if direction == "forward":
                    self.commandString += "11"
                else:
                    self.commandString += "00"

                timeToReturn = self.endMove - self.startMove

                self.withinBarrier = False
                self.startMove = 0

                #return the duration of the move
                return timeToReturn



    def sendCommand(self):

        #what I found to be the average time to walk/travel one meter
        #away or toward the sensor
        meterDuration = 2.387

        #an arduino delay equivalent to travel one meter
        #is about 1200 ms aka 1.2s


        #distance arduino should travel some ratio of this delay regardless if 
        #user traveled more an a meter or not
        travelRatio = self.moveDuration / meterDuration

        if travelRatio > 1:
            leftOver = self.moveDuration - meterDuration
            travelRatio = 1 + (leftOver / meterDuration)

        motorDelay = 1200 * travelRatio

        self.commandString += str(int(motorDelay))

        #inserting the start and end markers in the command string
        self.commandString = "<" + self.commandString
        self.commandString += ">"



        print("String that got sent", self.commandString)
        serialStuff.testing(self.commandString)


        #reset commandString after movements
        self.commandString = ""




                            
       
    def run(self):
        # -------- Main Program Loop -----------
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

                    orientations = body.joint_orientations

                    self.orientation = orientations[PyKinectV2.JointType_SpineMid].Orientation


                    vectorComponents = [self.orientation.x, self.orientation.y, self.orientation.z, self.orientation.w]

                    #print(vectorComponents)

                    rotation = super().calculateRotation(vectorComponents)

                    """print("this is the angle", rotation)

                    if -1 <= rotation <= 10:
                        print("looking straight ahead")

                    elif 40 <= rotation <= 65:
                        #serialStuff.turnRight()
                        print("facing right")

                    elif -75 <= rotation <= -40:
                        #serialStuff.turnLeft()
                        print("facing left")
                        """


                    #************************************************************
                    #this gets the z-distance from the middle of the kinect sensor
                    self.currentX = joints[PyKinectV2.JointType_SpineBase].Position.x
                    self.currentY = joints[PyKinectV2.JointType_SpineBase].Position.y
                    self.currentZ = joints[PyKinectV2.JointType_SpineBase].Position.z


                    joint_points = self._kinect.body_joints_to_color_space(joints)


                    self.moveDuration = self.movementHandling(self.initialZ, self.currentZ)


                    if self.moveDuration != None:

                        print("duration was", self.moveDuration)
                        self.sendCommand()

                        #execute the robot movement here


            h_to_w = float(self._frame_surface.get_height()) / self._frame_surface.get_width()
            target_height = int(h_to_w * self._screen.get_width())
            surface_to_draw = pygame.transform.scale(self._frame_surface, (self._screen.get_width(), target_height));
            self._screen.blit(surface_to_draw, (0,0))
            surface_to_draw = None


            ##updating the distance attributes
            self.initialZ = self.currentZ
            self.initialX  = self.currentX
            


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

