# -*- coding: utf-8 -*-
"""
Created on Sun Jun 13 2021

@author: T. David Meyer and David J. Weissenborn Jr.
"""

#%%
import pygame
import time
import random
import os
import math
from sys import exit

#%%
pygame.init()

FRAME_WIDTH, FRAME_HEIGHT  = 600, 800
FRAME_PADDING = 10

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (200, 200, 200)
GREEN = (0, 255, 0)

FPS = 60
BACKGROUND_VOLUME = 0.1

gameDisplay = pygame.display.set_mode((FRAME_WIDTH, FRAME_HEIGHT))
pygame.display.set_caption('Raindrops')
clock = pygame.time.Clock()
lightning_img = pygame.image.load(os.path.join('Assets', 'lightning_v5.png')).convert_alpha()
levels = list(range(1,51))
game_over = False  # will be set to True once player loses
game_completed = False  # will be set to True if player completes all levels.  They win the game.

score = 0

class IterRegistry(type):
    def __iter__(cls):
        return iter(cls._registry)


class Droplet:
    """Class to create droplets of water"""
    __metaclass__ = IterRegistry
    _registry = []

    def __init__(self, x_pos, y_pos, radius, color, is_connected, is_clicked, will_drop, is_dropping, should_die): ####
        self._registry.append(self)
        self.x_pos = x_pos
        self.y_pos = y_pos
        self.radius = radius
        self.color = color
        self.is_connected = is_connected 
        self.is_clicked = is_clicked
        self.will_drop = will_drop
        self.is_dropping = is_dropping
        self.should_die = should_die
        self.jitter_count = 0
        
        # load game sounds to channel 1
        self.pop_sfx = pygame.mixer.Sound(os.path.join('Assets', 'DoublePop.mp3'))
        self.pop_array = self.pop_sfx.get_raw()[130000:140000] #slice larger sound file to between 1.3s and 1.4s
        self.pop_sfx = pygame.mixer.Sound(buffer=self.pop_array)
        self.chan1 = pygame.mixer.Channel(1)
        self.chan1.set_volume(0.2)
        
        # Create surface for droplet
        self.image = pygame.Surface([radius * 2, radius * 2])
        self.rect = self.image.get_rect(center = (self.x_pos, self.y_pos))
        
        # Create mask from surface for collision detection
        self.mask = pygame.mask.from_surface(self.image)
        
    def draw(self, window):
        pygame.draw.circle(window, self.color, (self.x_pos, self.y_pos), self.radius)
        
    def burst(self):
        self.chan1.play(self.pop_sfx)

class Lightning:
    def __init__(self, x_pos, y_pos, is_clicked): ####
        self.x_pos = x_pos
        self.y_pos = y_pos
        self.is_clicked = is_clicked
        self.jitter_count = 0

        # load game sounds to channel 1
        self.pop_sfx = pygame.mixer.Sound(os.path.join('Assets', 'Thunder.mp3'))
        self.pop_array = self.pop_sfx.get_raw()[0:500000] #slice larger sound file to between 0s and 5s
        self.pop_sfx = pygame.mixer.Sound(buffer=self.pop_array)
        self.chan1 = pygame.mixer.Channel(1)
        self.chan1.set_volume(0.4)
        
        # Create surface for droplet
        self.image = lightning_img
        #self.image = pygame.transform.scale(self.image, (30,30))
        self.rect = self.image.get_rect(center = (self.x_pos, self.y_pos))
        
        # Create mask from surface for collision detection
        self.mask = pygame.mask.from_surface(self.image)

    def burst(self):
        self.chan1.play(self.pop_sfx)

