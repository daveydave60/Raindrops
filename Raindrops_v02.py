# -*- coding: utf-8 -*-
"""
Created on Sun Jun 13 21:28:09 2021

@author: T. David Meyer; David Weissenborn
"""

import pygame
import time
import random

pygame.init()

frame_width  = 600
frame_height = 800

black = (0, 0, 0)
white = (255, 255, 255)

gameDisplay = pygame.display.set_mode((frame_width, frame_height))
pygame.display.set_caption('Raindrops')
clock = pygame.time.Clock()

class IterRegistry(type):
    def __iter__(cls):
        return iter(cls._registry)
    

class Droplet:
    """Class to create droplets of water"""
    __metaclass__ = IterRegistry
    _registry = []
    
    def __init__(self, x_pos, y_pos, radius, has_dropped):
        self._registry.append(self)
        self.x_pos = x_pos
        self.y_pos = y_pos
        self.radius = radius
        self.has_dropped = has_dropped

def rain(Droplet): #don't think this works yet, but I would rather pass the function a Droplet than its parts.
    pygame.draw.circle(gameDisplay, black, (Droplet.x_pos, Droplet.y_pos), Droplet.radius)

def game_loop():

    # objs = []
    # objs = [Droplet(random.randrange(0, frame_width), random.randrange(0, frame_height), 3, False) for i in range(10)]

    # gameDisplay.fill(white)
    # for i in range(10):
    #     rain(objs[i].x_pos, objs[i].y_pos, objs[i].radius)
    
    # pygame.display.update()
  
    
    score = 0
    objs = []
    done = False
    
    while not done:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                #quit()

        
        objs.append(Droplet(random.randrange(0, frame_width), random.randrange(0, frame_height), 5, False))
        gameDisplay.fill(white)
        for i in range(len(objs)):
            #rain(objs[i].x_pos, objs[i].y_pos, objs[i].radius)
            rain(objs[i])
        pygame.display.update()
        clock.tick(60)

game_loop()
pygame.quit()
#quit()