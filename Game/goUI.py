#!/usr/bin/env python
# coding: utf-8

"""Goban made with Python, pygame and go.py.

This is a front-end for my go library 'go.py', handling drawing and
pygame-related activities. Together they form a fully working goban.

"""

import go
from sys import exit
import random
import pygame, sys, os
from pygame.locals import *
import ego_tool as et
import numpy as np
import RPi.GPIO as GPIO


BACKGROUND = 'images/ramin.jpg'
BOARD_SIZE = (320, 240) #820 ^ 2
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLACK = (0, 0, 0)
running = True # A flag used for stop the loop

mouse_coord = [5 + 24, 5 + 24]
poss = []
def draw_mouse():
    pygame.draw.circle(screen, RED, mouse_coord, 4, 0)
    pygame.display.update()

def remove_mouse():
    """Remove the stone from board."""
    blit_coords = (mouse_coord[0] - 6, mouse_coord[1] - 6)
    area_rect = pygame.Rect(blit_coords, (12, 12))
    screen.blit(background, blit_coords, area_rect)
    pygame.display.update()
    # super(Stone, self).remove()

class Stone(go.Stone):
    def __init__(self, board, point, color):
        """Create, initialize and draw a stone."""
        super(Stone, self).__init__(board, point, color)
        self.coords = (5 + self.point[0] * 12, 5 + self.point[1] * 12)
        self.possibilities = self.set_new_possiblities()
        # self.mouse_coord = (5 + 24, 5 + 24)
        self.draw()


    def draw(self):
        """Draw the stone as a circle."""
        pygame.draw.circle(screen, self.color, self.coords, 6, 0)

        """ Fill old possibilities list for future display"""
        s = pygame.Surface((80, 240))
        # s.set_alpha(128)
        s.fill((227, 200, 143))
        # Left top position
        screen.blit(s, (240, 0)) 
        """ Update scores """
        possibilities_font = pygame.font.Font(None, 20)
        char = possibilities_font.render('x  |  y  |  Win', True, (0,0,0))
        rec = char.get_rect(center = (280, 20))
        screen.blit(char, rec)

        for i in range(len(self.possibilities)):
            char = possibilities_font.render(str(self.possibilities[i][0]) + '   ' + str(self.possibilities[i][1]) + '   ' + str(self.possibilities[i][2])+'%', True, (0,0,0))
            rec = char.get_rect(center = (280, i * 24 + 40))
            screen.blit(char, rec)
        pygame.display.update()



    def set_new_possiblities(self):
        cur_board = np.zeros((19,19),int)
        for i in range(len(poss)):
            if i % 2 == 0:
                cur_board[poss[i][0]][poss[i][1]] = 1
            else:
                cur_board[poss[i][0]][poss[i][1]] = -1
        a, b = et.ego_predict(et.predict_init(), cur_board, 1)
        # print(a)

        new_possiblities = []
        # for i in a:
        #     temp = []
        #     (key, value), = i.items()
        #     for cor in key:
        #         temp.append(cor)
        #     temp.append(value)
        #     new_possiblities.append(temp)

        for i in range(9):
            temp = []
            for j in range(2):
                temp.append(random.randint(0,18))
            temp.append(random.randint(0, 100))
            new_possiblities.append(temp)
        return new_possiblities

    def remove(self):
        """Remove the stone from board."""
        blit_coords = (self.coords[0] - 6, self.coords[1] - 6)
        area_rect = pygame.Rect(blit_coords, (12, 12))
        screen.blit(background, blit_coords, area_rect)
        pygame.display.update()
        super(Stone, self).remove()


