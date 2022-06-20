# manager for the main menu
# made just to keep things organized

import pygame
import numpy
from Modules.UIObjects import TextButton as Button
from Modules.UIObjects import ImageButton
from Modules.UIObjects import TextLabel
from Modules import Track

from Modules import GhostManager

TimeData = GhostManager.Data()

Window = (800, 600)

pygame.init()
pygame.display.set_mode((Window[0], Window[1]))

def create_sheet(path, length, x, y):
    sheet = pygame.image.load(path).convert_alpha()
    sprites = []
    for i in range(length):
        xx = i*x
        #for j in range(y):
            #yy = j*32
        sprites.append(pygame.transform.scale(sheet.subsurface(xx, 0, x, y), (x*(2+(2/3)), y*(2+(2/3)))))
        #sprites.append(sheet.subsurface(xx, 0, x, y))
    #sprite = sprites[0]
    # scale the sprite to the render resolution
    #spsize = numpy.asarray(sprite.get_size())*self.Resolution[0]/800

    return sprites

## VARIABLES ##

## MAIN MENU STUFF ##
title_font = pygame.font.Font('Assets/Fonts/SNES.ttf', 45)
btn_font = pygame.font.Font('Assets/Fonts/SNES.ttf', 20)

MenuBG = pygame.image.load("Assets/MenuBG.png")
BG = pygame.transform.scale(MenuBG.copy(), (1200, 600))

Title = pygame.image.load("Assets/Title.png")
title = pygame.transform.scale(Title.copy(), (468, 152))


MenuButtons = [
    "Time Trials",
    "Quit Game"
]

CCButtons = [
    ["50 CC", 50],
    ["100 CC", 100],
    ["150 CC", 150]
]

Characters = [
    "Mayro",
    "Loogi",
    "Pear",
    "Tumor",
    
    "Sushi",
    "Dog",
    "Frank",
    "Ape"
]

# track background stuff
bg_path = "Assets/MenuBackgrounds/"

TrackBGs = {
    "MarioCircuit": "Grass",
    "MarioCircuit2": "Grass",
    "MarioCircuit3": "Grass",
    "MarioCircuit4": "Grass",

    "DonutPlains1": "Grass",
    "DonutPlains2": "Grass",
    "DonutPlains3": "Grass",

    "ChocoIsland1": "Dirt",
    "ChocoIsland2": "Dirt",

    "FrankBeach1": "Water",
    "FrankBeach2": "Water",

    "BowserCastle": "Lava",
    "BowserCastle2": "Lava",

    "GhostValley1": "Dark",
    "GhostValley2": "Dark",

    "VanillaLake1": "Ice",
    "VanillaLake2": "Ice",

    "RainbowRoad": "Dark"
}

## Colors ##
WHITE = (255, 255, 255)
GRAY = (175, 175, 175)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 204, 0)

# function to update time data
def update_time_data():
    TimeData.update()

# pause menu
class Pause:
    def __init__(self):
        self.ResumeButton = Button((125, 45), (Window[0]/2, Window[1]/2 - 15), "Resume", YELLOW, 20)
        self.PauseLabel = TextLabel((Window[0]/2, Window[1]/2 - 75), "Paused", GRAY, 40)
        self.RestartButton = Button((150, 45), (Window[0]/2, Window[1]/2 + 15), "Restart", WHITE, 20)
        self.QuitButton = Button((150, 45), (Window[0]/2, Window[1]/2 + 45), "Return to title screen", WHITE, 20)
        

    def draw_menu(self, WIN):
        # draw fade
        s = pygame.Surface(Window)
        s.set_alpha(150)
        s.fill((0, 0, 0))
        WIN.blit(s, (0, 0))

        # draw title
        label, labelPos = self.PauseLabel.render()
        WIN.blit(label, labelPos)

        # check if it is being hovered
        if self.ResumeButton.mouse_hovering():
            self.ResumeButton.TextColor = YELLOW
            self.RestartButton.TextColor = WHITE
            self.QuitButton.TextColor = WHITE
        elif self.RestartButton.mouse_hovering():
            self.ResumeButton.TextColor = WHITE
            self.RestartButton.TextColor = YELLOW
            self.QuitButton.TextColor = WHITE
        elif self.QuitButton.mouse_hovering():
            self.ResumeButton.TextColor = WHITE
            self.RestartButton.TextColor = WHITE
            self.QuitButton.TextColor = YELLOW

        # draw the buttons
        res, resPos = self.ResumeButton.render()
        WIN.blit(res, resPos)

        rest, restPos = self.RestartButton.render()
        WIN.blit(rest, restPos)

        q, qPos = self.QuitButton.render()
        WIN.blit(q, qPos)

    def buttons_hovering(self):
        # first check resume button
        if self.ResumeButton.mouse_hovering():
            return "Resume"
        
        # next check restart button
        elif self.RestartButton.mouse_hovering():
            return "Restart"

        # finally check the quit button
        elif self.QuitButton.mouse_hovering():
            return "Quit"

