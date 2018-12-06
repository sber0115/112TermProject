from pykinect2 import PyKinectV2
from pykinect2.PyKinectV2 import *
from pykinect2 import PyKinectRuntime

from trackingInit import *




import ctypes, _ctypes, pygame, sys, math


if sys.hexversion >= 0x03000000:
    import _thread as thread
else:
    import thread



#a menubutton is made a sprite so it can be added to a sprite 
#group and make for easy collision detection aka hand is touching
#the respective option on the menu                                             

#sectionHeight and sectionWidth correspond to the 
#region/square in which the text will be rendered
class MenuButton(pygame.sprite.Sprite):
    #option text will change with each menu option
    #using sectionWidth and sectionHeight to avoid use of magic numbers



    #blit both of the texts onto a single text surface
    #then call self.rect on the text surface
    #avoids assignment of two rects to this MenuButton instance
    def __init__(self, optionText, screen, cx, cy, sectionWidth, sectionHeight):
        pygame.sprite.Sprite.__init__(self)

        
        self.screen = screen
       
        self.optionText = optionText

        self.font = pygame.font.SysFont("assets/Arkitech_Bold.ttf", 85)

        (self.screenWidth, self.screenHeight) = (screen.get_width(), screen.get_height())
        
        self.textSurface = pygame.Surface((self.screenWidth, self.screenHeight), pygame.SRCALPHA, 32)
        
        #these are used to get the appropriate rect after rendering
        self.rectHeight = 0
        self.rectWidth = 0

        #initializing whiteSpace variable and will be used to add 
        #appropriate white space for rendering
        vWhiteSpace = 0

        for subLine in self.optionText.splitlines():
            text = self.font.render(subLine, True, (255,255,255))
            (textWidth, textHeight) = text.get_size()


            if textWidth > self.rectWidth:
                self.rectWidth = textWidth

            self.rectHeight += textHeight

            textPosition = (cx - textWidth/2, cy - textHeight + vWhiteSpace)
            self.textSurface.blit(text, textPosition)


            vWhiteSpace = textHeight

        self.image = pygame.Surface((self.rectWidth, self.rectHeight), pygame.SRCALPHA, 32)


        self.rect = self.image.get_rect()

        (self.rect.x, self.rect.y) = (cx - self.image.get_width()/2, cy - self.image.get_height()/2)

        #print("corner point", self.rect.x, self.rect.y)
        #print("rect dimensions", self.image.get_width(), self.image.get_height())

        self.screen.blit(self.image, self.rect)
        
        self.screen.blit(self.textSurface, (0,0))


                  
#would have to have the join data as attributes and shit
#refer to those attributes when calling functions like detectCollision and stuff
class Hand(pygame.sprite.Sprite):
    def __init__(self, joints, jointPoints, jointPart, handImage):

        self.image = handImage

        self.jointPart = jointPart

        pygame.sprite.Sprite.__init__(self)
        
        self.rect = self.image.get_rect()

        (self.rect.x, self.rect.y) = (int(jointPoints[jointPart].x * (1/2) - self.image.get_width()/2), \
                                        int(jointPoints[jointPart].y * (1/2) - self.image.get_height()/2))


        self.mask = pygame.mask.from_surface(self.image)


        if jointPart == PyKinectV2.JointType_HandLeft:
            self.image = pygame.transform.flip(self.image, True, False)

           

    def draw(self, frameSurface):
        #need to keep track of appropriate rect so it's rendered with twice the rect 
        #so it actually lines up
        frameSurface.blit(self.image, (self.rect.x * 2, self.rect.y * 2))
        


    #use sprite/group attributes here to appropriately 
    #check for collision and stuff
    #the hands are a member of body so have to pass it in
    def detectSelection(self, menuButtonSprites, body):
        handToCheck = None

        if self.jointPart == PyKinectV2.JointType_HandRight:
            handToCheck = body.hand_right_state
        else:
            handToCheck = body.hand_left_state


        for button in menuButtonSprites:
            if pygame.sprite.collide_rect(self, button) and handToCheck == 3:
                print("hand closing worked")
                return (True, button.optionText)
                