class Board(go.Board):
    def __init__(self, mouse_coor):
        """Create, initialize and draw an empty board."""
        super(Board, self).__init__()
        self.outline = pygame.Rect(13, 13, 223, 223)
        self.mouse_coor = [0, 0]
        # self.possibilities = [[1,2, 0.85], [5,2, 0.21],[2,4, 0.5], [5,6, 0.5], [11,23, 0.5], [13,23, 0.5], [13,23, 0.5], [13,23, 0.5], [13,23, 0.5]]
        self.possibilities = self.set_new_possiblities()
        self.draw()

    def inBound(self, row, col):
        if row < 0 or col < 0 or row > 19 or col > 19:
            return false
        return true

    def set_new_possiblities(self):
        new_possiblities = []
        for i in range(9):
            temp = []
            for j in range(2):
                temp.append(random.randint(0,18))
            temp.append(random.randint(0, 100))
            new_possiblities.append(temp)
        return new_possiblities

    def draw(self):
        """Draw the board to the background and blit it to the screen.

        The board is drawn by first drawing the outline, then the 19x19
        grid and finally by adding hoshi to the board. All these
        operations are done with pygame's draw functions.

        This method should only be called once, when initializing the
        board.

        """
        pygame.draw.rect(background, BLACK, self.outline, 3)
        # Outline is inflated here for future use as a collidebox for the mouse
        self.outline.inflate_ip(20, 20)
        for i in range(18):
            for j in range(18):
                rect = pygame.Rect(17 + (12 * i), 17 + (12 * j), 12, 12)
                pygame.draw.rect(background, BLACK, rect, 1)
        for i in range(3):
            for j in range(3):
                coords = (53 + (72 * i), 53 + (72 * j))
                pygame.draw.circle(background, BLACK, coords, 4, 0)

        screen.blit(background, (0, 0))

        # possibilities_font = pygame.font.Font(None, 20)
        # char = possibilities_font.render('x  |  y  |  Win', True, (0,0,0))
        # rec = char.get_rect(center = (280, 20))
        # screen.blit(char, rec)
        # for i in range(len(self.possibilities)):
        #     char = possibilities_font.render(str(self.possibilities[i][0]) + '   ' + str(self.possibilities[i][1]) + '   ' + str(self.possibilities[i][2])+'%', True, (0,0,0))
        #     rec = char.get_rect(center = (280, i * 24 + 40))
        #     screen.blit(char, rec)

        pygame.display.update()

    def update_liberties(self, added_stone=None):
        """Updates the liberties of the entire board, group by group.

        Usually a stone is added each turn. To allow killing by 'suicide',
        all the 'old' groups should be updated before the newly added one.

        """
        temp = []
        poss.clear()
        for group in self.groups:
            if added_stone:
                if group == added_stone.group:
                    continue
            group.update_liberties()
            for i in group.request_update_board():
                temp.append(i)
        if added_stone:
            added_stone.group.update_liberties()
            temp.append(added_stone.group.request_update_board())
        for i in temp:
            if not i in poss:
                poss.append(i)
        print(poss)



def main():
    while running:
        # pygame.time.wait(250)
        if (not GPIO.input(17)):
            print ('K_UP')
            if mouse_coord[1] != 5 + 12:
                x = int(round(((mouse_coord[0] - 5) / 12.0), 0))
                y = int(round(((mouse_coord[1] - 5) / 12.0), 0))
                stone_old = board.search(point=(x, y))
                if not stone_old:
                    remove_mouse()
                mouse_coord[1] -= 12
                x = int(round(((mouse_coord[0] - 5) / 12.0), 0))
                y = int(round(((mouse_coord[1] - 5) / 12.0), 0))
                stone_new = board.search(point=(x, y))
                if not stone_new:
                    # print('sb')
                    draw_mouse()
        elif (not GPIO.input(22)):
            print ('K_DOWN')
            if mouse_coord[1] != 233:
                x = int(round(((mouse_coord[0] - 5) / 12.0), 0))
                y = int(round(((mouse_coord[1] - 5) / 12.0), 0))
                stone_old = board.search(point=(x, y))
                if not stone_old:
                    remove_mouse()
                mouse_coord[1] += 12
                x = int(round(((mouse_coord[0] - 5) / 12.0), 0))
                y = int(round(((mouse_coord[1] - 5) / 12.0), 0))
                stone_new = board.search(point=(x, y))
                if not stone_new:
                    # print('sb2')
                    draw_mouse()
        elif (not GPIO.input(23)):
            if mouse_coord[0] != 5 + 12:
                x = int(round(((mouse_coord[0] - 5) / 12.0), 0))
                y = int(round(((mouse_coord[1] - 5) / 12.0), 0))
                stone_old = board.search(point=(x, y))
                if not stone_old:
                    remove_mouse()
                mouse_coord[0] -= 12
                x = int(round(((mouse_coord[0] - 5) / 12.0), 0))
                y = int(round(((mouse_coord[1] - 5) / 12.0), 0))
                stone_new = board.search(point=(x, y))
                if not stone_new:
                    # print('sb3')
                    draw_mouse()
        elif (not GPIO.input(27)):
            if mouse_coord[0] != 233:
                x = int(round(((mouse_coord[0] - 5) / 12.0), 0))
                y = int(round(((mouse_coord[1] - 5) / 12.0), 0))
                stone_old = board.search(point=(x, y))
                if not stone_old:
                    remove_mouse()
                mouse_coord[0] += 12
                x = int(round(((mouse_coord[0] - 5) / 12.0), 0))
                y = int(round(((mouse_coord[1] - 5) / 12.0), 0))
                stone_new = board.search(point=(x, y))
                if not stone_new:
                    # print('sb4')
                    draw_mouse()
        elif (GPIO.input(19)):
            x = int(round(((mouse_coord[0] - 5) / 12.0), 0))
            y = int(round(((mouse_coord[1] - 5) / 12.0), 0))
            stone = board.search(point=(x, y))
            if stone:
                stone.remove()
            else:
                added_stone = Stone(board, (x, y), board.turn())
            board.update_liberties(added_stone)
            board.set_new_possiblities()
        elif (not GPIO.input(26)):
            running = false
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                exit()
            if event.type == pygame.KEYDOWN:
                # if (not GPIO.input(17)):
                if event.key == pygame.K_UP:
                    print ('K_UP')
                    if mouse_coord[1] != 5 + 12:
                        x = int(round(((mouse_coord[0] - 5) / 12.0), 0))
                        y = int(round(((mouse_coord[1] - 5) / 12.0), 0))
                        stone_old = board.search(point=(x, y))
                        if not stone_old:
                            remove_mouse()
                        mouse_coord[1] -= 12
                        x = int(round(((mouse_coord[0] - 5) / 12.0), 0))
                        y = int(round(((mouse_coord[1] - 5) / 12.0), 0))
                        stone_new = board.search(point=(x, y))
                        if not stone_new:
                            # print('sb')
                            draw_mouse()
                elif event.key == pygame.K_DOWN:
                    print ('K_DOWN')
                    if mouse_coord[1] != 233:
                        x = int(round(((mouse_coord[0] - 5) / 12.0), 0))
                        y = int(round(((mouse_coord[1] - 5) / 12.0), 0))
                        stone_old = board.search(point=(x, y))
                        if not stone_old:
                            remove_mouse()
                        mouse_coord[1] += 12
                        x = int(round(((mouse_coord[0] - 5) / 12.0), 0))
                        y = int(round(((mouse_coord[1] - 5) / 12.0), 0))
                        stone_new = board.search(point=(x, y))
                        if not stone_new:
                            # print('sb2')
                            draw_mouse()
                elif event.key == pygame.K_LEFT:
                    print ('K_LEFT')
                    if mouse_coord[0] != 5 + 12:
                        x = int(round(((mouse_coord[0] - 5) / 12.0), 0))
                        y = int(round(((mouse_coord[1] - 5) / 12.0), 0))
                        stone_old = board.search(point=(x, y))
                        if not stone_old:
                            remove_mouse()
                        mouse_coord[0] -= 12
                        x = int(round(((mouse_coord[0] - 5) / 12.0), 0))
                        y = int(round(((mouse_coord[1] - 5) / 12.0), 0))
                        stone_new = board.search(point=(x, y))
                        if not stone_new:
                            # print('sb3')
                            draw_mouse()
                elif event.key == pygame.K_RIGHT:
                    print ('K_RIGHT')
                    if mouse_coord[0] != 233:
                        x = int(round(((mouse_coord[0] - 5) / 12.0), 0))
                        y = int(round(((mouse_coord[1] - 5) / 12.0), 0))
                        stone_old = board.search(point=(x, y))
                        if not stone_old:
                            remove_mouse()
                        mouse_coord[0] += 12
                        x = int(round(((mouse_coord[0] - 5) / 12.0), 0))
                        y = int(round(((mouse_coord[1] - 5) / 12.0), 0))
                        stone_new = board.search(point=(x, y))
                        if not stone_new:
                            # print('sb4')
                            draw_mouse()
                elif event.key == pygame.K_SLASH: # Confirm
                    x = int(round(((mouse_coord[0] - 5) / 12.0), 0))
                    y = int(round(((mouse_coord[1] - 5) / 12.0), 0))
                    stone = board.search(point=(x, y))
                    if stone:
                        stone.remove()
                    else:
                        added_stone = Stone(board, (x, y), board.turn())
                    board.update_liberties(added_stone)
                    board.set_new_possiblities()