# track select screen
class TrackSelection:
    def __init__(self, CC=100):
        self.CC = CC
        
        # music
        self.Music = pygame.mixer.Sound("Sounds/Music/Menus/Choose_Your_Driver.mp3")
        self.Selected = 0#"MarioCircuit"

        self.BackButton = Button((80, 50), (Window[0]-50, Window[1] - 50), "Back", WHITE, 20)
        
        self.TrackButtons = []
        self.TrackPreviews = {}
        self.CupTitles = []
        
        ind = 0
        col = -1
        for cup in Track.TrackList.keys():
            row = 1
            col += 1

            self.CupTitles.append(TextLabel((125 + col*275, 40), cup, GRAY, 21))
            for track in Track.TrackList[cup]:
                c = WHITE
                if ind == 0:
                    c = YELLOW
                btn = Button((200, 28), (125 + col*275, 50 + row*30), track[1], c, 15)
                btn.Key = track[0]
                btn.ID = ind
                self.TrackButtons.append(btn)
                # load the image
                self.TrackPreviews[btn.Key] = pygame.image.load("Assets/Tracks/"+btn.Key+"/Preview.png")
                ind += 1
                row += 1

        # images
        self.Foreground = pygame.image.load("Assets/Tracks/ChoiceForeground.png")

        self.Backgrounds = {
            "Grass": pygame.image.load(bg_path+"Grass.png"),
            "Dark": pygame.image.load(bg_path+"Dark.png"),
            "Water": pygame.image.load(bg_path+"Water.png"),
            "Dirt": pygame.image.load(bg_path+"Dirt.png"),
            "Lava": pygame.image.load(bg_path+"Lava.png"),
            "Ice": pygame.image.load(bg_path+"Ice.png")
        }

        self.BG = "Grass"

    def draw_menu(self, WIN):
        # draw the background
        WIN.blit(self.Backgrounds[self.BG], (0, 308))
        key = self.TrackButtons[self.Selected].Key

        # track preview
        WIN.blit(self.TrackPreviews[key], (0, 308))

        # track title and best times
        # if the track is vanilla lake set color to black
        col = WHITE
        if key == "VanillaLake1" or key == "VanillaLake2":
            col = BLACK
            
        text = btn_font.render(self.TrackButtons[self.Selected].Text, False, col)
        WIN.blit(text, (25, 325))

        times = TimeData.TrackData[self.TrackButtons[self.Selected].Key][self.CC]
        for t in range(len(times)):
            #if t == 0:
                #c
            time_text = btn_font.render(times[t], False, col)
            WIN.blit(time_text, (25, 375 + 25*t))

        # back button
        # if hovering then highlight
        if self.BackButton.mouse_hovering() and self.BackButton.TextColor != YELLOW:
            self.BackButton.TextColor = YELLOW
        elif not self.BackButton.mouse_hovering() and self.BackButton.TextColor != WHITE:
            self.BackButton.TextColor = WHITE
        back, backPos = self.BackButton.render()
        WIN.blit(back, backPos)

        # draw the foreground
        WIN.blit(self.Foreground, (0, 0))

        # cup names
        for c in self.CupTitles:
            cup, cupPos = c.render()
            WIN.blit(cup, cupPos)

        # now the buttons
        for b in self.TrackButtons:
            # if selected then make yellow
            # also change background
            if b.mouse_hovering() and b.Key != self.Selected:
                self.Selected = b.ID

                if b.Key in TrackBGs:
                    self.BG = TrackBGs[b.Key]
                else:
                    self.BG = "Grass"
                # change all buttons back to white
                for c in self.TrackButtons:
                    c.TextColor = WHITE
                b.TextColor = YELLOW
            btn, pos = b.render()
            WIN.blit(btn, pos)

    def buttons_hovering(self):
        # back button
        if self.BackButton.mouse_hovering():
            return "Back"

        # track button
        if self.TrackButtons[self.Selected].mouse_hovering():
            # if ghost then return true
            """
            hasGhost = False
            if GhostManager.has_ghost(self.TrackButtons[self.Selected].Key, self.CC):
                hasGhost = True
            """
            return self.TrackButtons[self.Selected].Key#, hasGhost
        return "None"

