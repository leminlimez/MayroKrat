## DEBUG OPTIONS ##
Fast_Compile = False # does not pre-compile the environment (meant for testing ui)
Debug_Mode = False # get put directly into the 3D environment
Debug_Track = "MarioCircuit" # track to load when starting in debug mode

import pygame
import numpy
import os
#import time

from Modules import Game
from Modules import Menus
from Modules import GhostManager
from Modules.UIObjects import Fade as FadeObject
from Modules.Track import Tracks
from Modules.Driver import Driver

from PyGame3D import Engine_3D

## CONFIG ##
Resolution = 2.5 # resolution multiplier; larger = more lag
Window = (800, 600) # Window size (default is 800 x 600)
FPS = 60 # FPS Cap

## Colors ##
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 204, 0)

## Assets ##
COIN = Engine_3D.get_image("Assets/Sprites/Coin.png")
COIN = pygame.transform.scale(COIN, (45, 45))
DRIFT = Engine_3D.get_image("Assets/Sprites/DriftParticle.png")
MINI = Engine_3D.get_image("Assets/Sprites/MiniTurbo.png")
SUPER = Engine_3D.get_image("Assets/Sprites/SuperTurbo.png")
ULTRA = Engine_3D.get_image("Assets/Sprites/UltraTurbo.png")

# initialize tracks
tracks = Tracks()

pygame.init()

# joystick
joysticks = [pygame.joystick.Joystick(i) for i in range(pygame.joystick.get_count())]

font = pygame.font.SysFont("Comic Sans MS", 32)

def initialize():
    # code to prepare camera
    Camera = Engine_3D.Camera(Resolution, Window, (0.0, 0.0, 0.0, 0.0), True)
    
    Mario, MarioSize = Camera.get_sprites("Assets/Racers/Mayro/MayroDrive.png", 12, 32, 32)
    MPos = (952, 1, 751)#(935, 1, 444)
    MSp = Engine_3D.Sprite(Mario, 12, MPos, True)
    MSp.Direction = numpy.deg2rad(-90.01)
    Camera.add_sprite(MSp)
    Camera.PImg = [DRIFT, MINI, SUPER, ULTRA]
    
    MDriver = Driver(MSp, 4.0, 0.4)
    MDriver.attach_camera(Camera)
    tracks.MarioCircuit.load_track(Camera)
    cp = tracks.MarioCircuit.Checkpoints
    Coins = tracks.MarioCircuit.spawn_coins(Camera)
    CoinAnims = []

    Camera.preload()


