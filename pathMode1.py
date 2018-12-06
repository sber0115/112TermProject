import serial
from trackingInit import *



arduinoSerialData = serial.Serial('COM20',9600)




import ctypes, _ctypes, pygame, sys, math


if sys.hexversion >= 0x03000000:
    import _thread as thread
else:
    import thread


class Robot():

    def __init__(self):
        self.commandString = ""
        
        self.tolerableRange = 80


 

    def move(self, start, end):
        print("getting to the move")

        #250 pixels equal to one meter change in robot's position
        #if the user draws a path that's less than or greater then
        #this then it'll move for some ratio of it

        pixelEquivalent = 450


        changeInX = start[0] - end[0]
        changeInY = start[1] - end[1]


        #this is going to make the robot move forward or back
        if abs(changeInX) <= self.tolerableRange:

            print("within range")

            movementRatio = abs(changeInY) / pixelEquivalent

            if movementRatio > 1:
                leftOver = abs(changeInY) - pixelEquivalent
                movementRatio = 1 + (leftOver / pixelEquivalent)

            #corresponds to one meter robot movement
            motorDelay = 1200 * movementRatio

            if changeInY > 0:
                print("command string set")

                self.commandString = "<11" + str(int(motorDelay)) + ">"

                print("this is the command string", self.commandString)
                self.executeCommand()

            else:
                self.commandString = "<00" + str(int(motorDelay)) + ">"
                self.executeCommand()


        elif abs(changeInY) <= self.tolerableRange:
           

            movementRatio = abs(changeInX) / pixelEquivalent

            if movementRatio > 1:
                leftOver = abs(changeInX) - pixelEquivalent
                movementRatio = 1 + (leftOver / pixelEquivalent)

            #corresponds to one meter robot movement
            motorDelay = 1200 * movementRatio

            if changeInX < 0:
                self.executeRotation("right")
                print("turned right")

            else:
                self.executeRotation("left")


            self.commandString = "<11" + str(int(motorDelay)) + ">"

            print("this is the command string", self.commandString)
            self.executeCommand()

          

        """else:
            self.calculateRotation()
            self.executeRotation()"""
        

    def executeRotation(self, rotationDirection):
   
        if rotationDirection == "right":
            self.commandString += "<10350>"
        else:
            self.commandString += "<01350>"

        self.executeCommand()


    #this is only called when an appropriate command string
    #has been created
    def executeCommand(self):
        arduinoSerialData.write(self.commandString.encode())
        #reset commandString after movements
        self.commandString = ""







class pathModeRuntime(trackingRuntime):
    def __init__(self):
        pygame.init()
        super().__init__()


        #reset the canvas when the user either specifies to reset or
        #when the user closes the left hand --> clear screen
        self.reset = False

        #coordinates of hands
        self.righHandCors = (0,0)

        self.leftHandCors = (0,0)



        #surface to be drawn on for path mode
        self.pathScreen = pygame.Surface((self.screenWidth, self.screenHeight), pygame.SRCALPHA, 32)

        self.textSurface = pygame.Surface((self.screenWidth, self.screenHeight), pygame.SRCALPHA, 32)

        self.font = pygame.font.SysFont("assets/Arkitech_Bold.ttf", 40)

        self.instructionsText = "Close right hand to start drawing path\nthen"\
                               + " close the left hand to see robot move"

        self.otherText = "To exit mode bring hands together"

        vWhiteSpace = 0
        heightMultiplier = 0


        if not self.reset:

            for subLine in self.instructionsText.splitlines():
                text = self.font.render(subLine, True, (0,0,0))
                (textWidth, textHeight) = text.get_size()

                textPosition = (self.screenWidth/2 - textWidth/2, self.screenHeight/3 - textHeight + vWhiteSpace)
                startingPosition = textPosition

                self.textSurface.blit(text, textPosition)

                heightMultiplier += 1
                vWhiteSpace = textHeight * heightMultiplier
        

            vWhiteSpace = 0

            for subLine in self.otherText.splitlines():
                text = self.font.render(subLine, True, (0,0,0))
                (textWidth, textHeight) = text.get_size()

                textPosition = (self.screenWidth/2 - textWidth/2, self.screenHeight * \
                                                                    (3/4) + vWhiteSpace)

                print(textPosition)
                self.textSurface.blit(text, textPosition)

                vWhiteSpace = textHeight



        self.pathScreen.fill((255,255,255))

        self.initialModeStart = False

        #store x and y coordinates of right hand once path drawing starts 
        self.pathStart = []

        self.pathEnd = []

        self.pathStarted = False



    #other is robot instance
    def pathHandling(self, joints, jointPoints, color, rightHand, leftHand, body, other):
       self.rightHandCors = [int(jointPoints[rightHand].x / 2), int(jointPoints[rightHand].y / 2)]

       if body.hand_right_state == 3:
            if not self.initialModeStart:
                self.initialModeStart = not self.initialModeStart

            if not self.pathStarted:
                self.pathStarted = not self.pathStarted
                self.pathStart = self.rightHandCors
                print("path started at", self.pathStart)
            
            self.pathEnd = self.rightHandCors
            pygame.draw.circle(self.pathScreen, color, self.rightHandCors, 10)


       if body.hand_left_state == 3:
            if self.pathStarted:
                other.move(self.pathStart, self.pathEnd)
                print("the ending coordinate was", self.pathEnd)
                self.reset = True
                self.pathStarted = False



       
    def run(self):

        robot = Robot()


        # -------- Main Program Loop -----------
        while not self._done:

            if self.reset:
                self.pathScreen.fill((255,255,255))
                self.reset = False

        
            # --- Main event loop
            for event in pygame.event.get(): # User did something
                if event.type == pygame.QUIT: # If user clicked close
                    self._done = True # Flag that we are done so we exit this loop
   

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
                    
                    self.pathHandling(joints, joint_points, (0,0,255), PyKinectV2.JointType_HandRight, \
                                                                        PyKinectV2.JointType_HandLeft, body, robot)
 
           
            self._screen.blit(self.pathScreen,(0,0))


            if not self.initialModeStart:
                self._screen.blit(self.textSurface,(0,0))


            pygame.display.update()

            # --- Go ahead and update the screen with what we've drawn.
            pygame.display.flip()

            # --- Limit to 60 frames per second
            self._clock.tick(60)

        # Close our Kinect sensor, close the window and quit.
        self._kinect.close()
        pygame.quit()



game = pathModeRuntime()
game.run()