# character select screen
class CharacterSelection:
    def __init__(self):
        self.TextFrame = 0
        self.BlinkFrame = 0
        self.Selected = 0

        # music
        self.Music = pygame.mixer.Sound("Sounds/Music/Menus/Choose_Your_Driver.mp3")

        # images
        self.Scrolling_Text = pygame.image.load("Assets/Character_Selection/Scrolling_Text.png")
        self.Scrolling_Text = pygame.transform.scale(self.Scrolling_Text, (683, 43))

        self.Menu = pygame.image.load("Assets/Character_Selection/Menu.png")
        self.Menu = pygame.transform.scale(self.Menu, (800, 600))

        self.BG = pygame.image.load("Assets/Character_Selection/Char_BG.png")
        self.BG = pygame.transform.scale(self.BG, (128, 150))

        self.Select1P = pygame.image.load("Assets/Character_Selection/1P_Select.png")
        self.Select1P = pygame.transform.scale(self.Select1P, (43, 21))

        self.Select1P_Buttons = []
        bid = 0
        for j in range(2):
            for i in range(4):
                btn = ImageButton(self.Select1P, (43, 21), (186 + 128*i, 170 + 170*j))
                if i == 0 and j == 0:
                    btn.Enabled = True
                else:
                    btn.Enabled = False
                btn.ID = bid
                bid += 1
                self.Select1P_Buttons.append(btn)

        self.Back1 = pygame.image.load("Assets/Character_Selection/Back_1.png")
        self.Back1 = pygame.transform.scale(self.Back1, (88, 27))

        self.Back2 = pygame.image.load("Assets/Character_Selection/Back_2.png")
        self.Back2 = pygame.transform.scale(self.Back2, (88, 27))

        self.BackBtn = ImageButton(self.Back1, (88, 27), (568, 510))
        self.BackBtn.State = 0

        self.OK1 = pygame.image.load("Assets/Character_Selection/1P_Ok1.png")
        self.OK1 = pygame.transform.scale(self.OK1, (91, 27))

        self.OK2 = pygame.image.load("Assets/Character_Selection/1P_Ok2.png")
        self.OK2 = pygame.transform.scale(self.OK2, (91, 27))

        self.OkBtn = ImageButton(self.OK1, (91, 27), (461, 509))
        self.OkBtn.State = 0
        self.OkBtn.Enabled = False

        self.Character_Images = []
        for c in Characters:
            img = "Assets/Racers/"+c+"/Menu.png"
            # create sprite sheet
            sheet = create_sheet(img, 6, 32, 32)
            frame = numpy.random.randint(0, 15)
            self.Character_Images.append([sheet, frame, False, 0, 0])
        

    def draw_menu(self, WIN):
        # draw the scrolling text
        WIN.blit(self.Scrolling_Text, (272 - self.TextFrame, 64))
        WIN.blit(self.Scrolling_Text, (955 - self.TextFrame, 64))
        
        self.TextFrame += 2
        if self.TextFrame >= 683:
            self.TextFrame = 0

        self.BlinkFrame += 1
        if self.BlinkFrame >= 14:
            self.BlinkFrame = 0

        # draw the backgrounds
        for j in range(2):
            for i in range(4):
                # draw the bg
                WIN.blit(self.BG, (146 + 128*i, 189 + 171*j))

        # draw the karts
        ind = 0
        for j in range(2):
            for i in range(4):
                DriverHeight = 0
                if self.Character_Images[ind][1] >= 8:
                    DriverHeight = 4
                self.Character_Images[ind][1] += 1
                if self.Character_Images[ind][1] >= 16:
                    self.Character_Images[ind][1] = 0
                    
                imgID = 0
                if self.Character_Images[ind][4] < 8 and self.Character_Images[ind][4] > 0:
                    imgID = int(numpy.floor(self.Character_Images[ind][4]/2))
                    if self.Character_Images[ind][2]:
                        self.Character_Images[ind][4] += 1
                    else:
                        self.Character_Images[ind][4] -= 1
                        
                elif self.Character_Images[ind][2]:
                    imgID = 4
                    DriverHeight = 0
                    if self.Character_Images[ind][3] >= 12:
                        imgID = 5
                    self.Character_Images[ind][3] += 1
                    if self.Character_Images[ind][3] >= 24:
                        self.Character_Images[ind][3] = 0
                # draw the driver
                WIN.blit(self.Character_Images[ind][0][imgID], (165 + 128*i, 210 + DriverHeight + 171*j))
                ind += 1

        WIN.blit(self.Menu, (0, 0))

        # if hovering over button then draw
        for b in self.Select1P_Buttons:
            if b.mouse_hovering() and self.OkBtn.Enabled == False:
                # disable every other button
                for btn in self.Select1P_Buttons:
                    btn.Enabled = False
                #if self.BackBtn.State == 1:
                    #self.BackBtn.Image = self.Back1
                    #self.BackBtn.State = 0
                b.Enabled = True
                self.Selected = b.ID
            # draw if enabled
            if b.Enabled and (self.BlinkFrame < 7 or self.OkBtn.Enabled == True):
                btn, pos = b.render()
                WIN.blit(btn, pos)

        # if hovering over back button
        if self.BackBtn.mouse_hovering():
            if self.BackBtn.State == 0:
                self.BackBtn.Image = self.Back2
                self.BackBtn.State = 1
        else:
            if self.BackBtn.State == 1:
                self.BackBtn.Image = self.Back1
                self.BackBtn.State = 0

        # draw back button
        back, backPos = self.BackBtn.render()
        WIN.blit(back, backPos)

        # if hovering over ok button
        if self.OkBtn.Enabled == True:
            if self.OkBtn.mouse_hovering():
                if self.OkBtn.State == 0:
                    self.OkBtn.Image = self.OK2
                    self.OkBtn.State = 1
            else:
                if self.OkBtn.State == 1:
                    self.OkBtn.Image = self.OK1
                    self.OkBtn.State = 0

            # draw back button
            ok, okPos = self.OkBtn.render()
            WIN.blit(ok, okPos)

    # manage button clicks
    def buttons_hovering(self):
        # first the back button
        if self.BackBtn.mouse_hovering():
            # unselect character if selected
            if self.OkBtn.Enabled == True:
                self.OkBtn.Enabled = False
                self.Character_Images[self.Selected][2] = False
                self.Character_Images[self.Selected][4] = 7
            else:
                # go back
                return "Back"

        # next the ok button
        if self.OkBtn.Enabled and self.OkBtn.mouse_hovering():
            return Characters[self.Selected]

        # now the selected button
        if self.Select1P_Buttons[self.Selected].mouse_hovering():
            # select
            self.OkBtn.Enabled = True
            self.Character_Images[self.Selected][4] = 1
            self.Character_Images[self.Selected][3] = 0
            self.Character_Images[self.Selected][2] = True

        return "None"