# main program
def main():
    clock = pygame.time.Clock()
    run = True

    # add a loading screen for while the camera compiles
    #text = font.render('Loading environment...', True, BLUE)
    #textRect = text.get_rect()
    #textRect.center = (Window[0] // 2, Window[1] // 2)
    WIN = pygame.display.set_mode((Window[0], Window[1]))
    #WIN.blit(text, textRect)
    pygame.display.update()
    pygame.display.set_caption("Loading game...")
    #Menus.create_menu_buttons()

    # initialize/preload the camera
    if not Fast_Compile:
        loadEnv = Game.TimeTrial(tracks.MarioCircuit, "Mayro", 100, False, False)
        del loadEnv
    #initialize()

    # create game
    #pygame.mouse.set_visible(False)
    game = None #Game.TimeTrial(tracks.MarioCircuit, "Mario", 100)
    screen = "Main"
    menu_animations = True

    # game determining variables
    # defaults
    selected_cc = 100
    selected_char = "Mayro"
    selected_track = tracks.MarioCircuit
    VS_Ghost = False

    # fade variables
    Fading = False
    Fade = FadeObject()
    
    # create the menu object
    Menu = None
    if not Debug_Mode:
        Menu = Menus.MainMenu(menu_animations)
        Menu.Music.play(-1)
        # set fps to 30 for main menu
        FPS = 30
    else:
        # load the debug mode
        # create the game
        pygame.mouse.set_visible(False)
        game = Game.TimeTrial(getattr(tracks, Debug_Track), "Mayro", 100, False)
        screen = "Game"
        FPS = 60

    PauseMenu = Menus.Pause()

    while run:
        clock.tick(FPS)
        pygame.display.set_caption("FPS: " + str(int(clock.get_fps())))

        #Menus.title_screen(WIN)
        #pygame.display.update()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                # if the user decides to quit
                run = False
            if event.type == pygame.KEYDOWN and screen == "Game" and game.RoundRunning:
                if GhostManager.is_valid_key(event.key):
                    # create the frame
                    game.GhostData.add_point(game.Timer, False, game.Driver.Coins, pygame.key.get_pressed())

            if event.type == pygame.KEYUP and screen == "Game" and game.RoundRunning:
                if GhostManager.is_valid_key(event.key):
                    # create the frame
                    game.GhostData.add_point(game.Timer, False, game.Driver.Coins, pygame.key.get_pressed())

                    
            if event.type == pygame.MOUSEBUTTONDOWN and not Fading:
                # mouse clicked
                if screen == "Main":
                    # check for clicking menu buttons
                    todo = Menu.buttons_hovering()
                    if Menu.ButtonType == "CC_Menu" and todo != "Back" and todo != "None":
                        screen = "Character"
                        selected_cc = todo
                        Fading = True
                        """
                        cc = todo
                        # create the game
                        pygame.mouse.set_visible(False)
                        del Menu
                        game = Game.TimeTrial(tracks.MarioCircuit2, "Mario", todo)
                        screen = "Game"
                        FPS = 60
                        """
                    elif Menu.ButtonType == "Main" and todo == "CC":
                        Menu.create_cc_buttons()
                    elif Menu.ButtonType == "Main" and todo == "Quit":
                        run = False
                        
                elif screen == "Character":
                    # check for clicking menu buttons
                    todo = Menu.buttons_hovering()
                    if todo == "Back":
                        screen = "Main"
                        Fading = True
                    elif todo != "None":
                        selected_char = todo
                        screen = "Tracks"
                        Fading = True
                        
                elif screen == "Tracks":
                    # check for clicking menu buttons
                    todo = Menu.buttons_hovering()
                    if todo == "Back":
                        screen = "Character"
                        Fading = True
                    elif todo != "None":
                        selected_track = getattr(tracks, todo)
                        VS_Ghost = False#GhostManager.has_ghost(selected_track.Name, selected_cc)
                        screen = "GameLoad"
                        Fading = True

            if event.type == pygame.JOYBUTTONDOWN:
                #### CONTROLLER STUFF ####
                if screen == "Main":
                    # check controller inputs
                    todo = Menu.controller_inputs(event.button)
                    #if event.button == 1:
                        #todo = "CC"
                    # check for selecting menu buttons
                    #todo = Menu.buttons_hovering()
                    if Menu.ButtonType == "CC_Menu" and todo != "Back" and todo != "None":
                        screen = "Character"
                        selected_cc = todo
                        Fading = True
                    elif Menu.ButtonType == "Main" and todo == "CC":
                        Menu.create_cc_buttons()
                    elif Menu.ButtonType == "Main" and todo == "Quit":
                        run = False
            elif event.type == pygame.JOYAXISMOTION:
                pass


        #### MENU MANAGEMENT STUFF ####
        
        if screen == "Game":
            status = game.update(WIN)
            if game.Paused:
                PauseMenu.draw_menu(WIN)

                # check if mouse down
                if pygame.mouse.get_pressed()[0]:
                    # check for clicking menu buttons
                    todo = PauseMenu.buttons_hovering()
                    del PauseMenu
                    PauseMenu = Menus.Pause()
                    if todo == "Quit":
                        # return to title screen
                        screen = "MainTransition"
                        Fading = True
                    elif todo == "Resume":
                        # resume the game
                        game.pause()
                    elif todo == "Restart":
                        # restart the race
                        screen = "GameRestart"
                        Fading = True

            # check the status of the game
            if status == 0:
                run = False
            elif status == 2:
                screen = "MainTransition"
                Fading = True

        else:
            if screen != "GameLoad" and screen != "MainTransition" and screen != "GameRestart":
                Menu.draw_menu(WIN)
                

            if Fading:
                # manage fading
                s, pos = Fade.render()
                WIN.blit(s, pos)
                #pygame.display.update()
                
                # if at the peak
                if Fade.at_peak():
                    if screen == "Character":
                        Menu.Music.stop()
                        del Menu
                        Menu = Menus.CharacterSelection()
                        #time.sleep(0.05) # wait to make sure music has loaded
                        Menu.Music.play(-1)
                    elif screen == "Main":
                        # return to cc menu
                        Menu.Music.stop()
                        del Menu
                        Menu = Menus.MainMenu(menu_animations)
                        Menu.create_cc_buttons()
                        Menu.Music.play(-1)
                    elif screen == "Tracks":
                        # show the track list
                        Menu.Music.stop()
                        del Menu
                        Menu = Menus.TrackSelection(selected_cc)
                        Menu.Music.play(-1)
                    elif screen == "GameLoad":
                        # create the game
                        pygame.mouse.set_visible(False)
                        Menu.Music.stop()
                        del Menu
                        game = Game.TimeTrial(selected_track, selected_char, selected_cc, VS_Ghost)
                        screen = "Game"
                        FPS = 60
                        Fade.Increment = Fade.Increment/2
                    elif screen == "MainTransition":
                        FPS = 30
                        Fade.Increment = Fade.Increment*2
                        Menu = Menus.MainMenu(menu_animations)
                        pygame.mouse.set_visible(True)
                        
                        # stop all running music in the game
                        game.Sounds["Theme_Regular"].stop()
                        game.Sounds["Theme_Final_Lap"].stop()

                        # save the ghost
                        if game.SaveGhost:
                            game.GhostData.save_data(selected_track.Name)
                        
                        Menu.Music.play(-1)
                        del game # clear the game
                        screen = "Main"
                        # update the time trial times
                        Menus.update_time_data()
                    elif screen == "GameRestart":
                        # restart the game
                        pygame.mouse.set_visible(False)
                        
                        # stop all running music in the game
                        game.Sounds["Theme_Regular"].stop()
                        game.Sounds["Theme_Final_Lap"].stop()
                        
                        # delete game object and create a new one
                        del game
                        game = Game.TimeTrial(selected_track, selected_char, selected_cc, VS_Ghost)
                        screen = "Game"
                        
                # if at the finish
                elif Fade.at_finish():
                    Fading = False
                    Fade.reset()
        pygame.display.update()

    pygame.quit()


if __name__ == '__main__':
    main()
