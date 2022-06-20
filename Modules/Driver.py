# driver class
import numpy
import random
import pygame

pygame.init()

## CONFIG ##
CC_Multipliers = {
    50: 1,
    100: 0.85,
    150: 0.7,
    200: 0.58
}

Checkpoint_Angles = {
    "RainbowRoad": [
        270.01,
        270.01,
        0.01,
        0.01,
        90.01,
        180.01,
        90.01,
        0.01,
        90.01,
        180.01,
        180.01,
        180.01,
        180.01,
        180.01,
        180.01,
        270.01
    ],

    "DonutPlains1": [
        270.01,
        0.01,
        180.01,
        270.01
    ],

    "DonutPlains2": [
        270.01,
        180.01,
        90.01,
        0.01,
        0.01
    ],

    "DonutPlains3": [
        270.01,
        0.01,
        180.01,
        90.01
    ],

    "VanillaLake1": [
        270.01,
        90.01,
        180.01,
        180.01,
        180.01
    ],

    "VanillaLake2": [
        270.01,
        250.01,
        180.01,
        90.01,
        90.01,
        0.01,
        35.01
    ],

    "GhostValley1": [
        270.01,
        270.01,
        270.01,
        90.01,
        90.01,
        90.01,
        45.01,
        270.01
    ],

    "GhostValley2": [
        270.01,
        90.01,
        0.01,
        90.01,
        180.01,
        90.01,
        180.01,
        270.01
    ],

    "BowserCastle": [
        270.01,
        270.01,
        90.01,
        90.01
    ],

    "BowserCastle2": [
        270.01,
        0.01,
        90.01,
        180.01,
        180.01,
        180.01
    ],

    "FrankBeach1": [
        270.01,
        0.01,
        80.01,
        180.01,
        200.01,
        270.01
    ],

    "FrankBeach2": [
        270.01,
        180.01,
        90.01,
        100.01,
        90.01,
        25.01,
        270.01,
        270.01
    ]
}

# check whether specified coordinate has collision in heightmap
def has_collision(hm, x, z, wc):
    if (int(x) >= 0 and int(x) < len(hm)
        and int(z) >= 0 and int(z) < len(hm[0])
        and hm[int(x)][int(z)][0] <= 250 and wc[hm[int(x)][int(z)][0]]):
        return True
    return False

def is_offroad(hm, x, z):
    if (int(x) >= 0 and int(x) < len(hm)
        and int(z) >= 0 and int(z) < len(hm[0])
        and hm[int(x)][int(z)][0] == 252):
        return False
    return True

def is_ice_block(hm, x, z):
    if (int(x) >= 0 and int(x) < len(hm)
        and int(z) >= 0 and int(z) < len(hm[0])
        and hm[int(x)][int(z)][0] == 69):
        return True
    return False

# types:
#   1 = boost pannel
#   2 = ramp
#   3 = no road
def get_road_type(hm, x, z):
    if (int(x) >= 0 and int(x) < len(hm)
        and int(z) >= 0 and int(z) < len(hm[0])):
        if hm[int(x)][int(z)][0] == 253:
            return 1
        elif hm[int(x)][int(z)][0] == 251:
            return 2
        elif hm[int(x)][int(z)][0] == 254:
            return 3
    return 0

## Variables ##
turning_speed = numpy.deg2rad(5)

class Character:
    def __init__(self, MaxSpeed=5.0, Acceleration=0.2):
        self.MaxSpeed = MaxSpeed
        self.Acceleration = Acceleration

Characters = {
    "Mayro": Character(4.0, 0.3),
    "Loogi": Character(3.6, 0.4),
    "Pear": Character(4.2, 0.25),
    "Tumor": Character(3.8, 0.35),
    "Sushi": Character(4.2, 0.25),
    "Dog": Character(4.4, 0.2),
    "Frank": Character(3.6, 0.4),
    "Ape": Character(4.4, 0.2)
}

