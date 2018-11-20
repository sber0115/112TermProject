import pygame
from sceneManager import SceneBase



pygame.init()
screen = pygame.display.set_mode((400, 400))

playing = True

while playing:

    clock = pygame.time.Clock()


    screen.fill((0, 0, 255))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            playing = False


    pygame.display.update()




