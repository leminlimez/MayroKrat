# where a bunch of the animation stuff is held
import pygame
import numpy

Window = (800, 600)

pygame.init()
pygame.display.set_mode((Window[0], Window[1]))

font = pygame.font.Font('Assets/Fonts/SNES.ttf', 30)

## Colors ##
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 204, 0)

def create_sheet(path, length, x, y):
    sheet = pygame.image.load(path).convert_alpha()
    sprites = []
    for i in range(length):
        xx = i*x
        #for j in range(y):
            #yy = j*32
        sprites.append(sheet.subsurface(xx, 0, x, y))
    #sprite = sprites[0]
    # scale the sprite to the render resolution
    #spsize = numpy.asarray(sprite.get_size())*self.Resolution[0]/800

    return sprites

# Table of animations
AnimData = {
    "Lakitu_Start": [ # when player starts a race
        "SpriteSheet", # what is being animated
        create_sheet("Assets/Lakitu/Lakitu_Start.png", 7, 38, 40), # sprite sheet
        400, # number of frames
        (105, 117), # size of sprite
        lambda frame: numpy.piecewise(frame, [(frame <= 31), (frame > 31 and frame <= 335), frame > 335], [(lambda frame: (5/3)*frame + 100), 150, (lambda frame: (5/3)*(370-frame) + 100)]), # calculate x coordinate
        lambda frame: numpy.piecewise(frame, [(frame <= 31), (frame > 31 and frame <= 335), frame > 335], [(lambda frame: (5*(5/3)*frame)), (lambda frame: 30*numpy.sin(frame*0.05) + 245), (lambda frame: 5*((5/3)*(370-frame)))]), # calculate y coordinate
        [[0, 0], [120, 1], [130, 2], [180, 3], [190, 4], [240, 3], [250, 4], [300, 5], [310, 6]] # what frame to change the sprite
        ],
    
    "Lakitu_Lap2": [ # when player reaches second lap
        "SpriteSheet", # what is being animated
        create_sheet("Assets/Lakitu/Lakitu_Lap2.png", 4, 36, 44), # sprite sheet
        125, # number of frames
        (108, 132), # size of sprite
        lambda frame: (frame*2), # calculate x coordinate
        lambda frame: -(((frame/4)-14)**2) + 175, # calculate y coordinate
        [[0, 0], [12, 1], [16, 2], [20, 3]] # what frame to change the sprite
        ],
    
    "Lakitu_Lap3": [ # when player reaches third lap
        "SpriteSheet", # what is being animated
        create_sheet("Assets/Lakitu/Lakitu_Lap3.png", 4, 36, 44), # sprite sheet
        125, # number of frames
        (108, 132), # size of sprite
        lambda frame: (frame*2), # calculate x coordinate
        lambda frame: -(((frame/4)-14)**2) + 175, # calculate y coordinate
        [[0, 0], [12, 1], [16, 2], [20, 3]] # what frame to change the sprite
        ],

    "Lakitu_Lap4": [ # when player reaches forth lap
        "SpriteSheet", # what is being animated
        create_sheet("Assets/Lakitu/Lakitu_Lap4.png", 4, 36, 44), # sprite sheet
        125, # number of frames
        (108, 132), # size of sprite
        lambda frame: (frame*2), # calculate x coordinate
        lambda frame: -(((frame/4)-14)**2) + 175, # calculate y coordinate
        [[0, 0], [12, 1], [16, 2], [20, 3]] # what frame to change the sprite
        ],

    "Lakitu_LapFinal": [ # when player reaches final lap
        "SpriteSheet", # what is being animated
        create_sheet("Assets/Lakitu/Lakitu_LapFinal.png", 4, 36, 44), # sprite sheet
        125, # number of frames
        (108, 132), # size of sprite
        lambda frame: (frame*2), # calculate x coordinate
        lambda frame: -(((frame/4)-14)**2) + 175, # calculate y coordinate
        [[0, 0], [12, 1], [16, 2], [20, 3]] # what frame to change the sprite
        ],

    "Lakitu_Finish": [ # when player finishes the race
        "SpriteSheet", # what is being animated
        create_sheet("Assets/Lakitu/Lakitu_Finish.png", 8, 50, 46), # sprite sheet
        500, # number of frames
        (150, 138), # size of sprite
        lambda frame: numpy.piecewise(frame, [(frame <= 30), (frame > 30 and frame <= 310), frame > 310], [(lambda frame: (5/3)*frame + 100), 150, (lambda frame: (5/3)*(340-frame) + 100)]), # calculate x coordinate
        lambda frame: numpy.piecewise(frame, [(frame <= 30), (frame > 30 and frame <= 310), frame > 310], [(lambda frame: (5*(5/3)*frame)), (lambda frame: 30*numpy.sin(frame*0.05) + 245), (lambda frame: 5*((5/3)*(340-frame)))]), # calculate y coordinate
        [
            [0, 5], [8, 6], [16, 7],
            [24, 0], [32, 1], [40, 2], [48, 3], [56, 4], [64, 5], [72, 6], [80, 7],
            [88, 0], [96, 1], [104, 2], [112, 3], [120, 4], [128, 5], [136, 6], [144, 7],
            [152, 0], [160, 1], [168, 2], [176, 3], [184, 4], [192, 5], [200, 6], [208, 7],
            [216, 0], [224, 1], [232, 2], [240, 3], [248, 4], [256, 5], [264, 6], [272, 7],
            [280, 0], [288, 1], [296, 2], [304, 3], [312, 4], [320, 5], [328, 6], [336, 7]
        ] # what frame to change the sprite
        ],


    "Time_BG":[ # background for the time animation
        "Rectangle", # what is being animated
        lambda size: pygame.Surface(size), # render text
        5500, # number of frames
        lambda size: size, # size of rectangle
        lambda frame: numpy.piecewise(frame, [(frame < 290), (frame >= 290 and frame <= 315), (frame > 315)], [1000, (lambda frame: 900-(20*(frame-290))), 400]), # calculate x coordinate
        lambda frame: 315 # y coordinate
    ],
    
    "Lap1_Time":[ # lap 1 time animation
        "Text", # what is being animated
        lambda txt, col: font.render("L1   "+txt, False, col), # render text
        5500, # number of frames
        40, # size of text
        lambda frame: numpy.piecewise(frame, [(frame < 290), (frame >= 290 and frame <= 315), (frame > 315)], [1000, (lambda frame: 900-(20*(frame-290))), 400]), # calculate x coordinate
        lambda frame: 250 # y coordinate
        ],
    
    "Lap2_Time":[ # lap 2 time animation
        "Text", # what is being animated
        lambda txt, col: font.render("L2   "+txt, False, col), # render text
        5500, # number of frames
        40, # size of text
        lambda frame: numpy.piecewise(frame, [(frame < 340), (frame >= 340 and frame <= 365), (frame > 365)], [1000, (lambda frame: 900-(20*(frame-340))), 400]), # calculate x coordinate
        lambda frame: 285 # y coordinate
        ],
    
    "Lap3_Time":[ # lap 3 time animation
        "Text", # what is being animated
        lambda txt, col: font.render("L3   "+txt, False, col), # render text
        5500, # number of frames
        40, # size of text
        lambda frame: numpy.piecewise(frame, [(frame < 390), (frame >= 390 and frame <= 415), (frame > 415)], [1000, (lambda frame: 900-(20*(frame-390))), 400]), # calculate x coordinate
        lambda frame: 320 # y coordinate
        ],

    "Time_Bar":[ # time bottom bar animation
        "Rectangle", # what is being animated
        lambda size: pygame.Surface(size), # render text
        5500, # number of frames
        lambda size: size, # size of rectangle
        lambda frame: numpy.piecewise(frame, [(frame < 440), (frame >= 440 and frame <= 465), (frame > 465)], [1000, (lambda frame: 900-(20*(frame-440))), 400]), # calculate x coordinate
        lambda frame: 350 # y coordinate
        ],

    "Overall_Time":[ # total time animation
        "Text", # what is being animated
        lambda txt, col: font.render("T    "+txt, False, col), # render text
        5500, # number of frames
        40, # size of text
        lambda frame: numpy.piecewise(frame, [(frame < 490), (frame >= 490 and frame <= 515), (frame > 515)], [1000, (lambda frame: 900-(20*(frame-490))), 400]), # calculate x coordinate
        lambda frame: 380 # y coordinate
        ],

    "Lakitu_Save":[ # animation for lakitu to save player
        "SpriteSheet", # what is being animated
        create_sheet("Assets/Lakitu/Lakitu_Save.png", 2, 29, 58), # sprite sheet
        3000, # number of frames
        (97, 174), # size of sprite
        lambda frame: (frame*2), # calculate x coordinate
        lambda frame: -(((frame/4)-14)**2) + 175, # calculate y coordinate
        [[0, 0], [12, 1], [16, 2], [20, 3]] # what frame to change the sprite
        ]
    }

