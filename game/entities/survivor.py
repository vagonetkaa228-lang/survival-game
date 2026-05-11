import pygame


class Survivor:
    def __init__(self,x,y, survivor_type ='survivor'):
        self.x = x
        self.y = y
        self.size = 15
        self.found = False
        self.type = survivor_type

    def draw(self, surface, camera_x, camera_y):
        pygame.draw.rect(surface, (0, 255, 0), (self.x - camera_x, self.y - camera_y, self.size, self.size))
