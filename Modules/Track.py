# track class

# OFFSET FROM START THING:
# x = 10
# y = 12

from PyGame3D import Engine_3D

COIN = Engine_3D.get_image("Assets/Sprites/Coin.png")
BOX = Engine_3D.get_image("Assets/Sprites/ItemBox.png")
cy = 2.5
by = 2.5

# types of checkpoints:
#       0 = regular
#       1 = key checkpoint
#       2 = finish line

# checkpoint array style:
# [point 1: (x, z), point 2: (x, z), type]

## Texture Paths ##
Basic = "Assets/Textures/BasicBlocks"

# Color sets for walls
WallColorSets = {
    "BasicBlocks": {
        0: (0, 0, 0),
        10: (232, 232, 0),
        20: (0, 32, 247),
        30: (232, 0, 0),
        40: (0, 232, 0)
    },

    "VanillaLake": {
        0: (0, 0, 0),
        10: (232, 232, 0),
        20: (0, 32, 247),
        30: (232, 0, 0),
        40: (0, 232, 0),
        69: (160, 192, 248)
    },

    "GhostValley": {
        0: (32, 16, 0),
        10: (72, 64, 40),
        20: (72, 64, 40)#(176, 160, 112)
    },

    "BowserCastle": {
        0: (176*0.65, 160*0.65, 160*0.65),
        50: (64, 48, 48)
    }
}

# Height sets for walls
WallHeightSets = {
    "BasicBlocks": {
        0: (5.5, 0),
        10: (5.5, 0),
        20: (5.5, 0),
        30: (5.5, 0),
        40: (5.5, 0)
    },

    "VanillaLake": {
        0: (5.5, 0),
        10: (5.5, 0),
        20: (5.5, 0),
        30: (5.5, 0),
        40: (5.5, 0),
        69: (5.5, 0) #4.5
    },

    "GhostValley": {
        0: (5.5, 0),
        10: (5.5, 0),
        20: (5.5, 0)
    },

    "BowserCastle": {
        0: (5.5, 0),
        50: (0, 0)
    }
}

WallTextureSets = {
    "BasicBlocks": {
        10: Basic+"/Yellow.png",
        20: Basic+"/Blue.png",
        30: Basic+"/Red.png",
        40: Basic+"/Green.png"
    }
}

class Track:
    def __init__(self, TrackName, Map, Sky, HeightMap, MiniMap, Checkpoints, MapScale=30, SkyHeight=1.0, Laps=3, JumpHeight=0.5, SpawnPosition=(0.0, 0.0, 0.0, 0.0), CoinPositions=[], MusicFolder="Sounds/Music/Tracks/MarioCircuit", WallColors={}, WallHeights={}, WallTextures={}, Sprites=[], SpriteImgs=[]):
        self.Name = TrackName
        self.Map = Engine_3D.parse_texture(Engine_3D.get_image(Map))
        self.Sky = Sky
        self.SkyHeight = SkyHeight
        self.Laps = Laps
        self.HeightMap = HeightMap
        self.MiniMap = Engine_3D.get_image(MiniMap)
        self.Checkpoints = Checkpoints
        self.MapScale = MapScale
        self.JumpHeight = JumpHeight
        
        self.CoinPositions = CoinPositions
        self.SpawnPosition = SpawnPosition[0]
        self.SpawnRotation = SpawnPosition[1]
        self.WallColors = WallColors
        self.WallHeights = WallHeights
        self.WallTextures = WallTextures

        self.Sprites = Sprites
        self.SpriteImgs = SpriteImgs

        self.MusicFolder = MusicFolder

    def load_track(self, Camera):
        Camera.set_map(self.Map, self.MapScale)
        Camera.set_sky(Engine_3D.get_image(self.Sky), self.SkyHeight)
        Camera.set_height_map(Engine_3D.parse_texture(Engine_3D.get_image(self.HeightMap)))
        if len(self.WallHeights) > 0:
            Camera.set_wall_heights(self.WallHeights)
        if len(self.WallColors) > 0:
            Camera.set_wall_colors(self.WallColors)

        if self.Name == "BowserCastle" or self.Name == "BowserCastle2":
            Camera.HasShadows = False
        #if len(self.WallTextures) > 0:
            #Camera.load_textures(self.WallTextures)

    def spawn_coins(self, Camera):
        Coins = []
        for c in self.CoinPositions:
            Coin = Engine_3D.Sprite([COIN], 20, c, True)
            Camera.add_sprite(Coin)
            Coins.append(Coin)
        return Coins

    def spawn_boxes(self, Camera):
        Boxes = []
        for b in self.BoxPositions:
            Box = Engine_3D.Sprite([BOX], 15, b, True)
            Camera.add_sprite(Box)
            Boxes.append(Box)
        return Boxes

    def spawn_sprites(self, Camera):
        if len(self.Sprites) > 0 and len(self.SpriteImgs) > 0:
            # load the images
            loaded = []
            for i in self.SpriteImgs:
                loaded.append(i)
                
            # spawn the sprites
            for s in self.Sprites:
                pos = s[0]
                size = s[1]
                img = loaded[s[2]]
                Sp = Engine_3D.Sprite([img], size, pos, True)
                Sp.Shadows = s[3]
                Camera.add_sprite(Sp)

    def get_minimap_pos(self, posx, posy):
        x = (posx/len(self.Map))*4200
        y = (posy/len(self.Map[0]))*4200
        return x, y