class startScreenRuntime(trackingRuntime):
    def __init__(self):
        pygame.init()

        super().__init__()
        

        #menu background onto the screen
        self.background = pygame.image.load("assets/menu.png")

        self.hand = pygame.image.load("assets/robotHand.png")
      
       
        self.background = pygame.transform.scale(self.background,(960,540)).convert_alpha()

        self.buttonsGroup = pygame.sprite.Group()

        
        #just rendering buttons in the appropriate locations
        self.buttonsGroup.add(MenuButton("Miror\nMode", self.background, self.screenWidth/4, self.screenHeight/4,\
                                                                    self.screenWidth/2, self.screenHeight/2))
        self.buttonsGroup.add(MenuButton("Party\nMode", self.background, self.screenWidth*(3/4), self.screenHeight/4,\
                                                                     self.screenWidth/2, self.screenHeight/2))
        self.buttonsGroup.add(MenuButton("Path\nMode", self.background, self.screenWidth/4, self.screenHeight*(3/4), \
                                                                     self.screenWidth/2, self.screenHeight/2))
        self.buttonsGroup.add(MenuButton("Mimic\nMode", self.background, self.screenWidth*(3/4), \
                                            self.screenHeight*(3/4), self.screenWidth/2, self.screenHeight/2))


        self.hasToChange = False
        self.screenChange = ""


           
    def changeScreen(self):
        print("gets to command")
        if self.screenChange == "Path\nMode":
            print("got the correct string")

        
        

       
    def run(self):
        # -------- Main Program Loop -----------
        while not self._done and not self.hasToChange:

            # --- Main event loop
            for event in pygame.event.get(): # User did something
                if event.type == pygame.QUIT: # If user clicked close
                    self._done = True # Flag that we are done so we exit this loop
            


            # --- Cool! We have a body frame, so can get skeletons
            if self._kinect.has_new_body_frame(): 
                self._bodies = self._kinect.get_last_body_frame()


            if self._bodies is not None:


                self.handGroup = pygame.sprite.Group()
               
             
                for i in range(0, self._kinect.max_body_count):
                    body = self._bodies.bodies[i]
                    if not body.is_tracked: 
                        
                        continue 

                    

                    joints = body.joints                    

                    # convert joint coordinates to color space 
                    joint_points = self._kinect.body_joints_to_color_space(joints)
                     
                  
                    #render both hands if body is detected
                    self.handGroup.add(Hand(joints, joint_points, PyKinectV2.JointType_HandRight, self.hand))
                    self.handGroup.add(Hand(joints, joint_points, PyKinectV2.JointType_HandLeft, self.hand))


                    for hand in self.handGroup:
                        hand.draw(self._frame_surface)

                        detection = hand.detectSelection(self.buttonsGroup, body)
  
                        if detection != None:
                            (self.hasToChange, self.screenChange) = detection 


            self._screen.blit(self.background,(0,0))

            
            h_to_w = float(self._frame_surface.get_height()) / self._frame_surface.get_width()
            target_height = int(h_to_w * self._screen.get_width())

            surface_to_draw = pygame.transform.scale(self._frame_surface, (self._screen.get_width(), target_height));
           
            self._screen.blit(surface_to_draw, (0,0))

               

            surface_to_draw = None
            


            #this essentially clears the surface
            self._frame_surface.fill((100,100,100,1))


            pygame.display.update()


            # --- Go ahead and update the screen with what we've drawn.
            pygame.display.flip()

            # --- Limit to 60 frames per second
            self._clock.tick(60)

        print("gets to the outside")
        if self.hasToChange:
            self.changeScreen()

        # Close our Kinect sensor, close the window and quit.
        self._kinect.close()
        pygame.quit()


game = startScreenRuntime()
game.run()