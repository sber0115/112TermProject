from pykinect2 import PyKinectV2
from pykinect2.PyKinectV2 import *
from pykinect2 import PyKinectRuntime






import ctypes, _ctypes, pygame, sys, math


if sys.hexversion >= 0x03000000:
    import _thread as thread
else:
    import thread



def run_game():
    pygame.init()
    screen = pygame.display.set_mode((width, height))
    clock = pygame.time.Clock()



run_game()