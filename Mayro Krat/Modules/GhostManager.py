# module for managing time trial
import os.path
from Modules import Track
import numpy
import pygame

from Modules.Driver import Driver

from PyGame3D import Engine_3D

CCs = [50, 100, 150]
Places = ["1st", "2nd", "3rd", "4th", "5th"]

def get_key_code(key):
    return pygame.key.name(key)#pygame.key.key_code(pygame.key.name(key))

def to_bool(string):
    if string == "True":
        return True
    elif string == "False":
        return False
    else:
        print("string not bool")
        return False

ValidKeys = [
    pygame.K_w,
    pygame.K_a,
    pygame.K_s,
    pygame.K_d,
    pygame.K_LSHIFT,
    pygame.K_UP,
    pygame.K_DOWN,
    pygame.K_LEFT,
    pygame.K_RIGHT,
    pygame.K_SPACE
]
"""
    get_key_code(pygame.K_w),
    get_key_code(pygame.K_a),
    get_key_code(pygame.K_s),
    get_key_code(pygame.K_d),
    get_key_code(pygame.K_LSHIFT),
    get_key_code(pygame.K_UP),
    get_key_code(pygame.K_DOWN),
    get_key_code(pygame.K_LEFT),
    get_key_code(pygame.K_RIGHT)
]
"""

"""
def n(key):
    print(pygame.key.name(key))

n(pygame.K_w)
n(pygame.K_a)
n(pygame.K_s)
n(pygame.K_d)
n(pygame.K_LSHIFT)
n(pygame.K_UP)
n(pygame.K_DOWN)
n(pygame.K_LEFT)
n(pygame.K_RIGHT)
"""

def is_valid_key(key):
    if get_key_code(key):#pygame.key.name(key) and get_key_code(key):
        return key in ValidKeys#get_key_code(key) in ValidKeys


# convert frames to time
def convert_to_time(frames):
    m = int(numpy.floor(frames/3600))
    s = int(numpy.floor((frames%3600)/60))
    s_str = str(s)
    if s < 10:
        s_str = "0"+s_str
    ms = int((frames%60)*(1000/60))
    ms_str = str(ms)
    if ms < 10:
        ms_str = "00"+ms_str
    elif ms < 100:
        ms_str = "0"+ms_str
    return str(m)+"'"+s_str+"\""+ms_str


# get the file path
def get_path(TrackName, CC):
    return "SaveData/Times/"+TrackName+"/GhostData_"+str(CC)+".txt"

# check if the file exists
def has_data(TrackName, CC):
    return os.path.exists(get_path(TrackName, CC))

# check if ghost data exists
def has_ghost(TrackName, CC):
    return os.path.exists("SaveData/Times/"+TrackName+"/Ghost_"+str(CC)+".txt")

# get the times if it exists
def get_times(TrackName, CC):
    # format: total, lap1, lap2, lap3
    times = []
    st = "-'--\"----"
    
    if has_data(TrackName, CC):
        # data file exists
        f = open(get_path(TrackName, CC))
        
        ind = 0
        ind2 = 0
        string = ""
        for L in f:
            Line = L.replace("\n", "")
            if ind%2 == 0 and L != "\n":
                # time
                if Line.isnumeric():
                    string = Places[ind2]+".  "+convert_to_time(int(Line))+"    "
            elif ind%2 == 1:
                # character
                ind2 += 1
                if L == "\n":
                    # no character found
                    string += "----"
                else:
                    string += Line
                times.append(string)
            ind += 1

        # if went less than places then add blanks
        if ind2 < len(Places):
            for i in range(len(Places)-ind2):
                # create a blank
                times.append(Places[i+ind2]+".  "+st+"   ----")

        # close the file
        f.close()
    else:
        for i in range(len(Places)):
            times.append(Places[i]+".  "+st+"   ----")
    return times

