import serial, math, time


arduinoSerialData = serial.Serial('COM20',9600)


#made it a global player so it's modifiable by user in certain situations
#and modifiable by the robot when making the actual commandString




class Robot():
   

    def __init__(self):
        self.direction = None

          #build up the string and when it needs to be sent to the arduino
        #then add the start and end markers 
        self.commandString = ""

    #move duration is a tuple containing how long the move lasted and
    #characters specifying how to move the sides of the car

    def displacementCommand(self, moveDuration):

        #what I found to be the average time to walk/travel one meter
        #away or toward the sensor
        meterDuration = 2.387

        #an arduino delay equivalent to travel one meter
        #is about 1200 ms aka 1.2s


        #distance arduino should travel some ratio of this delay regardless if 
        #user traveled more an a meter or not
        travelRatio = moveDuration[0] / meterDuration

        if travelRatio > 1:
            leftOver = moveDuration[0] - meterDuration
            travelRatio = 1 + (leftOver / meterDuration)

        motorDelay = 1200 * travelRatio


        #the 2nd element of the tuple dictates the motor directions
        self.commandString += moveDuration[1]

        self.commandString += str(int(motorDelay))

        #inserting the start and end markers in the command string
        self.commandString = "<" + self.commandString
        self.commandString += ">"



    #delay of 1200 ms corresponds to the execution of a 90 degree point turn
    #in a specified direction -> pass in the facing attribute of the user

    #since rotation command is called in rotation handling pass in rotationDirection
    #into the out function

    def executeRotation(self, rotationDirection):
        print("sent turning command")

        if rotationDirection == "right":
            self.commandString += "<10650>"
        else:
            self.commandString += "<01650>"

        self.executeCommand()



    #this is only called when an appropriate command string
    #has been created
    def executeCommand(self):
        arduinoSerialData.write(self.commandString.encode())
        #reset commandString after movements
        self.commandString = ""




#I feel like seperate class in seperate file makes the mirrorMode screen
#easier to follow

#besides this can be used for the mimicMode as well later on
class User():
 
 
    def __init__(self):
        self.direction = None
        self.facing = None


        #used in angle calculations during runtime
        self.orientation = None

        self.rotationAngle = 0

        #average change in position and boolen for whether or not player had already started moving
        (self.barrier, self.withinBarrier) = (0.03, False)

        #distance away from sensor or x displacement from center
        (self.initialZ, self.currentZ) = (0,0)
        (self.initialX, self.currentX) = (0,0)


         #to keep track of the movement's duration 
        (self.startMove, self.endMove) = (0,0)

        self.moveDuration = 0



    #calculates the rotation along the spine later on to appropriately
    #spin/turn the robot
    def calculateRotation(self, quaternion):
        value = 2.0 * (quaternion[3] * quaternion[1] - quaternion[2] * quaternion[0])

        if value > 1:
            value = 1
        elif value < -1:
            value = -1

        self.rotationAngle = math.asin(value)

        self.rotationAngle *= (180 / math.pi)

    
    #later update this function with a parameter for rotation
    #that would change how the robot handles movements
    def movementHandling(self):
        
        
        if self.facing == None:
            print(self.initialZ - self.currentZ)

        else:
            print(self.initialX - self.currentX)


        addToCommandString = ""

        if self.facing == None:
            initialVal = self.initialZ
            currentVal = self.currentZ
            print("checking Z displacement")
        else:
            initialVal = self.initialX
            currentVal = self.currentX
            print("checking X displacement")

        #this is about the average change in distance from sensor 
        #that elicits movement forward and backward
        if math.isclose(abs(initialVal - currentVal), self.barrier, rel_tol = .2):
                 
            print("started moving")
            if initialVal - currentVal < 0:
                #all motors going to be going forward in arduino code
                self.direction = "negative"
                
               
            elif initialVal - currentVal > 0:
                #all motors going to be going backward in arduino code
                self.direction = "positive"
                

            #detecting the start of some movement aka when user in within some movement "speed"
            if self.startMove == 0:
             
                self.withinBarrier = True
                self.startMove = time.time()
                           
        else:

            #if the user is still after having started moving
            if math.isclose(abs(initialVal - currentVal), 0, rel_tol = .1) and self.withinBarrier:
                print("stopped moving")
                self.endMove = time.time()

                if self.direction == "positive":
                    addToCommandString = "11"
                else:
                    addToCommandString = "00"

                timeToReturn = self.endMove - self.startMove

                self.withinBarrier = False
                self.startMove = 0
                
                #return the duration of the move
                return timeToReturn, addToCommandString




    def rotationHandling(self, other):
        if -1 <= self.rotationAngle <= 10:
            if self.facing == "right":
                #make a left turn and set facing to None
                other.executeRotation("left")
                self.facing = None
  
            elif self.facing == "left":

                #make a right turn and set facing to None
                other.executeRotation("right")
                self.facing = None

               
            print("looking straight ahead")


        elif 40 <= self.rotationAngle <= 65:
            if self.facing == None:
                self.facing = "right"
                other.executeRotation(self.facing)
                print("facing right")


        elif -75 <= self.rotationAngle <= -40:
            if self.facing == None:
                self.facing = "left"
                other.executeRotation(self.facing)
                print("facing left")


        
               



