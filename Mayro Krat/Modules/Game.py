# game manager
# contains game functions and mode classes

from PyGame3D import Engine_3D
import numpy
import pygame

from Modules.Items import Items
from Modules.Driver import Driver
from Modules import Animations
from Modules import GhostManager

items = Items()

Cheats = False

## CONFIG ##
Resolution = 2.5 # resolution multiplier; larger = more lag
Window = (800, 600) # Window size (default is 800 x 600)
FPS = 60 # FPS Cap

## Colors ##
WHITE = (255, 255, 255)
GRAY = (225, 225, 225)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 204, 0)
GREEN = (0, 255, 0)

# temporary variables
sx, sy, sz, sr = 952, 6, 751, 270

## Assets ##
COIN = Engine_3D.get_image("Assets/Sprites/Coin.png")
COIN = pygame.transform.scale(COIN, (45, 45))
DRIFT = Engine_3D.get_image("Assets/Sprites/DriftParticle.png")
MINI = Engine_3D.get_image("Assets/Sprites/MiniTurbo.png")
SUPER = Engine_3D.get_image("Assets/Sprites/SuperTurbo.png")
ULTRA = Engine_3D.get_image("Assets/Sprites/UltraTurbo.png")
BURNOUT = Engine_3D.get_image("Assets/Sprites/BurnoutParticle.png")

ROULETTE = Engine_3D.get_image("Assets/Items/Roulette.png")
ROULETTE = pygame.transform.scale(ROULETTE, (117, 81))#(91, 63))

pygame.init()

font3 = pygame.font.Font('Assets/Fonts/SNES.ttf', 35)


## Functions ##

def get_best_lap(LapTimes):
    best = 0
    bestTime = 9999999999
    for L in range(len(LapTimes)):
        if LapTimes[L] < bestTime:
            best = L
            bestTime = LapTimes[L]
    return best


