# -*- coding: utf-8 -*-
"""
Created on Sun Jun 13 21:28:09 2021

@author: T. David Meyer; David Weissenborn
"""

import pygame
import time
import random
import os

pygame.init()
pygame.mixer.init()

FRAME_WIDTH, FRAME_HEIGHT  = 600, 800

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

FPS = 60
BACKGROUND_VOLUME = 0.1

gameDisplay = pygame.display.set_mode((FRAME_WIDTH, FRAME_HEIGHT))
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
    pygame.draw.circle(gameDisplay, BLACK, (Droplet.x_pos, Droplet.y_pos), Droplet.radius)

def game_loop():

    # objs = []
    # objs = [Droplet(random.randrange(0, FRAME_WIDTH), random.randrange(0, FRAME_HEIGHT), 3, False) for i in range(10)]

    # gameDisplay.fill(WHITE)
    # for i in range(10):
    #     rain(objs[i].x_pos, objs[i].y_pos, objs[i].radius)
    
    # pygame.display.update()
  
    
    score = 0
    objs = []
    done = False
    
    rain_track = pygame.mixer.Sound(os.path.join('Assets', 'rainfall.mp3'))
    chan = pygame.mixer.Channel(0)
    
    chan.play(rain_track, loops = -1)
    chan.set_volume(BACKGROUND_VOLUME)
    
    #print(pygame.mixer.music.get_volume())
    
    while not done:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                #quit()

        
        objs.append(Droplet(random.randrange(0, FRAME_WIDTH), random.randrange(0, FRAME_HEIGHT), 5, False))
        gameDisplay.fill(WHITE)
        for i in range(len(objs)):
            #rain(objs[i].x_pos, objs[i].y_pos, objs[i].radius)
            rain(objs[i])
        pygame.display.update()
        clock.tick(FPS)

game_loop()
pygame.quit()
#quit()