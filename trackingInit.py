from pykinect2 import PyKinectV2
from pykinect2.PyKinectV2 import *
from pykinect2 import PyKinectRuntime





import ctypes, _ctypes, pygame, sys, math


if sys.hexversion >= 0x03000000:
    import _thread as thread
else:
    import thread




class trackingRuntime():
    def __init__(self):
        pygame.init()
        
        #self.calledByAnotherScreen = calledByAnotherScreen


        pygame.display.set_caption('Robo Dance Club')

        # Used to manage how fast the screen updates
        self._clock = pygame.time.Clock()

        
        # Set the width and height of the screen [width, height]

        #if not self.calledByAnotherScreen:
        self._infoObject = pygame.display.Info()
        self._screen = pygame.display.set_mode((self._infoObject.current_w >> 1, self._infoObject.current_h >> 1), 
                                                pygame.HWSURFACE|pygame.DOUBLEBUF|pygame.RESIZABLE, 32)
 

        # Loop until the user clicks the close button.
        self._done = False

       
        # Kinect runtime object, we want only color and body frames 
        self._kinect = PyKinectRuntime.PyKinectRuntime(PyKinectV2.FrameSourceTypes_Color | \
                                                                                    PyKinectV2.FrameSourceTypes_Body)
        

        self._frame_surface = pygame.Surface((self._kinect.color_frame_desc.Width, \
                                                            self._kinect.color_frame_desc.Height), pygame.SRCALPHA, 32)


        #the frame surface where kinect stuff is drawn is made transparent so the "view" doesn't get rendered in window
        self._frame_surface = self._frame_surface.convert_alpha()


        # here we will store skeleton data 
        self._bodies = None

        #this will be used to check where the hands are relative to the "buttons" on screen
        (self.screenWidth, self.screenHeight) = pygame.display.get_surface().get_size()
  
        self.mode = "startMode"

        


    def draw_color_frame(self, frame, target_surface):
        target_surface.lock()
        address = self._kinect.surface_as_array(target_surface.get_buffer())
        ctypes.memmove(address, frame.ctypes.data, frame.size)
        del address
        target_surface.unlock()


    def run(self):
        #overwritten by every screen using 
        #the attributes defined in the initialization of this class
        pass


