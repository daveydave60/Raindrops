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
pygame.font.init()

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
        
        # Create surface for droplet
        self.image = pygame.Surface([radius * 2, radius * 2])
        self.rect = self.image.get_rect(center = (self.x_pos, self.y_pos))
        
        # Create mask from surface for collision detection
        self.mask = pygame.mask.from_surface(self.image)
        
    def draw(self, window):
        pygame.draw.circle(window, BLACK, (self.x_pos, self.y_pos), self.radius)

def draw_clock(window, time_left):
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
    
def draw_message(window, text):
    message_font = pygame.font.SysFont('comicsans', 100)
    draw_text = message_font.render(text, 1, BLACK)
    window.blit(draw_text, (FRAME_WIDTH//2 - draw_text.get_width()//2, FRAME_HEIGHT//2 - draw_text.get_height()//2))
    pygame.display.update()
    pygame.time.delay(5000)

# Main function
def game_loop():
    # Initialize variables
    score = 0
    objs = []
    done = False
    
    time_start = time.time()
    time_given = 7 # in seconds
    time_left = time_given
    droplet_interval = 2
    
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
                    score += drop.radius
                    objs.remove(drop)

        # Manage clock
        time_left = max(0, time_given - (time.time() - time_start))
        
        # Append a Droplet to the running list
        if (time_left > 0) & (pygame.time.get_ticks() % droplet_interval == 0):  
            objs.append(Droplet(random.randrange(FRAME_PADDING*2, FRAME_WIDTH - FRAME_PADDING*2),
                                random.randrange(FRAME_PADDING*3 + 100, FRAME_HEIGHT - FRAME_PADDING * 2), 5, False))
        
        if time_left == 0:
            draw_message(gameDisplay, 'Time\'s up!')
            break
        
        gameDisplay.fill(WHITE)
        
        ##draw clock rect, and clock timer
        draw_clock(gameDisplay, time_left)
                
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