# check if time is a new record on track
def is_new_record(TrackName, NewTime, CC):
    if has_data(TrackName, CC):
        f = open(get_path(TrackName, CC))
        OldTime = int(f.readline())
        f.close()
        if NewTime > OldTime:
            return True
        else:
            return False
    else:
        return True

# apply the record
def set_record(TrackName, NewTime, Character, CC):
    # open the file in write mode (or create if doesn't exist)
    if has_data(TrackName, CC):
        # read file and reorganize by best time
        path = get_path(TrackName, CC)
        f = open(path, "r")

        # compile table
        ind = 0
        ind2 = 0
        tab = []
        for L in f:
            if L != "\n":
                Line = L.replace("\n", "")
                if ind%2 == 0 and Line.isnumeric():
                    # is time
                    tab.append([int(Line)])
                elif ind%2 == 1:
                    # is character
                    tab[ind2].append(Line)
                    ind2 += 1
                ind += 1
                
        # close file
        f.close()
        
        # add new time to table
        tab.append([NewTime, Character])
        
        # organize by lowest times
        tab.sort(key=lambda x: x[0])

        # write to file
        f = open(path, "w")
        ind = 0
        for t in tab:
            if ind < len(Places):
                f.write(str(t[0])+"\n"+t[1]+"\n")
                ind += 1
            else:
                break

        # close file
        f.close()
                
        #f.write(str(NewTime)+"\n")
    else:
        # create a new file
        f = open(get_path(TrackName, CC), "w")
        f.write(str(NewTime)+"\n"+Character+"\n")

        # close file
        f.close()


# class to record ghost data
class GhostData:
    def __init__(self, Character, CC):
        self.Character = Character
        self.CC = CC

        self.Frame = 0

        #self.LastShroomFrame = -1

        self.BurnedOut = False
        self.StartBoostFrame = 0

        self.Points = []#[[-1, False, 0, ["w"]]]#numpy.array([[-1, False, ["W"]]]) # numpy array used to increase performance
        #self.ShroomFrames = []
        self.CoinBoostFrames = []

    def update(self):
        self.Frame += 1

    def coin_boost(self, Frame, Coins):
        """
        found = False
        # find frame
        for point in self.Points:
            if point[0] == self.Frame:
                point[2] = True
                found = True

        # if not found then add a frame
        if not found:
            self.add_point(False, True, Coins, pygame.key.get_pressed())
        """
        self.CoinBoostFrames.append(Frame)
        self.add_point(Frame, True, Coins, pygame.key.get_pressed())

    def use_mushroom(self, Frame, Coins):
        """
        found = False
        # find frame
        for point in self.Points:
            if point[0] == self.Frame:
                point[1] = True
                found = True

        # if not found then add a frame
        if not found:
            self.add_point(True, False, Coins, pygame.key.get_pressed())
        """
        #self.ShroomFrames.append(Frame)
        self.add_point(Frame, False, Coins, pygame.key.get_pressed())

    def add_point(self, Frame, CoinBoost, Coins, KeysHeld):# Shroomed, CoinBoost, Coins, KeysHeld):
        Keys = []
        #if Shroomed:
            #self.LastShroomFrame
        """
        for key in KeysHeld:
            if is_valid_key(key):
                Keys.append(get_key_code(key))
        """
        for key in ValidKeys:
            if KeysHeld[key]:
                Keys.append(get_key_code(key))
        #self.Points = numpy.append(self.Points, [[self.Frame, Shroomed, Keys]], axis=0)
        self.Points.append([Frame, CoinBoost, Coins, Keys])

    def save_data(self, TrackName):
        # get the path
        path = "SaveData/Times/"+TrackName+"/Ghost_"+str(self.CC)+".txt"

        # write to file
        # write the initial data
        f = open(path, "w")
        f.write(self.Character+"\n")
        f.write(str(self.BurnedOut)+"\n")
        f.write(str(self.StartBoostFrame)+"\n")

        # loop through points and apply
        lastFrame = -1
        for point in self.Points:
            Line = ""
            if point[0] >= 0 and point[0] > lastFrame:
                lastFrame = point[0]
                Line += str(point[0])+";"
                Line += str(point[1])+";"
                Line += str(point[2])
                # loop through keys and apply
                if len(point[3]) > 0:
                    Line += ";"
                    ind = 0
                    for key in point[3]:
                        if ind > 0:
                            Line += "/"
                        Line += key
                        ind += 1
                        
                Line += "\n"

                # write the line to file
                f.write(Line)
        f.write("END")

        # close file
        f.close()