class Tracks:
    def __init__(self):
        # create each track
        self.MarioCircuit = Track(
            "MarioCircuit", # track name
            'Assets/Tracks/MarioCircuit/blank_track.png', # floor texture
            'Assets/Sky/MC.png', # sky texture
            'Assets/Tracks/MarioCircuit/height_map.png', # heightmap
            'Assets/Tracks/MarioCircuit/map.png', # minimap
            [
                [(815, 559), (1015, 559), 2], # finish line
                [(647, 7), (647, 375), 1], #[(647, 375), (864, 159), 1],
                [(7, 357), (167, 357), 1],
                [(777, 815), (777, 1015), 1]
                ],
            40, # map scale
            0.6, # sky size
            3, # number of laps
            0.5, # ramp jump height
            ((918, 1, 589), 270.01), # spawn position  #751
            
            [(587, cy, 243), # coin positions
             (603, cy, 243),
             (587, cy, 259),
             (571, cy, 243),
             (587, cy, 228),
             (507, cy, 187),
             (523, cy, 203),
             (540, cy, 187),
             (540, cy, 219),
             (507, cy, 219),
             (51, cy, 459),
             (67, cy, 459),
             (83, cy, 459),
             (75, cy, 523),
             (91, cy, 523),
             (107, cy, 523),
             (363, cy, 115),
             (395, cy, 115),
             (379, cy, 132),
             (363, cy, 147),
             (395, cy, 147),
             (451, cy, 155),
             (451, cy, 171),
             (435, cy, 171),
             (467, cy, 171),
             (451, cy, 187),
             (523, cy, 587),
             (523, cy, 603),
             (523, cy, 620),
             (507, cy, 603),
             (539, cy, 603),
             (779, cy, 947),
             (795, cy, 947),
             (811, cy, 947),
             (827, cy, 947)
            ],

            "Sounds/Music/Tracks/MarioCircuit", # music folder

            #{0: (0, 0, 0), # wall colors
            #10: (232, 232, 0),
            #20: (0, 32, 247),
            #30: (232, 0, 0),
            #40: (0, 232, 0)
            #110: (152, 152, 0),
            #120: (0, 0, 96),
            #130: (120, 0, 0),
            #140: (0, 136, 0)
            #},

            #{ # wall heights
                #0: (5.5, 0),
                #10: (5.5, 0),
                #20: (5.5, 0),
                #30: (5.5, 0),
                #40: (5.5, 0)
            #},
            WallColorSets["BasicBlocks"], # wall colors
            WallHeightSets["BasicBlocks"], # wall heights

            WallTextureSets["BasicBlocks"] # wall textures

            #[ # track sprite positions
                #[(0, 0, 0), 15, 0, False] # (pos), size, img id, shadows
            #],

            #[ # sprite images
                #"Assets/Tracks/Hazards/Pipe.png"
            #]
        )

        self.MarioCircuit2 = Track(
            "MarioCircuit2", # track name
            'Assets/Tracks/MarioCircuit2/track.png', # floor texture
            'Assets/Sky/MC.png', # sky texture
            'Assets/Tracks/MarioCircuit2/height_map.png', # heightmap
            'Assets/Tracks/MarioCircuit2/map.png', # minimap
            [
                [(775, 415), (1015, 415), 2], # finish line
                [(7, 365), (151, 365), 1],
                [(497, 383), (497, 511), 1],
                [(375, 815), (375, 1015), 1],
                [(262, 631), (262, 775), 1]
                ],
            50, # map scale
            0.6, # sky size
            3, # number of laps
            0.5, # ramp jump height
            ((902, 1, 453), 270.01), # spawn position

            [ # coin positions
                (861, cy, 345),
                (877, cy, 329),
                (893, cy, 313),
                (755, cy, 304),
                (755, cy, 272),
                (665, cy, 245),
                (653, cy, 257),
                (637, cy, 273),
                (635, cy, 219),
                (619, cy, 219),
                (603, cy, 219),
                (51, cy, 387),
                (51, cy, 403),
                (51, cy, 419),
                (531, cy, 472),
                (565, cy, 481),
                (582, cy, 506),
                (582, cy, 531),
                (579, cy, 891),
                (563, cy, 907),
                (547, cy, 923),
                (531, cy, 907),
                (515, cy, 891),
                (499, cy, 875),
                (483, cy, 891),
                (467, cy, 907),
                (451, cy, 923),
                (435, cy, 907),
                (419, cy, 891),
                (403, cy, 875),
                (387, cy, 891),
                (371, cy, 907),
                (355, cy, 923),
                (339, cy, 907),
                (323, cy, 891),
                (307, cy, 875),
                (101, cy, 773),
                (117, cy, 757),
                (133, cy, 741),
                (779, cy, 729),
                (795, cy, 729),
                (811, cy, 729)
            ],

            "Sounds/Music/Tracks/MarioCircuit", # music folder
            
            WallColorSets["BasicBlocks"], # wall colors
            WallHeightSets["BasicBlocks"] # wall heights
        )

        self.MarioCircuit3 = Track(
            "MarioCircuit3", # track name
            'Assets/Tracks/MarioCircuit3/track.png', # floor texture
            'Assets/Sky/MC.png', # sky texture
            'Assets/Tracks/MarioCircuit3/height_map.png', # heightmap
            'Assets/Tracks/MarioCircuit3/map.png', # minimap
            [
                [(7, 431), (167, 431), 2], # finish line
                [(511, 231), (511, 375), 1],
                [(247, 579), (447, 579), 1],
                [(847, 783), (1015, 783), 1],
                [(239, 919), (239, 1015), 1]
            ],
            50, # map scale
            0.6, # sky size
            3, # number of laps
            0.5, # ramp jump height
            ((94, 1, 462), 270.01), # spawn position

            [ # coin positions
                (64, cy, 326),
                (80, cy, 326),
                (96, cy, 326),
                (104, cy, 88),
                (120, cy, 104),
                (136, cy, 120),
                (211, cy, 84),
                (211, cy, 68),
                (211, cy, 52),
                (605, cy, 277),
                (621, cy, 293),
                (637, cy, 309),
                (917, cy, 348),
                (902, cy, 382),
                (869, cy, 398),
                (443, cy, 523),
                (427, cy, 539),
                (411, cy, 555),
                (403, cy, 571),
                (403, cy, 603),
                (411, cy, 619),
                (427, cy, 635),
                (443, cy, 651),
                (403, cy, 587),
                (419, cy, 587),
                (387, cy, 587),
                (371, cy, 587),
                (355, cy, 587),
                (339, cy, 587),
                (335, cy, 571),
                (355, cy, 603),
                (662, cy, 616),
                (662, cy, 632),
                (662, cy, 648),
                (790, cy, 616),
                (790, cy, 632),
                (790, cy, 648),
                (621, cy, 817),
                (605, cy, 833),
                (589, cy, 849),
                (481, cy, 841),
                (467, cy, 827),
                (453, cy, 813)
            ],

            "Sounds/Music/Tracks/MarioCircuit", # music folder

            WallColorSets["BasicBlocks"], # wall colors
            WallHeightSets["BasicBlocks"] # wall heights
        )

        self.MarioCircuit4 = Track(
            "MarioCircuit4", # track name
            'Assets/Tracks/MarioCircuit4/track.png', # floor texture
            'Assets/Sky/MC.png', # sky texture
            'Assets/Tracks/MarioCircuit4/height_map.png', # heightmap
            'Assets/Tracks/MarioCircuit4/map.png', # minimap
            [
                [(847, 559), (1015, 559), 2], # finish line
                [(527, 391), (527, 511), 1],
                [(7, 262), (151, 262), 1],
                [(663, 646), (839, 646), 1],
                [(7, 834), (183, 834), 1]
            ],
            50, # map scale
            0.6, # sky size
            3, # number of laps
            0.5, # ramp jump height
            ((918, 1, 589), 270.01), # spawn position

            [ # coin positions
                (918, cy, 259),
                (934, cy, 259),
                (950, cy, 259),
                (899, cy, 150),
                (843, cy, 150),
                (787, cy, 126),
                (729, cy, 162),
                (713, cy, 145),
                (697, cy, 129),
                (680, cy, 242),
                (413, cy, 113),
                (429, cy, 97),
                (445, cy, 81),
                (299, cy, 534),
                (299, cy, 550),
                (299, cy, 566),
                (331, cy, 558),
                (331, cy, 574),
                (331, cy, 590),
                (363, cy, 534),
                (363, cy, 550),
                (363, cy, 566),
                (395, cy, 558),
                (395, cy, 574),
                (395, cy, 590),
                (427, cy, 534),
                (427, cy, 550),
                (427, cy, 566),
                (685, cy, 609),
                (702, cy, 643),
                (685, cy, 685),
                (571, cy, 796),
                (571, cy, 811),
                (571, cy, 827)
            ],

            "Sounds/Music/Tracks/MarioCircuit", # music folder

            WallColorSets["BasicBlocks"], # wall colors
            WallHeightSets["BasicBlocks"] # wall heights
        )

        self.ChocoIsland1 = Track(
            "ChocoIsland1", # track name
            'Assets/Tracks/ChocoIsland1/track.png', # floor texture
            'Assets/Sky/CI.png', # sky texture
            'Assets/Tracks/ChocoIsland1/height_map.png', # heightmap
            'Assets/Tracks/ChocoIsland1/map.png', # minimap
            [
                [(647, 559), (1015, 559), 2], # finish line
                [(135, 279), (312, 279), 1],
                [(7, 615), (159, 615), 1],
                [(167, 839), (167, 1015), 1]
            ],
            50, # map scale
            0.6, # sky size
            3, # number of laps
            0.2, # ramp jump height
            ((878, 1, 587), 270.01), # spawn position

            [ # coin positions
                (867, cy, 507),
                (889, cy, 507),
                (867, cy, 475),
                (889, cy, 475),
                (883, cy, 491),

                (811, cy, 419),
                (843, cy, 419),
                (811, cy, 387),
                (843, cy, 387),
                (827, cy, 403),

                (779, cy, 363),
                (804, cy, 339),
                (779, cy, 307),

                (228, cy, 355),
                (244, cy, 355),
                (260, cy, 355),
                (276, cy, 355),
                (292, cy, 355),

                (147, cy, 491),
                (147, cy, 507),
                (147, cy, 523),
                (131, cy, 507),
                (163, cy, 507),

                (75, cy, 643),
                (75, cy, 659),
                (75, cy, 675),
                (115, cy, 739),
                (115, cy, 755),
                (115, cy, 771),

                (227, cy, 931),
                (227, cy, 963),
                (243, cy, 947),
                (259, cy, 931),
                (259, cy, 963),

                (275, cy, 907),
                (275, cy, 939),
                (291, cy, 923),
                (307, cy, 907),
                (307, cy, 939),

                (291, cy, 851),
                (291, cy, 883),
                (307, cy, 867),
                (323, cy, 851),
                (323, cy, 883),

                (331, cy, 835),
                (331, cy, 867),
                (347, cy, 851),
                (363, cy, 835),
                (363, cy, 867)
            ],

            "Sounds/Music/Tracks/ChocoIsland", # music folder

            WallColorSets["BasicBlocks"], # wall colors
            WallHeightSets["BasicBlocks"] # wall heights
        )

        self.FrankBeach1 = Track(
            "FrankBeach1", # track name
            'Assets/Tracks/FrankBeach1/track.png', # floor texture
            'Assets/Sky/FB.png', # sky texture
            'Assets/Tracks/FrankBeach1/height_map.png', # heightmap
            'Assets/Tracks/FrankBeach1/map.png', # minimap
            [
                [(21, 255), (309, 255), 2], # finish line
                [(423, 6), (423, 231), 1],
                [(605, 325), (1019, 325), 1],
                [(787, 444), (960, 1015), 1],
                [(219, 695), (219, 998), 1],
                [(4, 686), (171, 686), 1]
            ],
            50, # map scale
            0.6, # sky size
            3, # number of laps
            0.35, # ramp jump height
            ((182, 1, 285), 270.01), # spawn position

            [ # coin positions
                (219, cy, 147),
                (235, cy, 131),
                (251, cy, 115),

                (355, cy, 115),
                (355, cy, 131),
                (355, cy, 147),
                (507, cy, 91),
                (507, cy, 107),
                (507, cy, 123),
                (619, cy, 123),
                (619, cy, 139),
                (619, cy, 155),

                (819, cy, 299),
                (867, cy, 315),

                (883, cy, 683),
                (883, cy, 715),
                (915, cy, 683),
                (915, cy, 715),
                (899, cy, 699),

                (875, cy, 731),
                (875, cy, 747),
                (875, cy, 763),
                (859, cy, 747),
                (891, cy, 747),

                (827, cy, 779),
                (827, cy, 811),
                (859, cy, 779),
                (859, cy, 811),
                (843, cy, 795),

                (275, cy, 747),
                (275, cy, 763),
                (275, cy, 779),

                (283, cy, 899),
                (299, cy, 899),
                (315, cy, 899),

                (115, cy, 491),
                (131, cy, 515),
                (147, cy, 491),
                (179, cy, 467)
            ],

            "Sounds/Music/Tracks/FrankBeach", # music folder
        )

        self.DonutPlains1 = Track(
            "DonutPlains1", # track name
            'Assets/Tracks/DonutPlains1/track.png', # floor texture
            'Assets/Sky/DP.png', # sky texture
            'Assets/Tracks/DonutPlains1/height_map.png', # heightmap
            'Assets/Tracks/DonutPlains1/map.png', # minimap
            [
                [(7, 511), (239, 511), 2], # finish line
                [(503, 71), (503, 135), 1],
                [(838, 783), (838, 1015), 1],
                [(575, 582), (703, 582), 1]
            ],
            50, # map scale
            0.6, # sky size
            3, # number of laps
            0.3, # ramp jump height
            ((143, 1, 545), 270.01), # spawn position

            [ # coin positions
                (133, cy, 466),
                (101, cy, 466),
                (117, cy, 450),
                (101, cy, 434),
                (133, cy, 434),
                (221, cy, 153),
                (244, cy, 169),
                (284, cy, 113),
                (316, cy, 137),
                (616, cy, 91),
                (616, cy, 107),
                (616, cy, 123),
                (922, cy, 214),
                (922, cy, 246),
                (938, cy, 230),
                (954, cy, 214),
                (954, cy, 246),
                (772, cy, 478),
                (804, cy, 478),
                (772, cy, 510),
                (804, cy, 510),
                (788, cy, 494),
                (907, cy, 905),
                (907, cy, 921),
                (907, cy, 937),
                (891, cy, 921),
                (923, cy, 921),
                (597, cy, 493),
                (613, cy, 493),
                (629, cy, 493),
                (613, cy, 509),
                (613, cy, 477),
                (571, cy, 467),
                (587, cy, 452),
                (603, cy, 435),
                (539, cy, 435),
                (555, cy, 419),
                (571, cy, 403),
                (386, cy, 485),
                (369, cy, 501),
                (353, cy, 518),
                (419, cy, 830),
                (371, cy, 894),
                (323, cy, 854),
                (315, cy, 894),
                (243, cy, 822)
            ],

            "Sounds/Music/Tracks/DonutPlains", # music folder

            WallColorSets["BasicBlocks"], # wall colors
            WallHeightSets["BasicBlocks"] # wall heights
        )

        self.DonutPlains2 = Track(
            "DonutPlains2", # track name
            'Assets/Tracks/DonutPlains2/track.png', # floor texture
            'Assets/Sky/DP.png', # sky texture
            'Assets/Tracks/DonutPlains2/height_map.png', # heightmap
            'Assets/Tracks/DonutPlains2/map.png', # minimap
            [
                [(855, 575), (1015, 575), 2], # finish line
                [(431, 7), (431, 151), 1],
                [(311, 687), (415, 687), 1],
                [(663, 167), (663, 295), 1],
                [(847, 831), (847, 1015), 1]
            ],
            55, # map scale
            0.6, # sky size
            3, # number of laps
            0.3, # ramp jump height
            ((910, 1, 595), 270.01), # spawn position

            [ # coin positions
                (923, cy, 414),
                (939,  cy, 414),
                (955, cy, 414),
                (915, cy, 342),
                (931, cy, 342),
                (947, cy, 342),
                (601, cy, 53),
                (585, cy, 69),
                (569, cy, 85),
                (541, cy, 78),
                (525, cy, 61),
                (509, cy, 45),
                (84, cy, 460),
                (100, cy, 460),
                (116, cy, 460),
                (275, cy, 595),
                (275, cy, 611),
                (275, cy, 627),
                (275, cy, 643),
                (134, cy, 867),
                (134, cy, 883),
                (134, cy, 899),
                
                (571, cy, 275),
                (587, cy, 259),
                (603, cy, 243),
                (619, cy, 259),
                (619, cy, 227),
                (635, cy, 243),
                (651, cy, 227),
                (651, cy, 259),
                (667, cy, 243),
                (683, cy, 259),
                (699, cy, 275),

                (725, cy, 555),
                (757, cy, 555),
                (739, cy, 699),
                (763, cy, 739)
            ],

            "Sounds/Music/Tracks/DonutPlains", # music folder

            WallColorSets["BasicBlocks"], # wall colors
            WallHeightSets["BasicBlocks"] # wall heights
        )

        self.DonutPlains3 = Track(
            "DonutPlains3", # track name
            'Assets/Tracks/DonutPlains3/track.png', # floor texture
            'Assets/Sky/DP.png', # sky texture
            'Assets/Tracks/DonutPlains3/height_map.png', # heightmap
            'Assets/Tracks/DonutPlains3/map.png', # minimap
            [
                [(7, 527), (255, 527), 2], # finish line
                [(374, 7), (374, 263), 1],
                [(621, 279), (621, 447), 1],
                [(879, 751), (1015, 751), 1]
            ],
            55, # map scale
            0.6, # sky size
            3, # number of laps
            0.3, # ramp jump height
            ((110, 1, 547), 270.01), # spawn position

            [ # coin positions
                (99, cy, 459),
                (131, cy, 459),
                (115, cy, 443),
                (99, cy, 427),
                (131, cy, 427),

                (107, cy, 395),

                (188, cy, 179),
                (204, cy, 179),
                (220, cy, 179),
                
                (906, cy, 243),
                (922, cy, 243),
                (938, cy, 243),
                (914, cy, 323),
                (930, cy, 323),
                (946, cy, 323),

                (603, cy, 579),
                (619, cy, 595),
                (635, cy, 611),

                (859, cy, 851),
                (891, cy, 851),
                (875, cy, 867),
                (859, cy, 883),
                (891, cy, 883),

                (403, cy, 659),
                (435, cy, 659),
                (419, cy, 675),
                (403, cy, 691),
                (435, cy, 691),
                (403, cy, 715),
                (435, cy, 715),
                (419, cy, 731),
                (403, cy, 747),
                (435, cy, 747),

                (267, cy, 867),
                (219, cy, 867),
                (219, cy, 931),
                (179, cy, 931),
                (147, cy, 891),
                (195, cy, 827)
            ],

            "Sounds/Music/Tracks/DonutPlains", # music folder

            WallColorSets["BasicBlocks"], # wall colors
            WallHeightSets["BasicBlocks"] # wall heights
        )
        
        self.RainbowRoad = Track(
            "RainbowRoad", # track name
            'Assets/Tracks/RainbowRoad/track.png', # floor texture
            'Assets/Sky/RR.png', # sky texture
            'Assets/Tracks/RainbowRoad/height_map.png', # heightmap
            'Assets/Tracks/RainbowRoad/map.png', # minimap
            [
                [(0, 431), (131, 431), 2], # finish line
                [(0, 131), (131, 131), 1],
                [(404, 0), (404, 93), 1],
                [(684, 0), (684, 93), 1],
                [(665, 358), (834, 358), 1],
                [(393, 375), (393,468), 1],
                [(243, 538), (412, 538), 1],
                [(903, 609), (903, 702), 1],
                [(900, 794), (1016, 794), 1],
                [(833, 879), (833, 972), 1],
                [(763, 879), (763, 972), 1],
                [(693, 879), (693, 972), 1],
                [(603, 879), (603, 972), 1],
                [(513, 879), (513, 972), 1],
                [(173, 879), (173, 972), 1],
                [(0, 761), (131, 761), 1]
            ],
            50, # map scale
            0.6, # sky size
            3, # number of laps
            0.25, # ramp jump height
            ((74, 1, 448), 270.01), # spawn position

            [ # coin positions
                (49, cy, 390),
                (65, cy, 390),
                (81, cy, 390),
                (45, cy, 334),
                (58, cy, 334),
                (73, cy, 334),
                (171, cy, 27),
                (171, cy, 43),
                (171, cy, 59),
                (451, cy, 27),
                (451, cy, 44),
                (451, cy, 59),
                (619, cy, 27),
                (619, cy, 43),
                (619, cy, 59),
                (729, cy, 77),
                (745, cy, 61),
                (761, cy, 45),
                (734, cy, 355),
                (750, cy, 355),
                (766, cy, 355),
                (699, cy, 408),
                (699, cy, 424),
                (699, cy, 440),
                (294, cy, 491),
                (310, cy, 491),
                (326, cy, 491),
                (294, cy, 603),
                (310, cy, 603),
                (326, cy, 603),
                (595, cy, 638),
                (595, cy, 654),
                (595, cy, 670),
                (942, cy, 715),
                (958, cy, 715),
                (974, cy, 715),
                (944, cy, 827),
                (960, cy, 827),
                (976, cy, 827),
                (907, cy, 910),
                (907, cy, 926),
                (907, cy, 942),
                (459, cy, 936),
                (459, cy, 952),
                (459, cy, 968),
                (179, cy, 912),
                (179, cy, 928),
                (179, cy, 944),
                (48, cy, 843),
                (64, cy, 843),
                (80, cy, 843)
            ],

            "Sounds/Music/Tracks/RainbowRoad", # music folder
        )

        self.ChocoIsland2 = Track(
            "ChocoIsland2", # track name
            'Assets/Tracks/ChocoIsland2/track.png', # floor texture
            'Assets/Sky/CI.png', # sky texture
            'Assets/Tracks/ChocoIsland2/height_map.png', # heightmap
            'Assets/Tracks/ChocoIsland2/map.png', # minimap
            [
                [(7, 655), (168, 655), 2], # finish line
                [(463, 7), (463, 159), 1],
                [(807, 119), (1015, 119), 1],
                [(655, 799), (655, 1015), 1]
            ],
            50, # map scale
            0.6, # sky size
            3, # number of laps
            0.2, # ramp jump height
            ((106, 1, 683), 270.01), # spawn position

            [ # coin positions
                (75, cy, 603),
                (75, cy, 571),
                (107, cy, 571),
                (107, cy, 603),
                (91, cy, 587),

                (91, cy, 507),
                (91, cy, 539),
                (123, cy, 507),
                (123, cy, 539),
                (107, cy, 523),

                (243, cy, 59),
                (243, cy, 75),
                (243, cy, 91),

                (803, cy, 67),
                (819, cy, 83),
                (835, cy, 99),
                (851, cy, 155),
                (835, cy, 171),
                (819, cy, 187),

                (731, cy, 283),
                (731, cy, 299),
                (731, cy, 315),
                (715, cy, 299),
                (747, cy, 299),

                (835, cy, 539),
                (835, cy, 555),
                (835, cy, 571),

                (811, cy, 699),
                (811, cy, 715),
                (811, cy, 731),
                (795, cy, 715),
                (827, cy, 715),

                (347, cy, 843),
                (347, cy, 859),
                (347, cy, 875),
                (179, cy, 923),
                (179, cy, 939),
                (179, cy, 955)
            ],

            "Sounds/Music/Tracks/ChocoIsland", # music folder

            WallColorSets["BasicBlocks"], # wall colors
            WallHeightSets["BasicBlocks"] # wall heights
        )

        self.VanillaLake1 = Track(
            "VanillaLake1", # track name
            'Assets/Tracks/VanillaLake1/track.png', # floor texture
            'Assets/Sky/VL.png', # sky texture
            'Assets/Tracks/VanillaLake1/height_map.png', # heightmap
            'Assets/Tracks/VanillaLake1/map.png', # minimap
            [
                [(7, 527), (255, 527), 2], # finish line
                [(847, 559), (935, 559), 1],
                [(772, 609), (772, 1015), 1],
                [(599, 823), (599, 903), 1],
                [(303, 666), (303, 1015), 1]
            ],
            55, # map scale
            0.6, # sky size
            3, # number of laps
            0.5, # ramp jump height
            ((189, 1, 559), 270.01), # spawn position

            [ # coin positions
                (147, cy, 435),
                (171, cy, 403),
                (187, cy, 363),
                
                (169, cy, 323),
                (185, cy, 323),
                (201, cy, 323),

                (187, cy, 267),
                (243, cy, 211),

                (299, cy, 179),
                (299, cy, 195),
                (299, cy, 211),

                (825, cy, 379),
                (857, cy, 379),
                (825, cy, 411),
                (857, cy, 411),
                (841, cy, 395),

                (825, cy, 443),
                (825, cy, 459),
                (825, cy, 475),
                (809, cy, 459),
                (841, cy, 459),

                (883, cy, 499),
                (883, cy, 515),
                (883, cy, 531),
                (867, cy, 515),
                (899, cy, 515),

                (571, cy, 835),
                (555, cy, 875),
                (523, cy, 859),

                (267, cy, 835),
                (299, cy, 835),
                (267, cy, 867),
                (299, cy, 867),
                (283, cy, 851)
            ],

            "Sounds/Music/Tracks/VanillaLake", # music folder

            WallColorSets["VanillaLake"], # wall colors
            WallHeightSets["VanillaLake"] # wall heights
        )

        self.VanillaLake2 = Track(
            "VanillaLake2", # track name
            'Assets/Tracks/VanillaLake2/track.png', # floor texture
            'Assets/Sky/VL.png', # sky texture
            'Assets/Tracks/VanillaLake2/height_map.png', # heightmap
            'Assets/Tracks/VanillaLake2/map.png', # minimap
            [
                [(736, 495), (1015, 495), 2], # finish line
                [(682, 286), (1015, 286), 1],
                [(511, 78), (511, 359), 1],
                [(6, 327), (465, 327), 1],
                [(149, 478), (153, 907), 1],
                [(181, 798), (185, 1016), 1],
                [(262, 883), (1016, 887), 1]
            ],
            55, # map scale
            0.6, # sky size
            3, # number of laps
            0.5, # ramp jump height
            ((869, 1, 535), 270.01), # spawn position

            [ # coin positions
                (875, cy, 427),
                (891, cy, 427),
                (907, cy, 427),
                (875, cy, 395),
                (859, cy, 395),
                (843, cy, 395),

                (315, cy, 211),
                (331, cy, 227),
                (347, cy, 243),

                (129, cy, 706),
                (145, cy, 722),
                (161, cy, 738),
                (177, cy, 754),
                (193, cy, 770),

                (82, cy, 843),
                (98, cy, 859),
                (114, cy, 875),
                (98, cy, 915),
                (114, cy, 931),
                (130, cy, 947),
                (146, cy, 931),
                (162, cy, 947),
                (178, cy, 963),
                (154, cy, 899),
                (170, cy, 915),
                (186, cy, 931),

                (779, cy, 843),
                (795, cy, 811),
                (771, cy, 795),
                (795, cy, 779),
                (819, cy, 787),
                (835, cy, 827),
                (851, cy, 779),
                (867, cy, 747)
            ],

            "Sounds/Music/Tracks/VanillaLake", # music folder

            WallColorSets["VanillaLake"], # wall colors
            WallHeightSets["VanillaLake"] # wall heights
        )

        self.GhostValley1 = Track(
            "GhostValley1", # track name
            'Assets/Tracks/GhostValley1/track.png', # floor texture
            'Assets/Sky/GV.png', # sky texture
            'Assets/Tracks/GhostValley1/height_map.png', # heightmap
            'Assets/Tracks/GhostValley1/map.png', # minimap
            [
                [(927, 575), (1007, 575), 2], # finish line
                [(918, 430), (1012, 430), 1],
                [(918, 260), (1012, 260), 1],
                [(39, 311), (127, 311), 1],
                [(39, 471), (127, 471), 1],
                [(39, 634), (127, 634), 1],
                [(285, 712), (771, 791), 1],
                [(902, 687), (1020, 687), 1]
            ],
            50, # map scale
            0.6, # sky size
            3, # number of laps
            0.25, # ramp jump height
            ((951, 1, 612), 270.01), # spawn position

            [ # coin positions
                (939, cy, 435),
                (955, cy, 419),
                (971, cy, 403),
                (963, cy, 355),
                (979, cy, 339),
                (995, cy, 323),

                (619, cy, 125),
                (619, cy, 141),
                (619, cy, 157),

                (555, cy, 165),
                (539, cy, 165),
                (523, cy, 165),

                (67, cy, 411),
                (99, cy, 411),
                (67, cy, 443),
                (99, cy, 443),
                (51, cy, 427),
                (83, cy, 427),
                (115, cy, 427),

                (771, cy, 723),
                (787, cy, 723),
                (803, cy, 723),
                (819, cy, 723),

                (707, cy, 931),
                (739, cy, 931),
                (707, cy, 963),
                (739, cy, 963),
                (723, cy, 947),
                
                (755, cy, 939),
                (787, cy, 939),
                (755, cy, 971),
                (787, cy, 971),
                (771, cy, 955),

                (803, cy, 923),
                (835, cy, 923),
                (803, cy, 955),
                (835, cy, 955),
                (819, cy, 939)
            ],

            "Sounds/Music/Tracks/GhostValley", # music folder

            WallColorSets["GhostValley"], # wall colors
            WallHeightSets["GhostValley"] # wall heights
        )

        self.GhostValley2 = Track(
            "GhostValley2", # track name
            'Assets/Tracks/GhostValley2/track.png', # floor texture
            'Assets/Sky/GV.png', # sky texture
            'Assets/Tracks/GhostValley2/height_map.png', # heightmap
            'Assets/Tracks/GhostValley2/map.png', # minimap
            [
                [(47, 287), (127, 287), 2], # finish line
                [(327, 269), (407, 269), 1],
                [(483, 311), (483, 432), 1],
                [(676, 383), (1223, 431), 1],
                [(658, 481), (1009, 867), 1],
                [(567, 806), (647, 806), 1],
                [(513, 911), (513, 991), 1],
                [(47, 295), (127, 755), 1]
            ],
            50, # map scale
            0.6, # sky size
            3, # number of laps
            0.25, # ramp jump height
            ((103, 1, 320), 270.01), # spawn position

            [ # coin positions
                (83, cy, 123),
                (83, cy, 155),
                (115, cy, 123),
                (115, cy, 155),
                (99, cy, 139),

                (515, cy, 325),
                (515, cy, 341),
                (515, cy, 357),
                (515, cy, 373),

                (907, cy, 451),
                (923, cy, 451),
                (939, cy, 451),
                (955, cy, 451),
                (971, cy, 451),
                (987, cy, 451),

                (899, cy, 491),
                (915, cy, 491),
                (931, cy, 491),
                (947, cy, 491),
                (963, cy, 491),
                (979, cy, 491),
                (995, cy, 491),

                (907, cy, 531),
                (923, cy, 531),
                (939, cy, 531),
                (955, cy, 531),
                (971, cy, 531),
                (987, cy, 531),

                (763, cy, 651),
                (763, cy, 667),
                (763, cy, 683),
                (763, cy, 699),

                (571, cy, 915),
                (587, cy, 931),
                (603, cy, 947),
                (619, cy, 963),

                (259, cy, 845),
                (259, cy, 861),
                (259, cy, 877),
                (259, cy, 893)
            ],

            "Sounds/Music/Tracks/GhostValley", # music folder

            WallColorSets["GhostValley"], # wall colors
            WallHeightSets["GhostValley"] # wall heights
        )

        self.BowserCastle = Track(
            "BowserCastle", # track name
            'Assets/Tracks/BowserCastle/track.png', # floor texture
            'Assets/Sky/BC.png', # sky texture
            'Assets/Tracks/BowserCastle/height_map.png', # heightmap
            'Assets/Tracks/BowserCastle/map.png', # minimap
            [
                [(894, 655), (959, 655), 2], # finish line
                [(430, 825), (495, 825), 1],
                [(646, 406), (719, 406), 1],
                [(646, 876), (719, 876), 1]
            ],
            50, # map scale
            0.4, # sky size
            3, # number of laps
            0.25, # ramp jump height
            ((920, 1, 687), 270.01), # spawn position

            [ # coin positions
                (907, cy, 387),
                (923, cy, 387),
                (939, cy, 387),
                (915, cy, 275),
                (931, cy, 275),
                (947, cy, 275),
                (907, cy, 131),
                (923, cy, 131),
                (939, cy, 131),

                (571, cy, 29),
                (571, cy, 45),
                (571, cy, 61),
                (571, cy, 77),
                (427, cy, 34),
                (427, cy, 50),
                (427, cy, 66),
                (427, cy, 82),

                (499, cy, 275),
                (507, cy, 299),
                (507, cy, 331),
                (515, cy, 259),
                (523, cy, 315),
                (531, cy, 243),
                (539, cy, 299),
                (539, cy, 331),
                (547, cy, 283),
                (547, cy, 315),
                (547, cy, 251),
                (563, cy, 235),
                (563, cy, 251),
                (563, cy, 267),
                (563, cy, 299),
                (579, cy, 251),
                (579, cy, 283),
                (579, cy, 315),
                (587, cy, 299),
                (587, cy, 331),
                (595, cy, 243),
                (603, cy, 315),
                (611, cy, 259),
                (619, cy, 299),
                (619, cy, 331),
                (627, cy, 275)
            ],

            "Sounds/Music/Tracks/BowserCastle", # music folder

            WallColorSets["BowserCastle"], # wall colors
            WallHeightSets["BowserCastle"] # wall heights
        )

        self.BowserCastle2 = Track(
            "BowserCastle2", # track name
            'Assets/Tracks/BowserCastle2/track.png', # floor texture
            'Assets/Sky/BC.png', # sky texture
            'Assets/Tracks/BowserCastle2/height_map.png', # heightmap
            'Assets/Tracks/BowserCastle2/map.png', # minimap
            [
                [(29, 351), (96, 351), 2], # finish line
                [(478, 37), (478, 138), 1],
                [(639, 37), (1200, 104), 1],
                [(510, 230), (510, 295), 1],
                [(742, 906), (742, 999), 1],
                [(9, 932), (326, 999), 1]
            ],
            50, # map scale
            0.4, # sky size
            3, # number of laps
            0.28, # ramp jump height
            ((78, 1, 383), 270.01), # spawn position

            [ # coin positions
                (43, cy, 267),
                (59, cy, 267),
                (75, cy, 267),
                (51, cy, 195),
                (67, cy, 195),
                (83, cy, 195),

                (907, cy, 91),
                (923, cy, 75),
                (939, cy, 59),

                (723, cy, 299),
                (723, cy, 331),
                (755, cy, 299),
                (755, cy, 331),
                (739, cy, 315),

                (667, cy, 275),
                (667, cy, 307),
                (667, cy, 243),
                (699, cy, 275),
                (669, cy, 307),
                (683, cy, 291),
                (651, cy, 259),
                (635, cy, 243),
                (635, cy, 275),

                (611, cy, 251),
                (611, cy, 283),
                (579, cy, 251),
                (579, cy, 283),
                (595, cy, 267),

                (787, cy, 771),
                (803, cy, 771),
                (819, cy, 771),

                (723, cy, 947),
                (659, cy, 987),
                (603, cy, 955),
                (475, cy, 955),
                (475, cy, 987),
                (371, cy, 955),
                (371, cy, 987),
                (259, cy, 971)
            ],

            "Sounds/Music/Tracks/BowserCastle", # music folder

            WallColorSets["BowserCastle"], # wall colors
            WallHeightSets["BowserCastle"] # wall heights
        )

        self.FrankBeach2 = Track(
            "FrankBeach2", # track name
            'Assets/Tracks/FrankBeach2/track.png', # floor texture
            'Assets/Sky/FB.png', # sky texture
            'Assets/Tracks/FrankBeach2/height_map.png', # heightmap
            'Assets/Tracks/FrankBeach2/map.png', # minimap
            [
                [(546, 287), (857, 287), 2], # finish line
                [(503, 5), (503, 214), 1],
                [(73, 302), (259, 302), 1],
                [(28, 313), (210, 719), 1],
                [(67, 524), (259, 1017), 1],
                [(683, 626), (683, 891), 1],
                [(849, 678), (1010, 678), 1],
                [(860, 530), (981, 530), 1]
            ],
            50, # map scale
            0.6, # sky size
            3, # number of laps
            0.3, # ramp jump height
            ((695, 1, 318), 270.01), # spawn position

            [ # coin positions
                (659, cy, 219),
                (675, cy, 219),
                (691, cy, 219),
                (635, cy, 171),
                (651, cy, 171),
                (667, cy, 171),

                (228, cy, 116),
                (244, cy, 132),
                (260, cy, 148),
                (187, cy, 155),
                (203, cy, 171),
                (219, cy, 187),

                (267, cy, 683),
                (267, cy, 699),
                (267, cy, 715),
                (267, cy, 731),

                (163, cy, 843),
                (179, cy, 843),
                (195, cy, 843),
                (211, cy, 843),
                (227, cy, 843),

                (379, cy, 884),
                (379, cy, 900),
                (379, cy, 916),
                (451, cy, 900),
                (451, cy, 916),
                (451, cy, 932),
                (499, cy, 868),
                (499, cy, 884),
                (499, cy, 900),

                (683, cy, 732),
                (683, cy, 748),
                (683, cy, 764)
            ],

            "Sounds/Music/Tracks/FrankBeach", # music folder

            WallColorSets["BasicBlocks"], # wall colors
            WallHeightSets["BasicBlocks"] # wall heights
        )

TrackList = {
    "Mushroom Cup": [
        ["MarioCircuit", "Mario Circuit 1"],
        ["MarioCircuit2", "Mario Circuit 2"],
        ["MarioCircuit3", "Mario Circuit 3"],
        ["MarioCircuit4", "Mario Circuit 4"],
        ["ChocoIsland1", "Choco Island 1"],
        ["FrankBeach1", "Frank Beach 1"]
    ],
    
    "Star Cup":[
        ["DonutPlains1", "Donut Plains 1"],
        ["DonutPlains2", "Donut Plains 2"],
        ["DonutPlains3", "Donut Plains 3"],
        ["RainbowRoad", "Rainbow Road"],
        ["ChocoIsland2", "Choco Island 2"],
        ["FrankBeach2", "Frank Beach 2"]
    ],
    
    "Special Cup":[
        ["VanillaLake1", "Vanilla Lake 1"],
        ["VanillaLake2", "Vanilla Lake 2"],
        ["GhostValley1", "Ghost Valley 1"],
        ["GhostValley2", "Ghost Valley 2"],
        ["BowserCastle", "Bowser Castle 1"],
        ["BowserCastle2", "Bowser Castle 2"]
    ]
}
