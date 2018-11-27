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



#a menubutton is made a sprite so it can be added to a sprite 
#group and make for easy collision detection aka hand is touching
#the respective option on the menu                                             

#sectionHeight and sectionWidth correspond to the 
#region/square in which the text will be rendered
class MenuButton(pygame.sprite.Sprite):
    #option text will change with each menu option
    #using sectionWidth and sectionHeight to avoid use of magic numbers

    def __init__(self, optionText, screen, cx, cy, sectionWidth, sectionHeight):
        pygame.sprite.Sprite.__init__(self)
     

        font = pygame.font.SysFont("comicsansms", 85)
        
        #initializing whiteSpace variable and will be used to add 
        #appropriate white space for rendering
        vWhiteSpace = 0

        for subLine in optionText.splitlines():
            text = font.render(subLine, True, (255,255,255))
            (textWidth, textHeight) = text.get_size()
            screen.blit(text, (cx - textWidth/2,cy - textHeight + vWhiteSpace))
            vWhiteSpace = textHeight*(3/4)


                  
#would have to have the join data as attributes and shit
#refer to those attributes when calling functions like detectCollision and stuff
class Hand(pygame.sprite.Sprite):
    def __init__(self, joints, jointPoints, jointPart, handImage, frameSurface):

        pygame.sprite.Sprite.__init__(self)
        
        #self.handCors = self.hand.get_rect()

        self.handCors = (int(jointPoints[jointPart].x), int(jointPoints[jointPart].y))
       

        if jointPart == PyKinectV2.JointType_HandRight:
            frameSurface.blit(handImage, self.handCors)
        else:
            #render the horizontall flipped robot hand
            frameSurface.blit(pygame.transform.flip(handImage, True, False), self.handCors)


    #use sprite/group attributes here to appropriately 
    #check for collision and stuff
    #the hands are a member of body so have to pass it in
    def detectCollision(menuButtonSprites, body):
        if pygame.sprite.spritecollide(self, menuButtonSprites) and body.hand_right_state or body.hand_left_state == 3:
            print("Hand was closed and menu item was collided with")






class startScreenRuntime(SceneBase):
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


        
        self._frame_surface = pygame.Surface((self._kinect.color_frame_desc.Width, self._kinect.color_frame_desc.Height), pygame.SRCALPHA, 32)


        #the frame surface where kinect stuff is drawn is made transparent so the "view" doesn't get rendered in window
        self._frame_surface = self._frame_surface.convert_alpha()


        # here we will store skeleton data 
        self._bodies = None


        #this will be used to check where the hands are relative to the "buttons" on screen
        (self.screenWidth, self.screenHeight) = pygame.display.get_surface().get_size()
        print(self.screenWidth, self.screenHeight)


        #****************************** menu background onto the screen
        self.background = pygame.image.load("images/menuToBeUsed.png")

        self.hand = pygame.image.load("images/robotHand.png")
      
       
        self.background = pygame.transform.scale(self.background,(960,540))
        #*********************************************************************


       
    def run(self):
        # -------- Main Program Loop -----------
        while not self._done:


            #create the MenuButtons and add them to group to detect "collision" with hand

            buttonsGroup = pygame.sprite.Group()

            buttonsGroup.add(MenuButton("Miror\nMode", self.background, self.screenWidth/4, self.screenHeight/4, self.screenWidth/2, self.screenHeight/2))
            buttonsGroup.add(MenuButton("Party\nMode", self.background, self.screenWidth*(3/4), self.screenHeight/4, self.screenWidth/2, self.screenHeight/2))
            buttonsGroup.add(MenuButton("Path\nMode", self.background, self.screenWidth/4, self.screenHeight*(3/4), self.screenWidth/2, self.screenHeight/2))
            buttonsGroup.add(MenuButton("Mimic\nMode", self.background, self.screenWidth*(3/4), self.screenHeight*(3/4), self.screenWidth/2, self.screenHeight/2))

        
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

                    # convert joint coordinates to color space 
                    joint_points = self._kinect.body_joints_to_color_space(joints)
                     
                    print("body detected")
                    #create each hand after parameters are defined
                    handsGroup = pygame.sprite.Group()
                    handsGroup.add(Hand(joints, joint_points, PyKinectV2.JointType_HandRight, self.hand, self._frame_surface))
                    handsGroup.add(Hand(joints, joint_points, PyKinectV2.JointType_HandLeft, self.hand, self._frame_surface))
                   

            #rendering background image
            self._screen.blit(self.background, (0,0))

 
            #these lines are used to rescale the kinect "screen" --> makes sure the hands are also rendered
            #in the relatively same positions on the background 
            h_to_w = float(self._frame_surface.get_height()) / self._frame_surface.get_width()
            target_height = int(h_to_w * self._screen.get_width())
            surface_to_draw = pygame.transform.scale(self._frame_surface, (self._screen.get_width(), target_height));
            self._screen.blit(surface_to_draw, (0,0))

           

            surface_to_draw = None
            


            #this clears the renders the hand every frame --> the fourth parameter is the opacity/alpha
            #which is set to 1 to hide the previous frame
            self._frame_surface.fill((100,100,100,1))


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

