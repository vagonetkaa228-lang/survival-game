import pygame
import math


class Survivor:
    def __init__(self, x, y, survivor_type='survivor', name=None):
        self.x = x
        self.y = y
        self.size = 40
        self.found = False
        self.type = survivor_type
        self.name = name or survivor_type
        self.story_npc = False
        self.dialogue_completed = False
        self.hit_timer = 0
        self.in_water = False
        self.water_bob = 0.0

    def take_hit(self):
        self.hit_timer = 18

    def update(self):
        if self.in_water:
            self.water_bob += 0.08
        if self.hit_timer > 0:
            self.hit_timer -= 1

    def draw(self, surface, camera_x, camera_y):
        bob = int(math.sin(self.water_bob) * 4) if self.in_water else 0
        from game.assets.sprites import blit_entity
        blit_entity(
            surface, self.type, self.x, self.y + bob, self.size,
            camera_x, camera_y,
            hit=self.hit_timer > 0,
        )