class Animation:
    def __init__(self, anim_type, attributes=["", WHITE]):
        data = AnimData[anim_type]
        self.Type = data[0]
        if self.Type == "Text":
            self.Item = data[1](attributes[0], attributes[1])
            self.Size = data[3]
        elif self.Type == "Rectangle":
            self.Item = data[1](attributes[0])
            if anim_type == "Time_BG":
                self.Item.set_alpha(200)
            self.Item.fill(attributes[1])
            self.Size = attributes[0]
        else:
            self.Item = data[1]
            self.Size = data[3]
        self.Frame = 0
        self.MaxFrame = data[2] - 1
        self.EqX = data[4]
        self.EqY = data[5]

        if self.Type == "SpriteSheet":
            self.SpriteID = data[6][0][0]
            self.FrameChangeID = 0
            self.FrameChanges = data[6]

    def get(self):
        x = self.EqX(self.Frame)
        y = self.EqY(self.Frame)

        if self.Type == "SpriteSheet":
            return True, (0, self.Item[self.SpriteID], (x, y), self.Size)
        elif self.Type == "Text":
            return True, (1, self.Item, (x, y), self.Size)
        elif self.Type == "Rectangle":
            return True, (2, self.Item, (x, y), self.Size)
        else:
            return False, ()

    def increment(self):
        # increment the animation
        if self.Frame < self.MaxFrame:
            self.Frame += 1
            x = self.EqX(self.Frame)
            y = self.EqY(self.Frame)

            if self.Type == "SpriteSheet":
                # calculate change of sprite
                if self.FrameChangeID < len(self.FrameChanges)-1:
                    newID = self.FrameChangeID + 1
                    if self.Frame >= self.FrameChanges[newID][0]:
                        self.FrameChangeID = newID
                        self.SpriteID = self.FrameChanges[newID][1]
                
                return True, (0, self.Item[self.SpriteID], (x, y), self.Size)
            elif self.Type == "Text":
                return True, (1, self.Item, (x, y), self.Size)
            elif self.Type == "Rectangle":
                return True, (2, self.Item, (x, y), self.Size)
        return False, ()