# class for the ghost itself
class Ghost:
    def __init__(self, Track, CC, Camera):
        self.TrackName = Track.Name
        self.CC = CC
        self.Camera = Camera
        self.Track = Track

        self.ReferenceIndex = 0

        # load the file
        self.create_data()

        # initialize the driver
        # create driver sprites
        d, dsize = self.Camera.get_sprites("Assets/Racers/"+self.Character+"/"+self.Character+"Drive.png", 12, 32, 32)
        dpos = Track.SpawnPosition
        dsp = Engine_3D.Sprite(d, 12, dpos, True, 0, True)
        dsp.Direction = numpy.deg2rad(Track.SpawnRotation)
        self.Camera.add_sprite(dsp)

        # create driver object
        self.Driver = Driver(dsp, self.Character, CC)
        self.Driver.set_collision_map(self.Camera.HeightMap, self.Camera.WallCollisions)
        self.Driver.JumpHeight = self.Track.JumpHeight

        self.Driver.apply_compensation(self.Camera.Compensation)
        self.Driver.attach_camera(self.Camera)

        self.DriverHead = Engine_3D.get_image("Assets/Racers/"+self.Character+"/"+self.Character+"Head.png")
        

    def create_data(self):
        path = "SaveData/Times/"+self.TrackName+"/Ghost_"+str(self.CC)+".txt"
        if os.path.exists(path):
            # open the file
            f = open(path, 'r')
            self.GhostData = []
            
            # load the ghost data
            ind = 0
            for L in f:
                if L != "\n":
                    Line = L.replace("\n", "")
                    if ind == 0:
                        self.Character = Line
                    elif ind == 1:
                        self.BurnedOut = to_bool(Line)
                    elif ind == 2:
                        self.StartBoostFrame = int(Line)
                    elif Line == "END":
                        pass
                    else:
                        # expand the data
                        data = Line.split(";")
                        item = []
                        # set the frame
                        item.append(int(data[0]))
                        # set the mushroom status
                        #item.append(to_bool(data[1]))
                        # set the coin boost status
                        item.append(to_bool(data[1]))
                        # set the coins
                        item.append(int(data[2]))

                        # parse the keys
                        if len(data) == 4:
                            # there are keys pressed
                            keys = data[3].split("/")
                            item.append(keys)
                        else:
                            # there are no keys pressed
                            item.append([])
                        self.GhostData.append(item)
                    ind += 1

            # close the file
            f.close()

    # update the driver
    def update(self, StartFrame, Frame):
        Frame = Frame
        if StartFrame > 0 or StartFrame == -2:
            # race has not started yet
            if StartFrame <= self.StartBoostFrame and StartFrame != -2:
                # start boost animation
                pass
        elif StartFrame == 0:
            # race started
            if self.BurnedOut:
                # got burned out
                self.Driver.CanAccelerate = False
                self.Driver.AccelCooldown = 90
                self.Driver.BurnoutFrame = 75
                # create the particles
                self.Driver.drift_particles(self.Camera, False, True)
            else:
                # got the starter boost
                self.Driver.boost(3, self.StartBoostFrame/2)
        else:
            # race is going
            # update the frame index if needed
            if self.ReferenceIndex + 1 < len(self.GhostData) and self.GhostData[self.ReferenceIndex + 1][0] <= Frame:
                # update the index
                self.ReferenceIndex += 1

                # update the driver coins
                if self.Driver.Coins != self.GhostData[self.ReferenceIndex][2]:
                    self.Driver.Coins = self.GhostData[self.ReferenceIndex][2]

                # boost if can boost
                if "space" in self.GhostData[self.ReferenceIndex][3]:
                    self.Driver.boost(3, 150, True)

            self.Driver.boost_particles(self.Camera)

            if self.Driver.AccelCooldown > 0:
                self.Driver.AccelCooldown -= 1
                if self.Driver.AccelCooldown == 0:
                    self.Driver.CanAccelerate = True

            # manage the driver positions and movement
            moved = False
            turning = False

            u = 0.9
            tu = 0

            # determine if mushroom is used or coin is collected
            #if self.GhostData[self.ReferenceIndex][1] == True and self.GhostData[self.ReferenceIndex][0] == Frame:
                # boost with mushroom
                #self.Driver.boost(3, 150, True)
            if self.GhostData[self.ReferenceIndex][1] == True and self.GhostData[self.ReferenceIndex][0] == Frame:
                # boost for coin
                self.Driver.boost(1, 10)

            keys = self.GhostData[self.ReferenceIndex][3]

            ## KEY EVENTS ##

            # manage drifting
            if "left shift" in keys:
                # if same frame then jump
                if self.GhostData[self.ReferenceIndex][0] == Frame:
                    if self.Driver.UpPropulsion == 0.0:
                        self.Driver.UpPropulsion = 0.2

                    self.Driver.Drifting = True
                self.Driver.drift_particles(self.Camera)
            elif self.Driver.Drifting:
                self.Driver.Drifting = False

            self.Driver.Turn = 0

            if self.Driver.Drifting:
                u = 1.25

            # manage turning keys
            if ("a" in keys or "left" in keys) and self.Driver.BurnoutFrame == 0:
                if self.Driver.TurnDegree > 0:
                    tu += -u/2
                    self.Driver.Turn += 1
                else:
                    tu += -u
                    self.Driver.Turn += 2
                turning = True

            if ("d" in keys or "right" in keys) and self.Driver.BurnoutFrame == 0:
                if self.Driver.TurnDegree < 0:
                    tu += u/2
                    self.Driver.Turn += 1
                else:
                    tu += u
                    self.Driver.Turn += 2
                turning = True

            # manage acceleration key
            if ("w" in keys or "up" in keys) and self.Driver.CanAccelerate:
                moved = True
                self.Driver.accelerate(20)

            # manage deceleration key
            if ("s" in keys or "down" in keys) and not turning:
                moved = True
                self.Driver.decelerate_negative(0.25)

            # manage the turning
            if turning:
                # break drifting
                if ("s" in keys or "down" in keys):
                    tu = tu*1.25
                self.Driver.turn(tu)

            # decelerate if not moving
            if not moved and self.Driver.BoostCount <= 0:
                self.Driver.decelerate(0.25)

            # move driver and manage gravity
            self.Driver.move_parallel(self.Driver.Speed)
            self.Driver.propell_y()

            # disable drifting if needed
            #if not turning and self.Driver.UpPropulsion == 0.0 and self.Driver.Drifting:
                #self.Driver.Drifting = False
            #if not turning:
                #self.Driver.update_rotation(0.0)

            # finally, update driver
            self.Driver.update(None, True)
            self.Driver.update_camera(turning)


# class to load and store the data and times
class Data:
    def __init__(self):
        # loop through tracks and collect data
        self.TrackData = {}
        
        self.update()

    def update(self):
        for cup in Track.TrackList.keys():
            for track in Track.TrackList[cup]:
                self.TrackData[track[0]] = {}
                
                # get the track times
                # loop through CC speeds
                for cc in CCs:
                    self.TrackData[track[0]][cc] = get_times(track[0], cc)