class Driver:
    def __init__(self, sprite, Char="Mayro", CC=50):
        self.Sprite = sprite
        self.Rotation = self.Sprite.Direction

        self.Compensation = 1
        self.Comp2 = 1
        self.CC = CC
        self.JumpHeight = 0.5

        self.TrackName = "RainbowRoad"

        # driving variables
        ## Preferences ##
        self.MaxDriverSpeed = float(Characters[Char].MaxSpeed)
        self.MaxSpeed = float(Characters[Char].MaxSpeed)
        self.Acceleration = float(Characters[Char].Acceleration)

        ## Variables ##
        self.Speed = 0.0
        self.Coins = 0

        self.CanAccelerate = True
        self.AccelCooldown = 0

        self.UpPropulsion = 0.0

        self.Drifting = False
        self.TurnDegree = 0.0
        self.ParticleLeft = True
        self.DriftCount = 0

        self.Turn = 0

        self.BoostCount = 0
        self.Shrooming = False
        self.TouchedOffroad = False
        self.BurnoutFrame = 0

        self.TouchingBoost = False

        self.Colliding = True
        self.Ground = True
        self.Saving = False
        self.RespawnFrame = 0
        self.RespawnPos = ((0, 0), 0.0)
        self.Increment = (0, 0)

        # lap stuff
        self.Checkpoint = -1
        self.Lap = 0

        # sounds
        self.Sounds = {
            "Boost": pygame.mixer.Sound("Sounds/Kart/Shroom.wav"),
            "Jump": pygame.mixer.Sound("Sounds/Kart/Jump.wav"),
            #"Skid": pygame.mixer.Sound("Sounds/Kart/Skid.wav")
            #"Engine": "Sounds/Kart/Engine.wav",
        }

    def apply_compensation(self, comp):
        self.Compensation = (34.1/comp)*CC_Multipliers[self.CC]
        self.Comp2 = 34.1/comp
        self.Acceleration = self.Acceleration/self.Compensation
        self.reset_max_speed()

    # calculate the respawn position
    def get_respawn_pos(self, checkpoints):
        cp = checkpoints[self.Checkpoint]
        # get the coordinates
        x = (cp[0][0] + cp[1][0])/2
        z = (cp[0][1] + cp[1][1])/2

        Track = "RainbowRoad"
        if self.TrackName in Checkpoint_Angles:
            Track = self.TrackName
        angle = numpy.deg2rad(Checkpoint_Angles[Track][self.Checkpoint])
        """
        if cp[0][0] == cp[1][0]:
            x = cp[0][0]
        else:
            mp = (cp[1][0] - cp[0][0])/2
            x = cp[0][0] + mp

        if cp[0][1] == cp[1][1]:
            z = cp[0][1]
        else:
            mp = (cp[0][1] - cp[1][1])/2
            z = cp[0][1] + mp
        """

        return ((x/34, z/34), angle)

    # calculate the increment for the respawn
    def get_increment(self):
        x = self.RespawnPos[0][0] - self.Sprite.Position.x
        z = self.RespawnPos[0][1] - self.Sprite.Position.z
        return (x/60, z/60)

    def attach_camera(self, camera):
        self.Camera = camera
        self.update_camera()
        # snap it into position
        #rot = self.Rotation
        #x = self.Sprite.Position.x
        #y = self.Sprite.Position.y
        #z = self.Sprite.Position.z

        #cos, sin = numpy.cos(rot), numpy.sin(rot)
        #self.Camera.set_position((x, y/20 + 3, z))
        #self.Camera.CFrame.Rotation.x = rot

    def detach_camera(self):
        if hasattr(self, "Camera"):
            delattr(self, "Camera")

    def boost(self, amt=3, time=35, ignoreOffroad=False):
        if self.BoostCount < time:
            self.MaxSpeed = (self.MaxDriverSpeed + self.Coins/10 + amt)/self.Compensation# + amt/self.Compensation
            self.Speed = self.MaxSpeed
            self.Shrooming = ignoreOffroad
            self.BoostCount = time

    # manage checkpoint stuff
    def manage_checkpoints(self, checkpoints):
        # deciding next checkpoint index
        n = self.Checkpoint + 1
        if n > len(checkpoints)-1 or n < 0:
            n = 0

        # check if in bounds of checkpoint
        px = self.Sprite.Position.x*34
        pz = self.Sprite.Position.z*34
        point1 = checkpoints[n][0]
        point2 = checkpoints[n][1]
        if (px > point1[0] - 5 and px < point2[0] + 5
            and pz > point1[1] - 5 and pz < point2[1] + 5):
            # update checkpoint counter
            self.Checkpoint = n
            if checkpoints[n][2] == 2:
                self.Lap += 1
                return True
        return False

    # function for mainly updating
    def update(self, checkpoints, Ghost=False):
        # first update the driver angle when burned out
        if self.BurnoutFrame > 0:
            self.Sprite.Direction -= numpy.deg2rad(14.4)
            self.BurnoutFrame -= 1
        # second update the boost counter
        if self.BoostCount != 0:
            self.BoostCount -= 1
            if self.BoostCount <= 0:
                self.BoostCount = 0
                self.Shrooming = False
                self.reset_max_speed()
        # third update the drift counter
        if self.Drifting and self.UpPropulsion == 0.0 and self.Speed > self.MaxSpeed*0.5:
            if self.DriftCount < 100:
                self.DriftCount += 1
        else:
            if self.DriftCount != 0:
                # set the max speed
                if self.DriftCount >= 100:
                    self.boost(3, 100)
                elif self.DriftCount >= 55:
                    self.boost(3, 65)
                elif self.DriftCount >= 30:
                    self.boost(3, 35)
                
                self.DriftCount = 0

        # lakitu save
        if not self.Ground and self.Saving:
            if self.RespawnFrame == 0:
                self.RespawnFrame = 1
                self.RespawnPos = self.get_respawn_pos(checkpoints)
                self.Sprite.Direction = self.RespawnPos[1]
                self.TurnDegree = 0.0
                self.Rotation = self.RespawnPos[1]
                self.Increment = self.get_increment()
            elif self.RespawnFrame == 1:
                self.Sprite.Position.y += 30
                if self.Sprite.Position.y >= 400:
                    self.RespawnFrame = 2
                    self.Sprite.Position.y = 400
                    self.Sprite.Shadows = True
            elif self.RespawnFrame == 2:
                """
                self.Sprite.Position.x = self.RespawnPos[0][0]
                self.Sprite.Position.z = self.RespawnPos[0][1]
                self.Ground = True
                self.Saving = False
                self.UpPropulsion = -0.05
                """
                self.Sprite.Position.x += self.Increment[0]
                self.Sprite.Position.z += self.Increment[1]

                # check if the driver is at pos
                p = 0
                if self.Increment[0] < 0:
                    if self.Sprite.Position.x <= self.RespawnPos[0][0]:
                        p += 1
                        self.Sprite.Position.x = self.RespawnPos[0][0]
                elif self.Increment[0] > 0:
                    if self.Sprite.Position.x >= self.RespawnPos[0][0]:
                        p += 1
                        self.Sprite.Position.x = self.RespawnPos[0][0]
                elif self.Increment[0] == 0:
                    p += 1

                if self.Increment[1] < 0:
                    if self.Sprite.Position.z <= self.RespawnPos[0][1]:
                        p += 1
                        self.Sprite.Position.z = self.RespawnPos[0][1]
                elif self.Increment[1] > 0:
                    if self.Sprite.Position.z >= self.RespawnPos[0][1]:
                        p += 1
                        self.Sprite.Position.z = self.RespawnPos[0][1]
                elif self.Increment[1] == 0:
                    p += 1
                
                if p == 2:
                    # animation is finished
                    self.Ground = True
                    self.Saving = False
                    self.Coins -= 3
                    if self.Coins < 0:
                        self.Coins = 0
                    self.UpPropulsion = -0.05
                #"""
                
        # next update checkpoint count
        if not Ghost:
            return self.manage_checkpoints(checkpoints)

    def drift_particles(self, camera, starter=False, burnout=False, iteration=0):
        y = self.Sprite.Position.y - 150
        if (self.UpPropulsion == 0.0 and self.Speed > self.MaxSpeed*0.5 and self.Drifting == True) or starter == True or burnout == True:
            #self.ParticleLeft = not self.ParticleLeft
            size = random.randint(2, 4)
            off = (random.randint(12, 21)*0.01)/self.Comp2
            rot = camera.CFrame.Rotation.x
            cos = numpy.cos(rot)
            sin = numpy.sin(rot)
            dc = 0

            # determine the color
            if self.DriftCount >= 100:
                dc = 3
            elif self.DriftCount >= 55:
                dc = 2
            elif self.DriftCount >= 30:
                dc = 1

            # determine offset and spawn the particles
            if burnout == True:
                lt_offset = 60 + (iteration*4)
                x1 = self.Sprite.Position.x - off*sin
                z1 = self.Sprite.Position.z + off*cos
                camera.create_particle(size, (x1, y, z1), lt_offset, 4)
                x2 = self.Sprite.Position.x + off*sin
                z2 = self.Sprite.Position.z - off*cos
                camera.create_particle(size, (x2, y, z2), lt_offset, 4)

                if iteration < 5:
                    # recursively make more particles
                    self.drift_particles(camera, False, True, iteration+1)
            elif starter==True:
                x1 = self.Sprite.Position.x - off*sin
                z1 = self.Sprite.Position.z + off*cos
                camera.create_particle(size, (x1, y, z1), 8, 0)
                x2 = self.Sprite.Position.x + off*sin
                z2 = self.Sprite.Position.z - off*cos
                camera.create_particle(size, (x2, y, z2), 8, 0)
            elif self.TurnDegree < 0:
                x = self.Sprite.Position.x - off*sin
                z = self.Sprite.Position.z + off*cos
                camera.create_particle(size, (x, y+50, z), 8, dc)
            else:# self.TurnDegree > 0:
                x = self.Sprite.Position.x + off*sin
                z = self.Sprite.Position.z - off*cos
                camera.create_particle(size, (x, y+50, z), 8, dc)

    def boost_particles(self, camera):
        if self.BoostCount > 0 and self.Speed > self.MaxSpeed*0.5:
            #self.ParticleLeft = not self.ParticleLeft
            size = random.randint(10, 22)*0.1
            off = (random.randint(9, 14)*0.01)/self.Comp2
            rot = camera.CFrame.Rotation.x
            cos = numpy.cos(rot)
            sin = numpy.sin(rot)
            y = 5 + (self.Sprite.Position.y-100)

            # determine offset and spawn the particles
            if self.TurnDegree < -numpy.deg2rad(5):
                x = self.Sprite.Position.x - off*sin
                z = self.Sprite.Position.z + off*cos
                camera.create_particle(size, (x, y, z), 5, 2)
            elif self.TurnDegree > numpy.deg2rad(5):
                x = self.Sprite.Position.x + off*sin
                z = self.Sprite.Position.z - off*cos
                camera.create_particle(size, (x, y, z), 5, 2)
            else:
                # left
                x = self.Sprite.Position.x - off*sin
                z = self.Sprite.Position.z + off*cos
                camera.create_particle(size, (x, y, z), 5, 2)
                # right
                x = self.Sprite.Position.x + off*sin
                z = self.Sprite.Position.z - off*cos
                camera.create_particle(size, (x, y, z), 5, 2)

    # updates the rotation of the kart
    def update_rotation(self, units=0.0):
        m = 1
        if self.Turn - 1 > 0:
            m = self.Turn - 1
        td = numpy.deg2rad(37)/m
        if self.Drifting:
            td = numpy.deg2rad(79)/m
            
        if units > 0:
            if self.TurnDegree <= td:
                self.TurnDegree += turning_speed
                if self.TurnDegree > td:
                    self.TurnDegree = td
            elif self.TurnDegree > td:
                self.TurnDegree -= turning_speed
                
        elif units < 0:
            if self.TurnDegree > -td:
                self.TurnDegree -= turning_speed
                if self.TurnDegree < -td:
                    self.TurnDegree = -td
            elif self.TurnDegree < -td:
                self.TurnDegree += turning_speed
                
        else:
            if self.TurnDegree > 0:
                if self.TurnDegree - turning_speed < 0:
                    self.TurnDegree = 0
                else:
                    self.TurnDegree -= turning_speed
                self.Sprite.Direction = self.Rotation + self.TurnDegree
            elif self.TurnDegree < 0:
                if self.TurnDegree + turning_speed > 0:
                    self.TurnDegree = 0
                else:
                    self.TurnDegree += turning_speed
                self.Sprite.Direction = self.Rotation + self.TurnDegree

    def update_camera(self, turning=False):
        if hasattr(self, "Camera") and (self.Ground and not self.Saving or (self.RespawnFrame != 0 and self.RespawnFrame != 1)):
            # snap it into position
            rot = self.Rotation
            x = self.Sprite.Position.x
            y = self.Sprite.Position.y
            z = self.Sprite.Position.z
            """
            cos, sin = numpy.cos(rot), numpy.sin(rot)
            self.Camera.set_position((x - cos*3.2, y/20 + 3, z - sin*3.2))
            """
            self.Camera.set_offset(x, y, z, rot, -3.2, 3, -3.2)
            self.Camera.CFrame.Rotation.x = rot

            # reset the rotation of the sprite if not turning
            if not turning:
                self.update_rotation(0.0)

    def reset_max_speed(self):
        # reset the speed
        self.MaxSpeed = (self.MaxDriverSpeed + self.Coins/10)/self.Compensation

    def set_collision_map(self, CollisionMap, WallCollisions):
        self.CollisionMap = CollisionMap
        self.WallCollisions = WallCollisions


    ## Items ##

    def set_item(self, item):
        self.HeldItem = item

    def delete_item(self):
        delattr(self, "HeldItem")

    def use_item(self, Camera):
        if hasattr(self, "HeldItem"):
            self.HeldItem.use(Camera, self)
        

    ## Movement ##

    def too_slow(self):
        if self.Speed > 3.2 and not self.TouchedOffroad:
            self.Speed = 3.3

    def bounce(self, NewHeight, NewSpeed):
        if self.UpPropulsion == 0.0:
            self.UpPropulsion = NewHeight
        self.Speed = NewSpeed
        self.CanAccelerate = False
        self.Drifting = False
        self.DriftCount = 0
        self.BoostCount = 0
        self.Shrooming = False
        self.reset_max_speed()
        self.AccelCooldown = 25

    def fast_enough(self):
        self.bounce(self.Speed/19, -self.Speed/1.15)

    def move_parallel(self, units=0.0, t=20):
        rot = self.Rotation#.Sprite.Direction
        x = self.Sprite.Position.x
        y = self.Sprite.Position.y
        z = self.Sprite.Position.z

        nX = x + numpy.cos(rot)*(units/100)*(t/10)
        nZ = z + numpy.sin(rot)*(units/100)*(t/10)

        # check  collision
        if hasattr(self, "CollisionMap"):
            hm = self.CollisionMap
            wc = self.WallCollisions
            # convert it to the coordinates read by heightmap array
            ccX = x/30*(len(hm)-1)
            cnX = nX/30*(len(hm)-1)
            ccZ = z/30*(len(hm[0])-1)
            cnZ = nZ/30*(len(hm[0])-1)
            offs = 1
            #print(ccZ, cnZ, cnZ + offs, hm[int(cnX)][int(cnZ + offs)][0], hm[int(cnX)][int(cnZ - offs)][0])
            if (int(cnX) >= 0 and int(cnX) < len(hm) and int(cnX - offs) >= 0 and int(cnX + offs) < len(hm)
                    and cnZ >= 0 and int(cnZ) < len(hm[0]) and int(cnZ - offs) >= 0 and int(cnZ + offs) < len(hm[0])):
                # check collision conditions
                # first check ice blocks
                if (is_ice_block(hm, cnX-offs, cnZ) or is_ice_block(hm, cnX+offs, cnZ)
                   or is_ice_block(hm, cnX, cnZ-offs) or is_ice_block(hm, cnX, cnZ+offs)):
                    self.bounce(0.25, -5)
                elif (not(has_collision(hm, cnX-offs, cnZ, wc) or has_collision(hm, cnX+offs, cnZ, wc)
                       or has_collision(hm, cnX, cnZ-offs, wc) or has_collision(hm, cnX, cnZ+offs, wc))
                       or self.Colliding == False):
                    # types
                    tp1 = get_road_type(hm, cnX-offs, cnZ)
                    tp2 = get_road_type(hm, cnX+offs, cnZ)
                    tp3 = get_road_type(hm, cnX, cnZ-offs)
                    tp4 = get_road_type(hm, cnX, cnZ+offs)

                    # check if fall off
                    if ((tp1 == 3 or tp2 == 3
                        or tp3 == 3 or tp4 == 3) and self.Ground and self.Sprite.Position.y <= 110):
                        # fall
                        self.Ground = False
                        self.RespawnFrame = 0
                        self.Saving = False
                        self.Sprite.Shadows = False
                    
                    # check if it is a jump
                    if ((tp1 == 2 or tp2 == 2
                         or tp3 == 2 or tp4 == 2)
                        and self.UpPropulsion == 0.0 and self.Ground and self.Speed > 0.5):
                        self.UpPropulsion = self.JumpHeight
                        self.Colliding = False
                        # play jump sound
                        self.Sounds["Jump"].play()
                        if self.TouchingBoost:
                            self.TouchingBoost = False

                    # check if it is a boost pannel
                    elif ((tp1 == 1 or tp2 == 1
                         or tp3 == 1 or tp4 == 1)
                        and self.UpPropulsion == 0.0):
                        # boost
                        self.boost(4, 75, True)
                        if not self.TouchingBoost:
                            self.TouchingBoost = True
                            # play sound
                            self.Sounds["Boost"].play()
                    elif self.TouchingBoost:
                        self.TouchingBoost = False
                        
                    # check if it is offroad
                    if ((is_offroad(hm, cnX-offs, cnZ) or is_offroad(hm, cnX+offs, cnZ)
                        or is_offroad(hm, cnX, cnZ-offs) or is_offroad(hm, cnX, cnZ+offs)) and not self.Shrooming
                        and (self.TouchedOffroad == True or self.UpPropulsion == 0.0)):
                        # make sure speed is slower
                        self.TouchedOffroad = True
                        if self.Speed > self.MaxSpeed/2.5:
                            self.Speed = self.MaxSpeed/2.5
                        if self.Drifting:
                            self.Drifting = False
                            #self.Sounds["Skid"].stop()
                    elif self.TouchedOffroad == True:
                        self.TouchedOffroad = False
                    self.Sprite.Position.x = nX
                    self.Sprite.Position.z = nZ
                    
                elif not (has_collision(hm, ccX-offs, cnZ, wc) or has_collision(hm, ccX+offs, cnZ, wc)
                       or has_collision(hm, ccX, cnZ-offs, wc) or has_collision(hm, ccX, cnZ+offs, wc)):
                    if self.Speed <= 3.5:
                        self.too_slow()
                        self.Sprite.Position.z = nZ
                        #self.Speed = self.Speed/1.2
                    else:
                        self.fast_enough()
                
                elif not(has_collision(hm, cnX-offs, ccZ, wc) or has_collision(hm, cnX+offs, ccZ, wc)
                       or has_collision(hm, cnX, ccZ-offs, wc) or has_collision(hm, cnX, ccZ+offs, wc)):
                    if self.Speed <= 3.5:
                        self.too_slow()
                        self.Sprite.Position.x = nX
                        #self.Speed = self.Speed/1.3
                    else:
                        self.fast_enough()
                
                else:
                    """
                    if (is_ice_block(hm, ccX, ccZ) or is_ice_block(hm, cnX, cnZ)
                        or is_ice_block(hm, cnX-offs, ccZ) or is_ice_block(hm, cnX+offs, ccZ)
                        or is_ice_block(hm, cnX, ccZ-offs) or is_ice_block(hm, cnX, ccZ+offs)
                        or is_ice_block(hm, ccX-offs, cnZ) or is_ice_block(hm, ccX+offs, cnZ)
                        or is_ice_block(hm, ccX, cnZ-offs) or is_ice_block(hm, ccX, cnZ+offs)):
                    """
                    if self.Speed <= 3.5:
                        self.too_slow()
                        #self.Speed = self.Speed/1.3
                    else:
                        self.fast_enough()
        else:
            self.Sprite.Position.x = nX
            self.Sprite.Position.z = nZ

        # if camera then set camera to behind
        #if hasattr(self, "Camera"):
            #cos, sin = numpy.cos(rot), numpy.sin(rot)
            #self.Camera.set_position((x*34 - cos*100, y/100 + 6, z*34 - sin*100))
            #self.Camera.CFrame.Rotation.x = rot
            #self.update_camera()

    def accelerate(self, t=20):
        if self.CanAccelerate:
            if self.Speed + self.Acceleration/5 <= self.MaxSpeed:
                self.Speed += self.Acceleration/5
            else:
                self.Speed = self.MaxSpeed
            #self.move_parallel(self.Speed, t)

    def decelerate(self, amt=0.2, t=20):
        if self.Speed - amt >= 0:
            self.Speed -= amt
            
        # if negative speed then accelerate back to 0
        elif self.Speed + amt <= 0:
            self.Speed += amt
        else:
            self.Speed = 0
        #self.move_parallel(self.Speed, t)

    def decelerate_negative(self, amt=0.2, t=20):
        if self.Speed - amt >= -self.MaxSpeed/2:
            self.Speed -= amt
        else:
            self.Speed = -self.MaxSpeed/2
        #self.move_parallel(self.Speed, t)

    def forward(self, units=0.0, t=20):
        self.move_parallel(units, t)

    def backward(self, units=0.0, t=20):
        self.move_parallel(-units, t)

    def turn(self, units=0.0, t=20):
        #if units > 0 and self.TurnDegree < numpy.deg2rad(self.MaxTurnDegree):
            #self.TurnDegree += turning_speed
        #elif units < 0 and self.TurnDegree > -numpy.deg2rad(self.MaxTurnDegree):
            #self.TurnDegree -= turning_speed
        #if self.UpPropulsion == 0.0:
        if self.Speed < 0:
            units = -units
        if self.Speed == 0 and self.UpPropulsion != 0:
            self.Rotation = (self.Rotation + ((units/100)*(t/10))*0.5)
        else:
            self.Rotation = (self.Rotation + ((units/100)*(t/10))*(self.Speed/self.MaxSpeed))
        self.update_rotation(units)
        self.Sprite.Direction = self.Rotation + self.TurnDegree

        # if camera then rotate it as well
        #if hasattr(self, "Camera"):
            #self.Camera.CFrame.Rotation.x = self.Rotation#.Sprite.Direction

    def turn_left(self, units=0.0, t=20):
        self.turn(-units, t)

    def turn_right(self, units=0.0, t=20):
        self.turn(units, t)

    def propell_y(self):
        if self.UpPropulsion != 0:
            if (self.Ground and self.Sprite.Position.y + self.UpPropulsion*100 <= 100):
                self.Sprite.Position.y = 100
                self.UpPropulsion = 0.0
                if not self.Colliding:
                    self.Colliding = True
            elif (not self.Ground and self.Sprite.Position.y + self.UpPropulsion*100 <= -3000):
                self.Sprite.Position.y = -3000
                self.UpPropulsion = 0.0
                if not self.Colliding:
                    self.Colliding = True
                self.Saving = True
            else:
                self.Sprite.Position.y += self.UpPropulsion*100

                # increment the propulsion
                self.UpPropulsion -= 0.0198
            #if hasattr(self, "Camera"):
                #self.Camera.CFrame.Position.y = self.Sprite.Position.y/20
        elif not self.Ground and self.Saving == False:
            self.UpPropulsion = -0.05