def draw_clock(window, time_left):
    # Draw clock on screen
    pygame.draw.rect(
        window, BLACK, pygame.Rect(
            FRAME_PADDING, FRAME_PADDING, FRAME_WIDTH // 2 - FRAME_PADDING * 2, 100
            ), 2)
    clockLabel_font = pygame.font.SysFont('arial', 12)
    clockLabel_text = clockLabel_font.render("TIME LEFT", True, BLACK, WHITE)
    clockLabel_textRect = clockLabel_text.get_rect(topright=(FRAME_WIDTH // 2 - FRAME_PADDING * 2, FRAME_PADDING))
    
    window.blit(clockLabel_text, clockLabel_textRect)

    # Draw timer on screen
    time_font = pygame.font.SysFont('arial', 48)  #'freesansbold.ttf'
    
    time_text = str(int(time_left // 60)).rjust(2, "0") + ":" + str(int(time_left % 60)).rjust(2, "0") +\
        ":" + str(int((time_left % 1) * 100)).rjust(2, "0")
    time_text = time_font.render(time_text, True, BLACK, WHITE)
    time_textRect = time_text.get_rect()
    time_textRect.center = (FRAME_WIDTH // 4, (100 + FRAME_PADDING * 2) // 2)
    gameDisplay.blit(time_text, time_textRect)
    return time_textRect
    
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

def draw_message(window, text_string, text_size):
    # Draw message on screen
    pygame.draw.rect(window, GRAY, pygame.Rect(FRAME_WIDTH / 2 - 200, FRAME_HEIGHT / 2 - 100, 400, 200), 0)  #this rect is filled
    pygame.draw.rect(window, BLACK, pygame.Rect(FRAME_WIDTH / 2 - 200, FRAME_HEIGHT / 2 - 100, 400, 200), 4)  #this rect adds a border
    message_font = pygame.font.SysFont('comicsans', text_size)
    draw_text = message_font.render(text_string, 1, BLACK)
    window.blit(draw_text, (FRAME_WIDTH//2 - draw_text.get_width()//2, FRAME_HEIGHT//2 - draw_text.get_height()//2))
    pygame.display.update()


def level_intro(level):
    global score
    for i in range(FPS * 5): #run intro for 5 seconds
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
        
        gameDisplay.fill(WHITE)
        
        ##draw clock rect, and clock timer
        draw_clock(gameDisplay, 0)
                
        ##draw scoreboard rect and score
        draw_scoreboard(gameDisplay, score)
        
        #draw gameplay region rect
        pygame.draw.rect(gameDisplay, BLACK, pygame.Rect(FRAME_PADDING, 100 + FRAME_PADDING * 2, 
                FRAME_WIDTH - FRAME_PADDING * 2,FRAME_HEIGHT - 100 - FRAME_PADDING * 2 - FRAME_PADDING), 2)
        
        draw_message(gameDisplay, 'Level ' + str(level), 100)
         
def game_over_screen():
    print('You failed :(   Game over!')

def game_complete_screen():
    print('You beat the game!!!!')

# Main function
def game_loop(bool_small_drops_count, bool_nat_drops_neg, level):
    # Initialize variables
    global score
    global game_over
    global game_completed
    objs = []
    light_objs = []
    done = False
    jitters = [-3, 3] # determines how much a jittering droplet moves form side to side
    frames_elapsed = 0 #used for jitter
    jitter_frames = FPS * 2 - (level - 1)
    play_state = 'RUNNING'
    level_end_score_threshold = (level - 1) * 200

    lightning_prob = 1000 + ((level - 1) * 40) #expected value of lightning is 1 in this many frames

    time_given = 60 # in seconds
    time_left = time_given
    droplet_interval = 1
    initial_droplet_radius = 5
    radius_max = initial_droplet_radius + 6
    fall_speed = 10 
    
    gameDisplay.fill(WHITE)
    
    # Define clock_area
    clock_area = draw_clock(gameDisplay, time_left)
    
    pygame.display.update()
    
    # function to determine how a drop gets scored. for adding to current score
    def increment_score(drop, absorbed_by_clicked_drop, absorbing_drop_radius):
        size_check_met = True
        absorbed_check_met = True
        pos_neg_mult = 1
        
        if drop.is_clicked: #drop was clicked
            if drop.radius < radius_max and bool_small_drops_count == False:
                size_check_met = False
        else: #drop was absorbed
            if absorbed_by_clicked_drop == False: #absorbed by a natural drop
                if bool_nat_drops_neg:
                    pos_neg_mult = -1
                else:
                    absorbed_check_met = False
            else: #absorbed by a clicked drop
                if absorbing_drop_radius < radius_max and bool_small_drops_count == False:
                    size_check_met = False
        
        incr = int(drop.radius) * int(size_check_met) * int(absorbed_check_met) * pos_neg_mult
        
        return incr
    
    
    # Main while loop to check and manage game state
    while not done:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            
            # Handle clicked droplets
            if event.type == pygame.MOUSEBUTTONUP:
                pos = pygame.mouse.get_pos()
                
                # toggle pause when user clicks on clock
                if clock_area.collidepoint(pos):
                    play_state = 'PAUSED' if play_state == 'RUNNING' else 'RUNNING'
                
                if play_state != 'PAUSED':
                    # List clicked droplets
                    clicked_droplets = [d for d in objs if d.rect.collidepoint(pos)]
                    if len(clicked_droplets) != 0:
                        clicked_droplets[0].burst()
                    
                    # Start clicked droplets falling
                    for drop in clicked_droplets:
                        drop.is_dropping = True  # objs.remove(drop)
                        drop.is_clicked = True #used later for scoring
                        drop.will_drop = False
                        score += increment_score(drop, False, 0)

                    # Clear clicked lightning and start large droplets falling
                    clicked_lightning = [obj for obj in light_objs if obj.rect.collidepoint(pos)]
                    if len(clicked_lightning) != 0:
                        clicked_lightning[0].burst() #only one is clicked in a given frame
                        #light_objs[:] = []
                        light_objs.remove(clicked_lightning[0])
                        for i in [obj for obj in objs if obj.will_drop == True]:
                            i.is_clicked = True #this makes sure it gets scored positively
                            i.is_dropping = True
                    
        frames_elapsed += 1
        
        if play_state == 'PAUSED':
            draw_message(gameDisplay, 'Paused', 100)
        elif (time_left > 0) & (pygame.time.get_ticks() % droplet_interval == 0):
            # Append a Droplet to the running list
            objs.append(Droplet(random.randrange(FRAME_PADDING*2, FRAME_WIDTH - FRAME_PADDING*2),
                                random.randrange(FRAME_PADDING*3 + 100, FRAME_HEIGHT - FRAME_PADDING * 2),
                                5, BLACK, False, False, False, False, False))
            
            # Append lightning under the right conditions
            if random.random() < (1 / lightning_prob):
                light_objs.append(Lightning(random.randrange(FRAME_PADDING*2, FRAME_WIDTH - FRAME_PADDING*2),
                                            random.randrange(FRAME_PADDING*3 + 100, FRAME_HEIGHT - FRAME_PADDING * 2), False))
            
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
                connected_drop_area_sum += math.pi * (initial_droplet_radius ** 2) # to add in the area of the current drop if other drops are touching it
                objs.append(Droplet(objs[-1].x_pos, objs[-1].y_pos, math.sqrt(connected_drop_area_sum / math.pi), BLACK,
                                    False, False, False, False, False))
                objs.pop(-2) # remove second to last item, which was the original Droplet that fell this frame
                if objs[-1].radius > radius_max:
                    objs[-1].will_drop = True
            
            #jitter drops
            for i in [dplt for dplt in objs if dplt.will_drop == True]:
                i.x_pos += jitters[frames_elapsed % len(jitters)]
                i.jitter_count += 1
                if i.jitter_count > jitter_frames:
                    i.will_drop = False
                    i.is_dropping = True
            
            # Start large droplets falling down the screen and absorb any droplets in their path as they fall
            # and mark droplets that have fallen off the screen for removal
            for i in [dplt for dplt in objs if dplt.is_dropping == True]:
                i.y_pos += fall_speed
                for d in objs:
                    if d.rect.collidepoint(i.x_pos, i.y_pos) and i != d:
                        score += increment_score(d, i.is_clicked, i.radius)
                        #i.radius = math.sqrt(((i.radius ** 2 * math.pi) + (d.radius ** 2 * math.pi)) / math.pi)  # would make the falling drop grow as it consumes others
                        d.should_die = True
                if i.y_pos > FRAME_HEIGHT + 10:
                    i.should_die = True
        
            #clear Droplets that are marked for death
            objs[:] = [dplt for dplt in objs if dplt.should_die != True]
        
            # Manage clock
            time_left = max(0, time_left - 1/FPS) #= max(0, time_given - (time.time() - time_start))
        
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

            # Draw lightning in light_objs
            for l in light_objs:
                gameDisplay.blit(l.image, l.rect)

        if time_left == 0:
            draw_message(gameDisplay, 'Time\'s up!', 100)
            
            pygame.time.delay(3000)
            done = True
            #break
        
        pygame.display.update()
        clock.tick(FPS)

    if score < level_end_score_threshold:
        game_over = True
    elif level == levels[-1]:
        game_completed = True

# Load background sound to channel 0
rain_track = pygame.mixer.Sound(os.path.join('Assets', 'rainfall.mp3'))
chan = pygame.mixer.Channel(0)

# Play background sound on infinite loop
chan.play(rain_track, loops = -1)
chan.set_volume(BACKGROUND_VOLUME)

# loop through levels and end game when necessary
for level in levels:
    if game_over:
        break
    else:
        level_intro(level)
        game_loop(False, True, level)

if game_over:
    game_over_screen()
elif game_completed:
    game_complete_screen()

#print score and other initial variable attributes to a .csv database file 
print(score)
score_and_attrib_list = ['UserX', score]
with open(os.path.join('Assets', 'scoreDB.csv'),'a') as fd:
    fd.write(",".join([str(x) for x in score_and_attrib_list]) + '\n')
            
pygame.quit()
#%%
#quit()