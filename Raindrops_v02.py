# -*- coding: utf-8 -*-
"""
Created on Sat Jun 19 00:52:09 2021

@author: wrath
"""

import pygame
import time
import random
import os
import math

#%%
pygame.init()
pygame.mixer.init()

FRAME_WIDTH, FRAME_HEIGHT  = 600, 800
FRAME_PADDING = 10

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)

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
    
    def __init__(self, x_pos, y_pos, radius, color, is_connected, is_dropping, has_dropped):
        self._registry.append(self)
        self.x_pos = x_pos
        self.y_pos = y_pos
        self.radius = radius
        self.color = color
        self.is_connected = is_connected
        self.is_dropping = is_dropping
        self.has_dropped = has_dropped
        
        # Create surface for droplet
        self.image = pygame.Surface([radius * 2, radius * 2])
        self.rect = self.image.get_rect(center = (self.x_pos, self.y_pos))
        
        # Create mask from surface for collision detection
        self.mask = pygame.mask.from_surface(self.image)
        
    def draw(self, window):
        pygame.draw.circle(window, BLACK, (self.x_pos, self.y_pos), self.radius)

def draw_clock(window, time_start, time_left, time_given):
    # Draw clock on screen
    pygame.draw.rect(
        window, BLACK, pygame.Rect(
            FRAME_PADDING, FRAME_PADDING, FRAME_WIDTH / 2 - FRAME_PADDING * 2, 100
            ), 2)
    clockLabel_font = pygame.font.SysFont('arial', 12)
    clockLabel_text = clockLabel_font.render("TIME LEFT", True, BLACK, WHITE)
    clockLabel_textRect = clockLabel_text.get_rect(topright=(FRAME_WIDTH / 2 - FRAME_PADDING * 2, FRAME_PADDING))
    
    window.blit(clockLabel_text, clockLabel_textRect)

    # Draw timer on screen
    time_font = pygame.font.SysFont('arial', 48)  #'freesansbold.ttf'
    time_now = time.time()
    time_left = max(0, time_given - (time_now - time_start))
    time_text = str(int(time_left // 60)).rjust(2, "0") + ":" + str(int(time_left % 60)).rjust(2, "0") +\
        ":" + str(int((time_left % 1) * 100)).rjust(2, "0")
    time_text = time_font.render(time_text, True, BLACK, WHITE)
    time_textRect = time_text.get_rect()
    time_textRect.center = (FRAME_WIDTH / 4, (100 + FRAME_PADDING * 2) / 2)
    gameDisplay.blit(time_text, time_textRect)
    
def draw_scoreboard(window, score):
    pygame.draw.rect(
        window, BLACK, pygame.Rect(
            FRAME_WIDTH / 2 + FRAME_PADDING / 2, FRAME_PADDING, FRAME_WIDTH / 2 - FRAME_PADDING * 2, 100
            ), 2)
    scoreLabel_font = pygame.font.SysFont('arial', 12)
    scoreLabel_text = scoreLabel_font.render("SCORE", True, BLACK, WHITE)
    scoreLabel_textRect = scoreLabel_text.get_rect(topleft=(FRAME_WIDTH / 2 + FRAME_PADDING * 2, FRAME_PADDING))
    window.blit(scoreLabel_text, scoreLabel_textRect)
    
    score_font = pygame.font.SysFont('arial', 48)
    score_text = score_font.render(str(score), True, BLACK, WHITE)
    score_textRect = score_text.get_rect()
    score_textRect.center = (FRAME_WIDTH * 3/4, (100 + FRAME_PADDING * 2) / 2)
    window.blit(score_text, score_textRect)

# Main function
def game_loop():
    # Initialize variables
    score = 0
    objs = []
    done = False
    
    time_start = time.time()
    time_given = 10 # in seconds
    time_left = time_given
    droplet_interval = 1
    initial_droplet_radius = 5
    radius_max = initial_droplet_radius + 6
    fall_speed = 10
    
    # Load background sound to channel
    rain_track = pygame.mixer.Sound(os.path.join('Assets', 'rainfall.mp3'))
    chan = pygame.mixer.Channel(0)
    
    # Play background sound on infinite loop
    chan.play(rain_track, loops = -1)
    chan.set_volume(BACKGROUND_VOLUME)
    
    # Main while loop to check and manage game state
    while not done:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            
            # Handle clicked droplets
            if event.type == pygame.MOUSEBUTTONUP:
                pos = pygame.mouse.get_pos()
                
                # List clicked droplets
                clicked_droplets = [d for d in objs if d.rect.collidepoint(pos)]
                
                # Remove clicked droplets
                for drop in clicked_droplets:
                    score += int(drop.radius)
                    drop.is_dropping = True  # objs.remove(drop)

        # Append a Droplet to the running list
        if (time_left > 0) & (pygame.time.get_ticks() % droplet_interval == 0):  
            objs.append(Droplet(random.randrange(FRAME_PADDING*2, FRAME_WIDTH - FRAME_PADDING*2),
                                random.randrange(FRAME_PADDING*3 + 100, FRAME_HEIGHT - FRAME_PADDING * 2), 5, BLACK, False, False, False))
            
            # find connected droplets
            connected_drop_area_sum = 0
            if len(objs) > 1: # makes sure loop doesn't run on the first Droplet
                for i in objs[:-1]: # all but last item
                    if abs(i.x_pos - objs[-1].x_pos) < initial_droplet_radius*2 and abs(i.y_pos - objs[-1].y_pos) < initial_droplet_radius*2:
                        connected_drop_area_sum += math.pi * (i.radius ** 2)
                        i.is_connected, objs[-1].is_connected = True, True
                        i.color, objs[-1].color = GREEN, GREEN # this line simply for testing visual.  Remove for production.
                        objs.remove(i)  #comment for test, uncomment for prod
            
            # aggregate connected Droplets into one
            if connected_drop_area_sum > 0: # so this will only happen if there Droplets were connected in this frame
                connected_drop_area_sum += math.pi * (initial_droplet_radius ** 2) # to add in the radius of the current drop if other drops are touching it
                objs.append(Droplet(objs[-1].x_pos, objs[-1].y_pos, math.sqrt(connected_drop_area_sum / math.pi), BLACK, False, False, False))
                objs.pop(-2) # remove second to last item, which was the original Droplet that fell this frame
                if objs[-1].radius > radius_max:
                    objs[-1].is_dropping = True
            
            # Start large droplets falling down the screen
            for i in [dplt for dplt in objs if dplt.is_dropping == True]:
                i.y_pos += fall_speed
            
            # potentially needs a recursive call, because Droplets are growing and overlaping with others but not absorbing them
            # also need to pop Droplets from the list if they have dropped off of the screen
        
        gameDisplay.fill(WHITE)
        
        ##draw clock rect, and clock timer
        draw_clock(gameDisplay, time_start, time_left, time_given)
                
        ##draw scoreboard rect and score
        draw_scoreboard(gameDisplay, score)
        
        #draw gameplay region rect
        pygame.draw.rect(
            gameDisplay, BLACK, pygame.Rect(
                FRAME_PADDING, 
                100 + FRAME_PADDING * 2, 
                FRAME_WIDTH - FRAME_PADDING * 2,
                FRAME_HEIGHT - 100 - FRAME_PADDING * 2 - FRAME_PADDING
                ), 2)
        
        # Draw droplets in objs
        for droplet in objs:
            droplet.draw(gameDisplay)
            
        pygame.display.update()
        clock.tick(FPS)

game_loop()
pygame.quit()
#%%
#quit()