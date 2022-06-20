# button class

import pygame

DefaultFont = "Assets/Fonts/SNES.ttf"

## Colors ##
WHITE = (255, 255, 255)
GRAY = (200, 200, 200)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 204, 0)

class Fade:
    def __init__(self, Size=(800, 600), Position=(0, 0), PauseFrames=5, Increment=0.1):
        self.Visibility = 0.0 # from 0 to 1
        self.Increasing = True
        self.Increment = Increment
        self.PauseFrame = 0
        self.PauseFrames = PauseFrames
        self.Size = Size
        self.Position = Position
        self.Peaked = False

    # reset the fade
    def reset(self):
        self.Visibility = 0.0
        self.Increasing = True
        self.PauseFrame = 0
        self.Peaked = False

    # increment the visibility
    def increment(self):
        if self.Visibility == 1 and self.PauseFrame <= self.PauseFrames:
            self.PauseFrame += 1
        else:
            if self.Increasing:
                self.Visibility += self.Increment
                if self.Visibility >= 1:
                    self.Visibility = 1
                    self.Increasing = False
            else:
                self.Visibility -= self.Increment
                if self.Visibility < 0:
                    self.Visibility = 0

    # check if it is at the peak
    def at_peak(self):
        if self.Visibility == 1:
            return True
        return False

    # check if it is finished
    def at_finish(self):
        if self.Visibility == 0 and not self.Increasing and not self.Peaked:
            self.Peaked = True
            return True
        return False

    def render(self):
        self.increment()
        
        s = pygame.Surface(self.Size)
        s.set_alpha(self.Visibility*255)
        s.fill((0, 0, 0))

        return s, self.Position

class Button:
    def __init__(self, Size=(40, 26), Position=(0, 0)):
        self.Position = Position
        #self.AnchorPoint = AnchorPoint
        self.Size = Size
        self.Enabled = True

    def mouse_hovering(self):
        mouse = pygame.mouse.get_pos()
        if (self.Position[0]-self.Size[0]/2 <= mouse[0] <= self.Position[0]+self.Size[0]/2
            and self.Position[1]-self.Size[1]/2 <= mouse[1] <= self.Position[1]+self.Size[1]/2):
            return True
        return False

class TextButton(Button):
    def __init__(self, Size=(40, 26), Position=(0, 0), Text="TextButton", TextColor=BLACK, TextSize=25, Font=DefaultFont):
        super().__init__(Size, Position)
        self.Text = Text
        self.TextSize = TextSize
        self.TextColor = TextColor
        self.Font = Font
        self.LoadedFont = pygame.font.Font(Font, TextSize)

    def render(self):
        btn = self.LoadedFont.render(self.Text, False, self.TextColor)
        btn_rect = btn.get_rect()
        btn_rect.center = self.Position
        return btn, btn_rect

class ImageButton(Button):
    def __init__(self, Image, Size=(40, 26), Position=(0, 0)):
        super().__init__(Size, Position)
        self.Image = Image

    def render(self):
        return self.Image, self.Position

    def mouse_hovering(self):
        mouse = pygame.mouse.get_pos()
        if (self.Position[0] <= mouse[0] <= self.Position[0]+self.Size[0]
            and self.Position[1] <= mouse[1] <= self.Position[1]+self.Size[1]):
            return True
        return False

class TextLabel:
    def __init__(self, Position=(0, 0), Text="TextLabel", TextColor=BLACK, TextSize=25, Font=DefaultFont):
        self.Position = Position
        self.Text = Text
        self.TextColor = TextColor
        self.TextSize = TextSize
        self.Font = Font
        self.LoadedFont = pygame.font.Font(Font, TextSize)

    def render(self):
        text = self.LoadedFont.render(self.Text, False, self.TextColor)
        text_rect = text.get_rect()
        text_rect.center = self.Position
        return text, text_rect
        