class Game:
    def __init__(self, Track, Character="Mayro", CC=50, WatchingGhost=False):#, Ghost=False):
        self.CC = CC
        self.Character = Character
        self.WatchingGhost = WatchingGhost
        
        # create a new game
        self.Track = Track
        self.Camera = Engine_3D.Camera(Resolution, Window, (sx, sy, sz, sr), True)

        # loading track
        self.Track.load_track(self.Camera)

        # creating the driver
        if not WatchingGhost:
            d, dsize = self.Camera.get_sprites("Assets/Racers/"+Character+"/"+Character+"Drive.png", 12, 32, 32)
            dpos = Track.SpawnPosition
            dsp = Engine_3D.Sprite(d, 12, dpos, True, 0, True)
            dsp.Direction = numpy.deg2rad(Track.SpawnRotation)
            self.Camera.add_sprite(dsp)
            
            self.Driver = Driver(dsp, Character, CC)
            #self.Driver.attach_camera(self.Camera)
            self.Driver.set_collision_map(self.Camera.HeightMap, self.Camera.WallCollisions)
            self.Driver.JumpHeight = self.Track.JumpHeight
            self.Driver.TrackName = Track.Name

            self.Driver.apply_compensation(self.Camera.Compensation)

            rot = self.Driver.Rotation
            x = self.Driver.Sprite.Position.x
            y = self.Driver.Sprite.Position.y
            z = self.Driver.Sprite.Position.z
            self.Camera.set_offset(x, y, z, rot, 10, 3, 10)
            self.Camera.CFrame.Rotation.x = rot - numpy.deg2rad(180)

            self.DriverHead = Engine_3D.get_image("Assets/Racers/"+Character+"/"+Character+"Head.png")
        #self.DriverHead = pygame.transform.scale(self.DriverHead, (48, 48))
        
        self.Camera.PImg = [DRIFT, MINI, SUPER, ULTRA, BURNOUT]

        # track features
        self.Checkpoints = self.Track.Checkpoints
        self.Coins = self.Track.spawn_coins(self.Camera)
        self.CoinAnims = []
        self.Track.spawn_sprites(self.Camera)

        # animations
        self.Anims = []

        # load the sounds
        self.Sounds = {
            "Start_Jingle": pygame.mixer.Sound("Sounds/Race/Start_Jingle.mp3"),
            "Countdown": pygame.mixer.Sound("Sounds/Race/Countdown2.wav"),
            "GOOO": pygame.mixer.Sound("Sounds/Race/GOOO2.wav"),
            
            "Theme_Regular": pygame.mixer.Sound(self.Track.MusicFolder+"/Regular.mp3"),
            "Theme_Final_Lap": pygame.mixer.Sound(self.Track.MusicFolder+"/Final_Lap.mp3"),
            
            "Coin": pygame.mixer.Sound("Sounds/Kart/Coin.wav"),
            "Spinout": pygame.mixer.Sound("Sounds/Kart/Spinout.wav"),
            
            "Final_Lap": pygame.mixer.Sound("Sounds/Race/Laps/Final_Lap_Notice.mp3"),
            "Goal": pygame.mixer.Sound("Sounds/Race/Laps/Goal.mp3"),

            "New_Record": pygame.mixer.Sound("Sounds/Race/TimeTrial/New_Record.mp3"),
            "No_Record": pygame.mixer.Sound("Sounds/Race/TimeTrial/No_Record.mp3")
        }

        # game variables
        self.RoundRunning = False

        # create the ghost data
        self.GhostData = GhostManager.GhostData(Character, CC)

        # start of game variables
        self.StartAnimFrame = 130
        self.StartingFrames = 301
        self.StartingFrame = -2
        self.BoostFrame = 0
        self.EndingFrame = -1

        # key variables
        self.SpaceDown = False
        self.LShiftDown = False
        self.EscDown = False

        # pause variables
        self.Paused = False
        self.CanPause = False

        # preload
        self.Camera.preload()



    # function to show the animations
    def animate(self, WIN):
        if len(self.Anims) > 0:
            new = []
            for a in self.Anims:
                success, data = False, ()
                if not self.Paused:
                    success, data = a.increment()
                elif self.Paused:
                    success, data = a.get()
                    
                if success:
                    new.append(a)
                    if data[0] == 0: # if the data is a sprite
                        sprite = pygame.transform.scale(data[1], data[3]) # scale the sprite
                        WIN.blit(sprite, data[2])
                    elif data[0] == 1: # if the data is text
                        text_rect = data[1].get_rect()
                        text_rect.center = data[2]
                        WIN.blit(data[1], text_rect)
                    elif data[0] == 2: # if the data is rectangle
                        pos = (data[2][0] - data[3][0]/2, data[2][1] - data[3][1]/2)
                        WIN.blit(data[1], pos)
                        
            self.Anims = new


    # function to draw the ui
    def draw_ui(self, WIN):
        # draw the animations
        self.animate(WIN)
        
        # draw the coin counter
        WIN.blit(COIN, (10, Window[1]-50))
        if self.Driver.Coins >= 10:
            text = font3.render(str(self.Driver.Coins), False, YELLOW)
        else:
            text = font3.render(str(self.Driver.Coins), False, GRAY)
        #textRect = text.get_rect()
        #textRect.center = (90, Window[1]-33)
        #text.center = (90, Window[1]-36)
        WIN.blit(text, (70, Window[1]-49))#textRect)

        # draw the lap counter
        lap = self.Driver.Lap
        if lap < 4:
            if lap < 1:
                lap = 1
            lap_text = font3.render("Lap "+str(lap), False, GRAY)
            #lap_textRect = text.get_rect()
            #lap_textRect.center = (150, Window[1]-33)
            WIN.blit(lap_text, (150, Window[1]-49))#lap_textRect)

            # draw the item roulette
            if hasattr(self.Driver, "HeldItem"):
                WIN.blit(ROULETTE, (10, 10))
                item = pygame.transform.scale(self.Driver.HeldItem.Icon.copy(), (72, 72))#(54, 54))
                rect = ROULETTE.get_rect()
                ix = 10 + ROULETTE.get_width()/2 - item.get_width()/2
                iy = 10 + ROULETTE.get_height()/2 - item.get_height()/2
                WIN.blit(item, (ix, iy))
        
            # draw the minimap
            minimap = self.Track.MiniMap
            mmhx, mmhy = self.Track.get_minimap_pos(self.Driver.Sprite.Position.x, self.Driver.Sprite.Position.z)
            mmx = Window[0] - minimap.get_width()
            mmy = Window[1]/2 - minimap.get_height()/2

            # add the minimap itself
            WIN.blit(minimap, (mmx, mmy))
            WIN.blit(self.DriverHead, (mmx+mmhx-self.DriverHead.get_width()/2, mmy+mmhy-self.DriverHead.get_height()/2))

            if hasattr(self, "Ghost"):
                mmhgx, mmhgy = self.Track.get_minimap_pos(self.Ghost.Driver.Sprite.Position.x, self.Ghost.Driver.Sprite.Position.z)
                WIN.blit(self.Ghost.DriverHead, (mmx+mmhgx-self.Ghost.DriverHead.get_width()/2, mmy+mmhgy-self.Ghost.DriverHead.get_height()/2))

        # update the display
        # does in the other
        #pygame.display.update()


    # animate coins
    def show_coin_anims(self):
        # organization:     coin item,  kart collecting,    frame
        if not self.Paused:
            new = []
            for c in self.CoinAnims:
                c[2] += 1
                if c[2] < 44:
                    new.append(c)
                    rot = self.Camera.CFrame.Rotation.x
                    cos = numpy.cos(rot)
                    sin = numpy.sin(rot)
                    off = 0.1
                    c[0].Position.x = c[1].Sprite.Position.x + off*cos
                    c[0].Position.y = c[1].Sprite.Position.y - ((c[2]-22))**2 + 484
                    c[0].Position.z = c[1].Sprite.Position.z + off*sin
                else:
                    c[0].Enabled = False
            if len(new) < len(self.CoinAnims):
                self.CoinAnims = new


    # pause the game
    def pause(self):
        if self.CanPause and not self.EscDown:
            self.EscDown = True
            if self.Paused:
                pygame.mouse.set_visible(False)
                self.Paused = False
                self.RoundRunning = True
            else:
                pygame.mouse.set_visible(True)
                self.Paused = True
                self.RoundRunning = False


    # moving and controls
    def move(self, keys, t=20):
        moved = False
        turning = False

        u = 0.9
        tu = 0

        self.Driver.boost_particles(self.Camera)

        if keys[pygame.K_ESCAPE]:
            self.pause()
        elif self.EscDown:
            self.EscDown = False

        if keys[pygame.K_SPACE] and not self.SpaceDown and not self.Paused and self.Driver.Ground:
            self.SpaceDown = True
            if self.RoundRunning:
                if hasattr(self.Driver, "HoldingItem"):
                    # create ghost point
                    self.GhostData.use_mushroom(self.Timer, self.Driver.Coins)
                self.Driver.use_item(self.Camera)
        elif not keys[pygame.K_SPACE] and self.SpaceDown:
            self.SpaceDown = False

        if keys[pygame.K_p] and Cheats and not self.Paused:
            self.Driver.set_item(items.TripleMushroom)

        # driver holding item
        """
        if hasattr(self.Driver, "HoldingItem"):
            if not keys[pygame.K_SPACE]:
                # disgard item
                self.Driver.HoldingItem[1].drop(self.Camera, self.Driver, True, self.Driver.HoldingItem[0])
            else:
                # hold behind back
                rot = self.Driver.Rotation
                cos, sin = numpy.cos(rot), numpy.sin(rot)
                self.Driver.HoldingItem[0].set_position((self.Driver.Sprite.Position.x*34 - 22*cos, 0.8, self.Driver.Sprite.Position.z*34 - 22*sin))
        """
        
        if keys[pygame.K_LSHIFT] and self.RoundRunning and not self.Paused and self.Driver.Ground:
            if not self.LShiftDown and not self.Driver.Drifting:
                self.LShiftDown = True
                if self.Driver.UpPropulsion == 0.0:
                    self.Driver.UpPropulsion = 0.2
                    self.Driver.Sounds["Jump"].play()
                    
                self.Driver.Drifting = True
                #self.Driver.Sounds["Skid"].play(-1)
            #if MDriver.UpPropulsion == 0.0:
            u = 1.25
            #Camera.create_particle(3, (MDriver.Sprite.Position.x, 0, MDriver.Sprite.Position.z), 8)
            self.Driver.drift_particles(self.Camera)
        elif not self.Paused:
            self.Driver.Drifting = False
            #self.Driver.Sounds["Skid"].stop()
            self.LShiftDown = False

        self.Driver.Turn = 0
        
        if (keys[pygame.K_a] or keys[pygame.K_LEFT]) and self.Driver.BurnoutFrame == 0 and self.RoundRunning and not self.Paused and self.Driver.Ground:
            #Cam.turn_left(1.5, t)
            #MDriver.turn_left(u, t)
            if self.Driver.TurnDegree > 0:
                tu += -u/2
                self.Driver.Turn += 1
                if not (keys[pygame.K_d] or keys[pygame.K_RIGHT]) and self.Driver.Drifting and self.Driver.UpPropulsion == 0:
                    # disable drifting
                    self.Driver.Drifting = False
            else:
                tu += -u
                self.Driver.Turn += 2
            turning = True

        if (keys[pygame.K_d] or keys[pygame.K_RIGHT]) and self.Driver.BurnoutFrame == 0 and self.RoundRunning and not self.Paused and self.Driver.Ground:
            #Cam.turn_right(1.5, t)
            #MDriver.turn_right(u, t)
            if self.Driver.TurnDegree < 0:
                tu += u/2
                self.Driver.Turn += 1
                if not (keys[pygame.K_a] or keys[pygame.K_LEFT]) and self.Driver.Drifting and self.Driver.UpPropulsion == 0:
                    # disable drifting
                    self.Driver.Drifting = False
            else:
                tu += u
                self.Driver.Turn += 2
            turning = True
        """
        if keys[pygame.K_i]:
            Cam.turn_down(1.5, t)

        if keys[pygame.K_o]:
            Cam.turn_up(1.5, t)
        """

        if not (keys[pygame.K_a] or keys[pygame.K_d] or keys[pygame.K_LEFT] or keys[pygame.K_RIGHT]) and self.Driver.Drifting and self.Driver.UpPropulsion == 0:
            self.Driver.Drifting = False
        
        if self.Driver.Ground and  ((keys[pygame.K_w] or keys[pygame.K_UP]) and self.Driver.CanAccelerate and self.RoundRunning) or (self.RoundRunning == False and self.StartingFrame <= 0 and self.StartAnimFrame <= 0 and not self.Paused):
            #Cam.forward(10.0, t)
            moved = True
            self.Driver.accelerate(t)
        elif (keys[pygame.K_w] or keys[pygame.K_UP]) and self.StartingFrame > 0 and self.BoostFrame == 0:
            # starter boost if not already
            self.BoostFrame = self.StartingFrame

        if self.Driver.Ground and (keys[pygame.K_s] or keys[pygame.K_DOWN]) and self.RoundRunning and not turning and not self.Paused:
            #Cam.backward(10.0, t)
            moved = True
            self.Driver.decelerate_negative(0.25, t)

        if turning and not self.Paused:
            # brake drifting
            if keys[pygame.K_s] or keys[pygame.K_DOWN]:
                tu = tu*1.25
            self.Driver.turn(tu, t)

        if not moved and self.Driver.BoostCount <= 0 and not self.Paused:
            self.Driver.decelerate(0.25, t)

        if not self.Paused:
            self.Driver.move_parallel(self.Driver.Speed, t)
            self.Driver.propell_y()
        #if not turning and self.Driver.UpPropulsion == 0.0 and not self.Paused:
            #self.Driver.Drifting = False
            #self.Driver.Sounds["Skid"].stop()
        if not self.Paused:
            self.Driver.update_camera(turning)

        # set the sprite to the position of the camera
        # first get the offset
        #cx, cz, rot = Camera.CFrame.Position.x, Camera.CFrame.Position.z, Camera.CFrame.Rotation.x
        #cos, sin = numpy.cos(rot), numpy.sin(rot)
        #MSp.set_position((cx*34 + cos*100, 1, cz*34 + sin*100))
        #MSp.Direction = rot


    # check for if a kart collides with a coin or item box
    def check_collisions(self, kart):
        # loop through coins and check if in bounds
        offset = 0.2
        for i in self.Coins:
            if (i.Enabled and i.Active and kart.Sprite.Position.x > i.Position.x - offset and kart.Sprite.Position.x < i.Position.x + offset
                and kart.Sprite.Position.z > i.Position.z - offset and kart.Sprite.Position.z < i.Position.z + offset):
                i.Active = False
                i.Shadows = False
                self.Sounds["Coin"].play()
                if kart.Coins < 10:
                    kart.Coins += 1
                self.CoinAnims.append([i, kart, 0])
                if kart.Ground:
                    kart.boost(1, 10)
                self.GhostData.coin_boost(self.Timer, self.Driver.Coins)


    # update each frame
    def update(self, WIN):
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                # if the user decides to quit
                return 0

            # key down events
            if event.type == pygame.KEYDOWN:
                
                #if event.key == pygame.K_q:
                    #Camera.CFrame.Position.y -= 1
                #if event.key == pygame.K_e:
                    #Camera.CFrame.Position.y += 1
                
                if event.key == pygame.K_LSHIFT and self.RoundRunning:
                    if self.Driver.UpPropulsion == 0.0:
                        self.Driver.UpPropulsion = 0.2
                    self.Driver.Drifting = True
                if event.key == pygame.K_SPACE and self.RoundRunning:
                    self.Driver.use_item(self.Camera)
                if event.key == pygame.K_p:
                    #print(MDriver.Sprite.dir2p)
                    #print(MSp.dir2p)
                    self.Driver.set_item(items.TripleMushroom)

                if event.key == pygame.K_w:
                    # starter boost if not already
                    if self.StartingFrame > 0 and self.BoostFrame == 0:
                        self.BoostFrame = self.StartingFrame

            # Item Events
            # when item is held
            #if event.type == ItemHeld:
                #pass
        """
        self.Camera.draw() # draw the camera environment

        if self.Driver.AccelCooldown > 0 and not self.WatchingGhost:
            self.Driver.AccelCooldown -= 1
            if self.Driver.AccelCooldown == 0:
                self.Driver.CanAccelerate = True

        #if self.RoundRunning:
        if not self.WatchingGhost:
            self.move(pygame.key.get_pressed())#, clock.tick())
        #else:
            #self.Driver.update_camera(False)
        if hasattr(self, "Ghost"):
            if not self.Paused:
                self.Ghost.update(self.StartingFrame, self.Timer)

        if not self.Paused:
            self.Camera.increment_particles()
        newLap = self.Driver.update(self.Checkpoints)
        if newLap:
            if self.Driver.Lap != 1 and hasattr(self, "LapTimes") and hasattr(self, "Timer"):
                # calculate total
                total = 0
                for lt in self.LapTimes:
                    total += lt
                self.LapTimes.append(self.Timer - total)
                self.PauseTimer = self.Timer
            if self.Driver.Lap == 2:# (self.Driver.Lap >= 2 and self.Driver.Lap <= 4):
                # create new lakitu animation
                newAnim = Animations.Animation("Lakitu_Lap"+str(self.Driver.Lap))
                self.Anims.append(newAnim)
            elif self.Driver.Lap == 3:#5:
                # create new lakitu animation
                newAnim = Animations.Animation("Lakitu_LapFinal")
                self.Anims.append(newAnim)
                self.Sounds["Theme_Regular"].stop()
                self.Sounds["Final_Lap"].play()
                self.StartAnimFrame = -150
            elif self.Driver.Lap == 4:
                # stop the music
                self.Sounds["Theme_Final_Lap"].stop()
                self.Sounds["Goal"].play()
                # end race
                self.Driver.detach_camera()
                newAnim = Animations.Animation("Lakitu_Finish")
                self.Anims.append(newAnim)
                self.RoundRunning = False
                self.CanPause = False

                # show the animations
                if hasattr(self, "LapTimes") and hasattr(self, "Timer"):
                    best = get_best_lap(self.LapTimes)
                    
                    L1 = GhostManager.convert_to_time(self.LapTimes[0])
                    L2 = GhostManager.convert_to_time(self.LapTimes[1])
                    L3 = GhostManager.convert_to_time(self.LapTimes[2])
                    Total = GhostManager.convert_to_time(self.Timer)

                    L1c = WHITE
                    L2c = WHITE
                    L3c = WHITE
                    Totalc = YELLOW

                    # if is new record then set color to green
                    if not self.WatchingGhost:
                        if GhostManager.is_new_record(self.Track.Name, self.Timer, self.CC):
                            Totalc = GREEN
                            self.EndJingle = "New_Record"
                            # add a final point
                            self.GhostData.add_point(self.Timer, False, self.Driver.Coins, pygame.key.get_pressed())
                            # save the ghost
                            self.SaveGhost = True
                        # apply the new record
                        GhostManager.set_record(self.Track.Name, self.Timer, self.Character, self.CC)

                    # determine the color
                    if best == 0:
                        L1c = YELLOW
                    elif best == 1:
                        L2c = YELLOW
                    elif best == 2:
                        L3c = YELLOW

                    animBG = Animations.Animation("Time_BG", [(400, 260), BLACK])
                    self.Anims.append(animBG)
                    
                    animL1 = Animations.Animation("Lap1_Time", [L1, L1c])
                    animL2 = Animations.Animation("Lap2_Time", [L2, L2c])
                    animL3 = Animations.Animation("Lap3_Time", [L3, L3c])
                    
                    animLine = Animations.Animation("Time_Bar", [(350, 6), WHITE])

                    animTotal = Animations.Animation("Overall_Time", [Total, Totalc])
                    
                    self.Anims.append(animL1)
                    self.Anims.append(animL2)
                    self.Anims.append(animL3)

                    self.Anims.append(animLine)

                    self.Anims.append(animTotal)

                    self.EndingFrame = 0
                    self.DisappearFrame = 290

        # starting stuff #

        # pre-countdown animation
        if self.StartAnimFrame > 0:
            # variables needed
            rot = self.Driver.Rotation
            x = self.Driver.Sprite.Position.x
            y = self.Driver.Sprite.Position.y
            z = self.Driver.Sprite.Position.z
            if self.StartAnimFrame > 105:
                if self.StartAnimFrame == 106:
                    # play the start jingle
                    self.Sounds["Start_Jingle"].play()
                self.Camera.set_offset(x, y, z, rot, 7, 3, 7)
                self.Camera.CFrame.Rotation.x = rot - numpy.deg2rad(180)
                self.StartAnimFrame -= 1
            elif self.StartAnimFrame > 60:
                off = 3.2 + (3.8*((self.StartAnimFrame-61)/44))
                self.Camera.set_offset(x, y, z, rot, off, 3, off)
                self.Camera.CFrame.Rotation.x = rot - numpy.deg2rad(180)
                self.StartAnimFrame -= 1
            else:
                off = numpy.deg2rad(180*((self.StartAnimFrame-1)/59))
                self.Camera.set_offset(x, y, z, rot - off, -3.2, 3, -3.2)
                self.Camera.CFrame.Rotation.x = rot - off
                self.StartAnimFrame -= 1
                if self.StartAnimFrame == 0:
                    # attach the camera
                    self.Driver.attach_camera(self.Camera)
                    self.StartingFrame = self.StartingFrames
                    
        elif self.StartAnimFrame <= -5 and self.StartAnimFrame > -110:
            self.StartAnimFrame -= 1
            if self.StartAnimFrame == -110:
                # start the music
                self.Sounds["Theme_Regular"].play(-1)
        elif self.StartAnimFrame <= -150 and self.StartAnimFrame > -270:
            self.StartAnimFrame -= 1
            if self.StartAnimFrame == -270:
                # start the final lap music
                #self.Sounds["Final_Lap"].stop()
                self.Sounds["Theme_Final_Lap"].play(-1)

        # countdown
        if self.StartingFrame == 301:
            L_start = Animations.Animation("Lakitu_Start")
            self.Anims.append(L_start)
            self.StartingFrame -= 1
        elif self.StartingFrame > 0:
            self.StartingFrame -= 1
            if not pygame.key.get_pressed()[pygame.K_w]:
                self.BoostFrame = 0

            # decide if sound needs to play
            if self.StartingFrame == 180 or self.StartingFrame == 120 or self.StartingFrame == 60:
                self.Sounds["Countdown"].play()
                
            # create the particles for attempting to starter boost
            if self.BoostFrame > 0:
                self.Driver.drift_particles(self.Camera, True)
        elif self.StartingFrame == 0:
           # if hasattr(self, "Ghost"):
                #self.Ghost.update(self.StartingFrame, self.Timer)
            self.StartingFrame -= 1
            self.RoundRunning = True
            self.CanPause = True
            # play the sound
            self.Sounds["GOOO"].play()
            self.StartAnimFrame = -5
            self.GhostData.add_point(self.Timer, False, self.Driver.Coins, pygame.key.get_pressed())
            self.GhostData.StartBoostFrame = self.BoostFrame
            # give driver boost or burnout
            if self.BoostFrame < 120:
                self.Driver.boost(3, self.BoostFrame/2)
            else:
                # burnout
                self.Driver.CanAccelerate = False
                self.Driver.AccelCooldown = 90
                self.Driver.BurnoutFrame = 75
                self.Sounds["Spinout"].play()
                self.GhostData.BurnedOut = True
                # create the particles
                self.Driver.drift_particles(self.Camera, False, True)

        # ending countdown and returning to menu
        if self.EndingFrame >= 0:
            self.EndingFrame += 1
            if self.EndingFrame >= 800:
                # return to menu
                return 2

        self.draw_ui(WIN)
        self.show_coin_anims()

        if not self.WatchingGhost:
            self.check_collisions(self.Driver)
        return 1


class TimeTrial(Game):
    def __init__(self, Track, Character="Mayro", CC=50, Ghost=False, WatchingGhost=False):
        super().__init__(Track, Character, CC, WatchingGhost)#, Ghost)
        
        if Ghost:
            # create ghost object
            self.Ghost = GhostManager.Ghost(Track, CC, self.Camera)

            if WatchingGhost:
                self.Driver = self.Ghost.Driver
                self.DriverHead = self.Ghost.DriverHead
                
        # give the initial item for time trials
        self.Driver.set_item(items.TripleMushroom)
        self.Timer = 0
        self.LapTimes = []
        self.DisappearFrame = -1

        self.SaveGhost = False

        self.EndJingle = "No_Record"

    def draw_ui(self, WIN):
        super().draw_ui(WIN)

        col = WHITE

        if self.Driver.Lap < 4 and self.RoundRunning:
            self.Timer += 1
            #self.GhostData.update()
        elif self.RoundRunning:
            col = YELLOW

        # draw the timer
        dispTime = self.Timer
        if hasattr(self, "PauseTimer"):
            if self.PauseTimer + 90 <= self.Timer:
                delattr(self, "PauseTimer")
            else:
                dispTime = self.PauseTimer
                col = YELLOW

        if self.DisappearFrame > 0:
            self.DisappearFrame -= 1
            if self.DisappearFrame == 230:
                # play the end jingle
                self.Sounds[self.EndJingle].play()
        if self.DisappearFrame != 0:
            timeStr = GhostManager.convert_to_time(dispTime)
            text = font3.render(timeStr, False, col)
            textSize = font3.size(timeStr)
            WIN.blit(text, (Window[1] - textSize[0]/4 - 10, textSize[1]/2 + 10))

        # update the display
        #pygame.display.update()


class Race(Game):
    def __init__(self, Track, Character="Mayro", CC=50):
        super().__init__(Track, Character, CC)
        # create the computer racers
        # for testing it is loogi
        #Loogi = 

