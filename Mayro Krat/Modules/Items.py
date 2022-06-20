# item class
from PyGame3D import Engine_3D
import numpy
import pygame

pygame.init()

ItemHeld = pygame.USEREVENT + 1
ItemDropped = pygame.USEREVENT + 2

class Item:
    def __init__(self, name, icon, holds=False, size=20, drops=False):
        self.Name = name
        self.Icon = icon
        self.Size = size
        self.Holds = holds # whether or not the item can be held behind the driver's back
        self.DropsLightning = drops # if the item drops on the ground when struck by lightning

    def drop(self, Camera, Driver, hasSprite=False, sprite=None):
        rot = Driver.Rotation
        cos, sin = numpy.cos(rot), numpy.sin(rot)
        x = Driver.Sprite.Position.x - 35*cos
        y = 0.8
        z = Driver.Sprite.Position.z - 35*sin
        pos = (x, y, z)
        delattr(Driver, "HoldingItem")
        # create a sprite
        if hasSprite == False:
            item = Engine_3D.Sprite([self.Icon], self.Size, pos, False)
            Camera.add_sprite(item)


class Banana(Item):
    def __init__(self):
        img = Engine_3D.get_image('Assets/Items/Banana/Banana.png')
        super().__init__("Banana", img, True, 8, True)

    def use(self, Camera, Driver):
        #self.drop(Camera, Driver)
        # make the driver hold the item behind their back
        rot = Driver.Rotation
        cos, sin = numpy.cos(rot), numpy.sin(rot)
        x = Driver.Sprite.Position.x*34 - 22*cos
        y = 0.8
        z = Driver.Sprite.Position.z*34 - 22*sin
        pos = (x, y, z)
        
        item = Engine_3D.Sprite([self.Icon], self.Size, pos, False)
        Camera.add_sprite(item)
        #self.InWorld = True
        #self.Sprite = item
        delattr(Driver, "HeldItem")
        Driver.HoldingItem = [item, self]


class Mushroom(Item):
    def __init__(self):
        img = Engine_3D.get_image('Assets/Items/Mushroom/Mushroom.png')
        super().__init__("Mushroom", img, False, 20, True)
        self.Sound = pygame.mixer.Sound("Sounds/Kart/Shroom.wav")

    def use(self, Camera, Driver):
        # speed up the driver
        Driver.boost(3, 150, True)
        self.Sound.play()
        delattr(Driver, "HeldItem")


class DoubleMushroom(Item):
    def __init__(self):
        img = Engine_3D.get_image('Assets/Items/DoubleMushroom/DoubleMushroom.png')
        super().__init__("DoubleMushroom", img, False, 20, True)
        self.Sound = pygame.mixer.Sound("Sounds/Kart/Shroom.wav")

    def use(self, Camera, Driver):
        # speed up the driver (and replace with other shroom)
        Driver.boost(3, 150, True)
        self.Sound.play()
        Driver.HeldItem = ItemList[0]


class TripleMushroom(Item):
    def __init__(self):
        img = Engine_3D.get_image('Assets/Items/TripleMushroom/TripleMushroom.png')
        super().__init__("TripleMushroom", img, False, 20, True)
        self.Sound = pygame.mixer.Sound("Sounds/Kart/Shroom.wav")

    def use(self, Camera, Driver):
        # speed up the driver (and replace with other shrooms)
        Driver.boost(3, 150, True)
        self.Sound.play()
        Driver.HeldItem = ItemList[1]


ItemList = [Mushroom(), DoubleMushroom(), TripleMushroom(), Banana()]

class Items:
    def __init__(self):
        self.Mushroom = ItemList[0]
        self.DoubleMushroom = ItemList[1]
        self.TripleMushroom = ItemList[2]
        self.Banana = ItemList[3]
