# -*- coding: utf-8 -*-
"""
Created on Sun Jun 13 21:28:09 2021

@author: T. David Meyer; David Weissenborn
"""

import pygame
import time
import random
import os

#%%
pygame.init()
pygame.mixer.init()

FRAME_WIDTH, FRAME_HEIGHT  = 600, 800
FRAME_PADDING = 10

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
    time_start = time.time()
    time_given = 70 # in seconds
    time_left = time_given
    
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

        if time_left > 0:  
            #append a Droplet to the running list
            objs.append(Droplet(random.randrange(FRAME_PADDING*2, FRAME_WIDTH - FRAME_PADDING*2),
                                random.randrange(FRAME_PADDING*3 + 100, FRAME_HEIGHT - FRAME_PADDING * 2), 5, False))
        
        gameDisplay.fill(WHITE)
        
        ##draw clock rect, and clock timer
        pygame.draw.rect(gameDisplay, BLACK, pygame.Rect(FRAME_PADDING, FRAME_PADDING, FRAME_WIDTH / 2 - FRAME_PADDING * 2, 100), 2)
        clockLabel_font = pygame.font.SysFont('arial', 12)
        clockLabel_text = clockLabel_font.render("TIME LEFT", True, BLACK, WHITE)
        clockLabel_textRect = clockLabel_text.get_rect(topright=(FRAME_WIDTH / 2 - FRAME_PADDING * 2, FRAME_PADDING))
        gameDisplay.blit(clockLabel_text, clockLabel_textRect)
        time_font = pygame.font.SysFont('arial', 48)  #'freesansbold.ttf'
        time_now = time.time()
        time_left = max(0, time_given - (time_now - time_start))
        time_text = str(int(time_left // 60)).rjust(2, "0") + ":" + str(int(time_left % 60)).rjust(2, "0") + ":" + str(int((time_left % 1) * 100)).rjust(2, "0")
        time_text = time_font.render(time_text, True, BLACK, WHITE)
        time_textRect = time_text.get_rect()
        time_textRect.center = (FRAME_WIDTH / 4, (100 + FRAME_PADDING * 2) / 2)
        gameDisplay.blit(time_text, time_textRect)
        ##end draw clock
        
        ##draw scoreboard rect and score
        pygame.draw.rect(gameDisplay, BLACK, pygame.Rect(FRAME_WIDTH / 2 + FRAME_PADDING / 2, FRAME_PADDING, FRAME_WIDTH / 2 - FRAME_PADDING * 2, 100), 2)
        scoreLabel_font = pygame.font.SysFont('arial', 12)
        scoreLabel_text = scoreLabel_font.render("SCORE", True, BLACK, WHITE)
        scoreLabel_textRect = scoreLabel_text.get_rect(topleft=(FRAME_WIDTH / 2 + FRAME_PADDING * 2, FRAME_PADDING))
        gameDisplay.blit(scoreLabel_text, scoreLabel_textRect)
        score_font = pygame.font.SysFont('arial', 48)
        score_text = score_font.render(str(score), True, BLACK, WHITE)
        score_textRect = score_text.get_rect()
        score_textRect.center = (FRAME_WIDTH * 3/4, (100 + FRAME_PADDING * 2) / 2)
        gameDisplay.blit(score_text, score_textRect)
        #still need to 
        ##end draw scoreboard
        
        #draw gameplay region rect
        pygame.draw.rect(gameDisplay, BLACK, pygame.Rect(FRAME_PADDING, 100 + FRAME_PADDING * 2, FRAME_WIDTH - FRAME_PADDING * 2,
                                                         FRAME_HEIGHT - 100 - FRAME_PADDING * 2 - FRAME_PADDING), 2)
        
        for i in range(len(objs)): #for each Droplet
            #rain(objs[i].x_pos, objs[i].y_pos, objs[i].radius)
            rain(objs[i])
        pygame.display.update()
        clock.tick(FPS)

game_loop()
pygame.quit()
#%%
#quit()