# the main menu
class MainMenu:
    def __init__(self, animated=False):
        self.MenuFrame = 0
        self.Animated = animated
        self.Buttons = []
        self.BorderSize = (250, 0)

        self.AnimationFrame = 0

        self.ButtonType = ""
        self.Selected = ""

        self.Shroom = pygame.image.load("Assets/MenuShroom.png")
        self.Shroom = pygame.transform.scale(self.Shroom, (36, 36))
        self.ShroomPosY = 0

        # create the buttons
        self.create_menu_buttons()

        # music and drivers
        self.Music = pygame.mixer.Sound("Sounds/Music/Menus/Main_Theme.mp3")

        self.Drivers = {}
        for d in Characters:
            self.Drivers[d] = create_sheet("Assets/Racers/"+d+"/"+d+"Drive.png", 12, 32, 32)

        self.Items = {
            "Banana": pygame.image.load("Assets/Items/Banana/Banana.png"),
            "Shell": pygame.image.load("Assets/Items/GreenShell/GreenShell.png")
        }

    ## FUNCTIONS ##

    # clear the menu buttons
    def clear_buttons(self):
        for b in self.Buttons:
            del b
        self.Buttons.clear()

    # create the menu button objects
    def create_menu_buttons(self):
        # clear the current buttons
        self.clear_buttons()#Buttons.clear()

        self.ButtonType = "Main"
        bh = 35
        self.Selected = MenuButtons[0]
        self.ShroomPosY = 325

        # generate the new buttons
        for b in range(len(MenuButtons)):
            col = WHITE
            if b == 0:
                col = YELLOW
            btn = Button((200, 28), (Window[0]/2, 325 + b*35), MenuButtons[b], col, 17)
            self.Buttons.append(btn)
            bh += 35
        self.BorderSize = (280, bh)

    # create the cc button objects
    def create_cc_buttons(self):
        # clear the current buttons
        self.clear_buttons()#Buttons.clear()

        self.ButtonType = "CC_Menu"
        bh = 35
        self.Selected = CCButtons[0]
        self.ShroomPosY = 325

        # generate the new buttons
        for b in range(len(CCButtons) + 1):
            if b < len(CCButtons):
                col = WHITE
                if b == 0:
                    col = YELLOW
                btn = Button((80, 28), (Window[0]/2, 325 + b*35), CCButtons[b][0], col, 17)
                btn.CC_Value = CCButtons[b][1]
                self.Buttons.append(btn)
            else:
                # make the back button
                btn = Button((80, 28), (Window[0]/2, 325 + b*35), "Back", WHITE, 17)
                self.Buttons.append(btn)
            bh += 35
        self.BorderSize = (280, bh)

    # animate the karts/items
    def animate_karts(self, WIN):
        f = self.AnimationFrame
        # initial part of animation
        if f > 130:
            char = ["Mayro"]
            # driving characters
            x = lambda frame: 2.7*(frame-150)
            y = lambda frame: 6*numpy.ceil(numpy.sin((x-150)/3))

            for c in range(len(char)):
                cX = x(f - 15*c)
                # if it is close enough to the window then continue
                #if cX >= -40:
                # calculate y
                cY = 450 + y(f - 15*c)
                # apply the character
                WIN.blit(self.Drivers[char[c]][7], (cX, cY))

    # animate the main menu
    # drives karts across it and moves the background
    def animate_main_menu(self, WIN):
        # background
        WIN.blit(BG, (self.MenuFrame, 0))
        if self.Animated:
            WIN.blit(BG, (self.MenuFrame+1200, 0))
            self.MenuFrame -= 2
            if self.MenuFrame <= -1200:
                self.MenuFrame = -2

            # animate the karts
            self.AnimationFrame = 0
            self.animate_karts(WIN)

    # creates the title screen
    def draw_menu(self, WIN):
        # animate background
        self.animate_main_menu(WIN)
        
        # title
        #title = title_font.render("Mayro Krat", False, BLUE)
        #title_rect = title.get_rect()
        #title_rect.center = (Window[0]/2, 100)
        #WIN.blit(title, title_rect)
        WIN.blit(title, (Window[0]/2 - title.get_width()/2, 50))

        # draw border
        if self.BorderSize[0] > 0 and self.BorderSize[1] > 0:
            s = pygame.Surface(self.BorderSize)
            s.fill((0, 0, 0))
            WIN.blit(s, (Window[0]/2-140, 290))

        # check if the buttons are hovered
        for b in range(len(self.Buttons)):
            if self.Buttons[b].mouse_hovering():
                self.Selected = self.Buttons[b].Text
                # reset the colors
                for h in self.Buttons:
                    h.TextColor = WHITE
                self.Buttons[b].TextColor = YELLOW
                self.ShroomPosY = 325 + b*35

        # buttons
        for b in self.Buttons:
            btn, pos = b.render()
            WIN.blit(btn, pos)

        # menu shroom
        shroomX = 125
        if self.ButtonType == "CC_Menu":
            shroomX = 90
        WIN.blit(self.Shroom, (Window[0]/2 - shroomX, self.ShroomPosY - self.Shroom.get_height()/2))

    # manage controller inputs
    def controller_inputs(self, btn):
        # next check select button
        if btn == 1:
            if self.ButtonType == "Main":
                if self.Selected == self.Buttons[0].Text:
                    return "CC"
                elif self.Selected == self.Buttons[1].Text:
                    return "Quit"
            elif self.ButtonType == "CC_Menu":
                for b in self.Buttons:
                    if self.Selected == b.Text:
                        if b.Text == "Back":
                            return "Back"
                        else:
                            return b.CC_Value
        elif btn == 0:
            if self.ButtonType == "CC_Menu":
                return "Back"
        return "None"

    # manage joystick movements
    def joystick_inputs(self, axis):
        # scroll up
        pass

    # check for main menu clicks
    def buttons_hovering(self):
        if self.ButtonType == "Main":
            # on the main menu
            
            # play button
            if self.Buttons[0].mouse_hovering():
                # show the cc buttons
                #self.create_cc_buttons()
                return "CC" # show the cc menu
            
            # quit button
            elif self.Buttons[1].mouse_hovering():
                return "Quit" # quit the game
        elif self.ButtonType == "CC_Menu":
            # on the cc menu
            for b in self.Buttons:
                if b.mouse_hovering():
                    # check if it is the back button
                    if b.Text == "Back":
                        self.create_menu_buttons()
                        return "Back"
                    else:
                        return b.CC_Value
        return "None"

        