"""
if __name__ == '__main__':
    pygame.init()
    pygame.display.set_caption('ECE 5725 GO')
    screen = pygame.display.set_mode(BOARD_SIZE, 0, 32)
    background = pygame.image.load(BACKGROUND).convert()
    board = Board([0,0])
    
    os.putenv('SDL_VIDEODRIVER', 'fbcon') # Display on piTFT
    os.putenv('SDL_FBDEV', '/dev/fb1') #
    os.putenv('SDL_MOUSEDRV', 'TSLIB') # Track mouse clicks on piTFT
    os.putenv('SDL_MOUSEDEV', '/dev/input/touchscreen')
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(17, GPIO.IN, pull_up_down=GPIO.PUD_UP) 
    GPIO.setup(22, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(23, GPIO.IN, pull_up_down=GPIO.PUD_UP) 
    GPIO.setup(27, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(19, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(26, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    # GPIO.add_event_detect(17, GPIO.FALLING, callback=GPIO17_callback, bouncetime=300) 
    # GPIO.add_event_detect(22, GPIO.FALLING, callback=GPIO22_callback, bouncetime=300)
    # GPIO.add_event_detect(23, GPIO.FALLING, callback=GPIO23_callback, bouncetime=300) 
    # GPIO.add_event_detect(27, GPIO.FALLING, callback=GPIO27_callback, bouncetime=300) 
    # GPIO.add_event_detect(19, GPIO.FALLING, callback=GPIO19_callback, bouncetime=300)
    # GPIO.add_event_detect(26, GPIO.FALLING, callback=GPIO26_callback, bouncetime=300)

    # def GPIO17_callback(channel):
    #     print('UP')
    # def GPIO22_callback(channel):
    #     print('DOWN')
    # def GPIO23_callback(channel):
    #     print('LEFT')
    # def GPIO27_callback(channel):
    #     print('RIGHT')
    # def GPIO19_callback(channel):
    #     print('CONFIRM')
    # def GPIO26_callback(channel):
    #     running = False
    #     print('QUIT')

    main()
