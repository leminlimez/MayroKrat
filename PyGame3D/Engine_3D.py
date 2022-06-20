# basic engine for 3D rendering

#import threading
import pygame
import numpy
from numba import njit

from PyGame3D.Modules.Positionals import CFrame
from PyGame3D.Modules.Positionals import Vector3

#### Variables ####

## Config ##
ValidFrames = 1300 # max amount of frames camera is allowed to move before next frame (lag management)
RenderDistance = 1450 # render distance for walls
SpriteDistance = 10 # render distance for sprites

ShadowImg = pygame.image.load('Assets/Sprites/Shadow3.png')

# check whether specified coordinate has collision in heightmap
def has_collision(hm, x, z, wc):
    if (int(x) >= 0 and int(x) < len(hm)
        and int(z) >= 0 and int(z) < len(hm[0])
        and hm[int(x)][int(z)][0] <= 250 and wc[hm[int(x)][int(z)][0]]):
        return True
    return False

# create the rendered frame
@njit(fastmath=True)
def create_frame(frame, Resolution, posx, posy, posz, rot, roty, HasShadows, WallHeights, WallColors, WallShadows, Sky, Floor, Map, MapScale, HeightMap, WallTextures):
    # raycast

    ## Variables ##

    # Resolution Variables #
    hres = Resolution[0]
    vres = Resolution[1]
    mod = hres/60 # scaling factor (fov)
    yoffset = int((vres/4)*posy)
    l_hm = len(HeightMap)-1
    wcomp = (l_hm)/MapScale # wall compensation for positional scaling
    posx = posx*(l_hm/MapScale)
    posz = posz*(l_hm/MapScale)
    #rotoffset = int((vres/2)*roty)
    #skystart = int((vres/2)*0.8 + rotoffset)
    
    # loop through rows of pixels
    for i in range(hres):
        rot_i = rot + numpy.deg2rad(i/mod - 30)
        sin = numpy.sin(rot_i)
        cos =numpy.cos(rot_i)
        correction = numpy.cos(numpy.deg2rad(i/mod - 30)) # corrects the fisheye effect

        ## Sky ##
        
        # apply the sky texture or a base color
        if Sky != None:
            imgid = Sky[int(numpy.rad2deg(rot_i)%360)]
            frame[i][:len(imgid)] = imgid[:]
            frame[i][len(imgid):] = imgid[len(imgid)-1] # continuation of the last pixel
        else:
            frame[i][:] = 230

        # loop through the columns of pixels
        # make sure the y is in bounds
        if posy > -12.5 and posy < 1.7:#1.4:
            for j in range(vres/2):#-1, -1, -1):
                b = 0
                #if posy < 0:
                    #b = (((vres/2) - j)/2)*(numpy.log(abs(posy**(1/3))))
                #elif posy > 0:
                    #b = (((vres/2) - j)/2)*(numpy.log(abs(posy)))
                n = (((vres/2)-yoffset)/((vres/2)-j+(0.00001)))/correction
                x = posx + cos*n
                z = posz + sin*n

                # shading to each part for distance
                #shade = 0.5 + 0.5*(1-j/(vres/2))

                ## Floor ##

                # prioritize drawing map
                if Map != None:
                    # get the image resolution
                    imgresx = len(Map)
                    imgresy = len(Map)
                    
                    # calculating floor pixel
                    fx = int(x/MapScale*(imgresx-1))
                    fz = int(z/MapScale*(imgresy-1))
                    #s = 1
                    
                    # check if the map is within bounds before drawing
                    # this prevents infinite cloning
                    # Old method: if fx == int(x/30*(imgresx-1)) and fz == int(z/30*(imgresy-1)):
                    if fx < len(Map) and fx >= 0 and fz < len(Map[0]) and fz >= 0 and not (HeightMap[fx][fz][0] == 254 and HeightMap[fx][fz][1] == 254):
                        # if there is a wall on top then do not place it
                        #bh = False
                        #if HeightMap != None:
                            #if HeightMap[int(fx-0.5)][int(fz-0.5)][0] <= 250:
                            #if fx-2 < len(HeightMap) and fx >= 0 and fz < len(HeightMap[0]) and fz >= 0 and HeightMap[fx][fz][0] <= 250:
                                #s *= 0.3
                                #if not HeightMap[fx][fz][0] <= 250:
                                    #frame[i][vres-j-1] = Map[fx][fz]
                            #else:
                                #frame[i][vres-j-1] = Map[fx][fz]
                        #else:
                        frame[i][int(vres-j-1)] = Map[fx][fz]#*s#[Map[fx][fz][0]*s, Map[fx][fz][1]*s, Map[fx][fz][2]*s]
                    
                elif Floor != None:
                    # get the image resolution
                    imgresx = len(Floor)
                    imgresy = len(Floor)
                    
                    # calculating floor pixel
                    fx = int(x/MapScale%1*(imgresx-1))
                    fz = int(z/MapScale%1*(imgresy-1))
                    
                    frame[i][vres-j-1] = Floor[fx][fz]
                else:
                    # if no applied floor then apply a blank texture
                    if int(x)%2 == int(z)%2:
                        frame[i][vres-j-1] = [0, 0, 0]
                    else:
                        frame[i][vres-j-1] = [255, 0, 255]
            
            # raycasting method
            if HeightMap != None:
                # get the image resolution
                imgresx = len(HeightMap)
                imgresy = len(HeightMap[0])
                
                r = []
                wx, wz = posx, posz#/comp
                count = 0
                amt = 0.01
                for b in range(30):
                    #  cast a ray until it either goes out of map or touches a wall
                    while count < RenderDistance and not (int(wx*wcomp) < imgresx and int(wx*wcomp) >= 0 and int(wz*wcomp) < imgresy and int(wz*wcomp) >= 0 and HeightMap[int(wx*wcomp)][int(wz*wcomp)][0] <= 250):
                        wx, wz = wx + amt*cos, wz + amt*sin
                        count += 1

                        # when far enough away the ray will become less accurate
                        # an attempt to optimize without sacrificing render distance
                        if count == 1000:
                            amt = 0.05
                        elif count == 1300:
                            amt = 0.1

                    skip = True

                    if int(wx*wcomp) < imgresx and int(wx*wcomp) >= 0 and int(wz*wcomp) < imgresy and int(wz*wcomp) >= 0 and HeightMap[int(wx*wcomp)][int(wz*wcomp)][0] <= 250:
                        # ray hit a wall
                        n = (abs((wx - posx)/cos))#/4)*WallHeights[wall_id]
                        wall_id = HeightMap[int(wx*wcomp)][int(wz*wcomp)][0]
                        #Height = int((((vres/2)/(n*correction + 0.000001))/2))#8)*WallHeights[wall_id])
                        if WallHeights[wall_id][0] > 0:
                            Height = int((((vres/2)/(n*correction + 0.000001))/8)*WallHeights[wall_id][0]) # multiply by wall height
                            Offset = int((((vres/2)/(n*correction + 0.000001))/4)*(4-WallHeights[wall_id][0])) - (((vres/2)/(n*correction + 0.000001))/2)*posy
                            Wy = int((((vres/2)/(n*correction + 0.000001))/8)*WallHeights[wall_id][1])
                            Wx = wx*wcomp
                            Wz = wz*wcomp
                            if WallHeights[wall_id][0] == 0:
                                skip = False
                            r.append((Height, wall_id, Offset, Wy, Wx, Wz, amt))
                        """
                        mag = (4-WallHeights[wall_id])
                        if WallHeights[wall_id] == 4:
                            mag = 1
                        """
                        #if Height < vres:
                            #for k in range(Height):
                                #if (vres/2) + Height + k >= 0 and (vres/2) + Height + k < vres: # make sure that it is on screen
                                    #frame[i][int((vres/2)) + Height + k] = WallColors[wall_id]
                        if skip:
                            wx, wz = wx + 0.25*cos, wz + 0.25*sin
                    else:
                        break

                # loop through the temporary array of walls in reverse
                for ind in range(len(r)-1, -1, -1):
                    Height = r[ind][0]
                    wall_id = r[ind][1]
                    Offset = r[ind][2]
                    Wy = r[ind][3]
                    Wx, Wz = r[ind][4], r[ind][5]
                    amt = r[ind][6]

                    # calculating the coordinates for the texture
                    """
                    hasTexture = False
                    xx = 0
                    x = 0
                    yy = 0
                    Wall = None
                    if WallTextures != None:
                        for w in range(len(WallTextures)):
                            if WallTextures[w][0] == wall_id:
                                hasTexture = True
                                Wall = WallTextures[w][1]
                                xx = int(x*3%1*6)
                                if x%1 < 0.02 or x%1 > 0.98:
                                    xx = int(z*0.8%1*6)
                                xx = numpy.linspace(0, 1, 8)*7%7
                                yy = numpy.linspace(0, 1, Height)*7%7
                                x = int(xx[int(((Wx*34)+2)%7)])
                                break
                    """
                    shade = False#1
                    offs = 5.0
                    if amt == 0.01:
                        offs = 0.5
                    elif amt == 0.05:
                        offs = 2.5
                    if HeightMap[int(Wx-offs)][int(Wz-offs)][0] <= 250:
                        shade = True#*= 0.45
                    if Height < vres:
                            for k in range(Height):
                                if (vres/2) + Height + Offset+1 - Wy + k >= 0 and (vres/2) + Height + Offset+1 - Wy + k < vres: # make sure that it is on screen
                                    #if hasTexture:
                                        #frame[i][int((vres/2) + Height + Offset - Wy + k)] = Wall[x][int(yy[int(k)])]
                                    #if WallColors[wall_id][0] == 232 and WallColors[wall_id][1] == 232:
                                        #frame[i][int((vres/2) + Height + Offset - Wy + k)] = WallTexture[int(xx[int(((Wx*34)+2)%8)])][int(yy[k])]#WallColors[wall_id]
                                    #else:
                                    #else:
                                        # apply the shadow color if not texture
                                    if shade and HasShadows:
                                        frame[i][int((vres/2) + Height + Offset+1 - Wy + k)] = WallShadows[wall_id]#WallColors[wall_id+100]
                                    else:
                                        frame[i][int((vres/2) + Height + Offset+1 - Wy + k)] = WallColors[wall_id]#*shade

                # draw the top of the walls
                for j in range(vres/2-1, -1, -1):
                    """
                    h = ((vres/2) - j)
                    bh = 0
                    if posy != 0:
                        bh = (((vres/2) - j)/posy)
                    """
                    # offsets for the wall top specifically
                    #nw = (((vres/2)-yoffset*2.25)/((vres/2)-j+h+0.00001))/correction#+Height*2))/correction
                    nw = (((vres/2)-(yoffset+(WallHeights[0][0]*30)))/((vres/2)-j+0.00001))/correction
                    xw = posx + cos*nw
                    zw = posz + sin*nw
                    
                    # calculating wall pixel
                    fx = int(xw/MapScale*(imgresx-1))
                    fz = int(zw/MapScale*(imgresy-1))
                    
                    # if the map contains ice blocks
                    if WallHeights[69][0] != 4:
                        nv = (((vres/2)-(yoffset+(WallHeights[69][0]*30)))/((vres/2)-j+0.00001))/correction
                        xv = posx + cos*nv
                        zv = posz + sin*nv

                        # calculating wall pixel
                        fxv = int(xv/MapScale*(imgresx-1))
                        fzv = int(zv/MapScale*(imgresy-1))

                        # check the heights of the ice blocks first
                        if fxv < len(HeightMap) and fxv >= 0 and fzv < len(HeightMap) and fzv >= 0 and HeightMap[fxv][fzv][0] == 69:
                            if WallHeights[69][0] > 0 and WallHeights[69][0] < 9 and nv > 0:
                                #Offset = ((((vres/2) - j)/2)*((4-WallHeights[HeightMap[fx][fz][0]][0])/3.5))
                                b = int(vres-j-1)#-Height + Offset)
                                if b >= 0 and b < vres:
                                    frame[i][b] = Map[fx][fz]#WallColors[HeightMap[fx][fz][0]]
                                    
                        # next check the heights of the walls
                        elif fx < len(HeightMap) and fx >= 0 and fz < len(HeightMap) and fz >= 0 and HeightMap[fx][fz][0] <= 250 and HeightMap[fx][fz][0] != 69:
                            if WallHeights[HeightMap[fx][fz][0]][0] > 0 and WallHeights[HeightMap[fx][fz][0]][0] < 9 and nw > 0:
                                #Offset = ((((vres/2) - j)/2)*((4-WallHeights[HeightMap[fx][fz][0]][0])/3.5))
                                b = int(vres-j-1)#-Height + Offset)
                                if b >= 0 and b < vres:
                                    frame[i][b] = Map[fx][fz]#WallColors[HeightMap[fx][fz][0]]
                    else:
                        if fx < len(HeightMap) and fx >= 0 and fz < len(HeightMap) and fz >= 0 and HeightMap[fx][fz][0] <= 250:
                            if WallHeights[HeightMap[fx][fz][0]][0] > 0 and WallHeights[HeightMap[fx][fz][0]][0] < 9 and nw > 0:
                                #Offset = ((((vres/2) - j)/2)*((4-WallHeights[HeightMap[fx][fz][0]][0])/3.5))
                                b = int(vres-j-1)#-Height + Offset)
                                if b >= 0 and b < vres:
                                    frame[i][b] = Map[fx][fz]#WallColors[HeightMap[fx][fz][0]]
                    """
                    if fx < len(HeightMap) and fx >= 0 and fz < len(HeightMap) and fz >= 0 and HeightMap[fx][fz][0] <= 250:
                        if WallHeights[HeightMap[fx][fz][0]][0] > 0 and WallHeights[HeightMap[fx][fz][0]][0] < 9 and nw > 0:
                            Height = 1
                            if WallHeights[HeightMap[fx][fz][0]][1] == 0:
                                Height = (((vres/2) - j)/2)
                            else:
                                Height = (((vres/2) - j)/2)*WallHeights[HeightMap[fx][fz][0]][1]
                            Offset = ((((vres/2) - j)/2)*((4-WallHeights[HeightMap[fx][fz][0]][0])/3.5))
                            b = int(vres-j-Height + h/2 + Offset)
                            if b >= 0 and b < vres:
                                frame[i][b] = Map[fx][fz]#WallColors[HeightMap[fx][fz][0]]
                    """
            

    return frame

# manage and sort the list of sprites

@njit(fastmath=True)
def sort_sprites(sprites, posX, posZ, rot, comp, HeightMap):
    # table of sprites:     sprite id,  size,   positionx,   direction,  enabled,    angle,  distance,  positionz,  dir2p,  amt of sprites, posy,   priority
    # indexes:                       0           1            2                3              4             5             6             7              8                9             10            11
    # using: 2, 3, 4, 5, 6, 7, 8, 9
    #sp = sprites.copy()

    posx = posX#*(34.1/comp)#/comp
    posz = posZ#*(34.1/comp)#/comp

    for s in sprites:
            if s[4] == True:
                cos, sin = numpy.cos(s[3]), numpy.sin(s[3])
                sx, sz = s[2]*(34.1/comp), s[7]*(34.1/comp)
                # calculate the angle to make sure it is within the player's vision
                angle = numpy.arctan((sz-posz)/(sx-posx+0.00001))
                if abs(posx + numpy.cos(angle) - sx) > abs(posx - sx):
                    angle = (angle - numpy.pi)%(2 * numpy.pi)

                diff = (rot-angle)%(2*numpy.pi)
                #b = True
                if diff > 10*numpy.pi/6 or diff < numpy.pi/6:
                    dir2p = ((((s[3] - angle)%(2*numpy.pi))/numpy.pi)*s[9])
                    s[8] = dir2p
                    d = numpy.sqrt((posx - sx)**2 + (posz - sz)**2) # distance from camera
                    # calculate if there is a wall in front of them
                    """
                    if HeightMap != None:
                        x, z = s[2]*34.1, s[7]*34.1
                        cos, sin = (posx*34.1 - x)*(1/d), (posz*34.1 - z)*(1/d)#/(1/d)
                        for i in range(int(d/0.05)):
                            x, z = x + 0.05*cos, z + 0.05*sin
                            if (int(x) >= 0 and int(x) < len(HeightMap) and int(z) >= 0 and int(z) < len(HeightMap[0]) and HeightMap[int(x)][int(z)][0] <= 250):
                                #and ((int(x-0.02*cos) >= 0 and int(x-0.02*cos) < len(HeightMap) and HeightMap[int(x-0.02*cos)][int(z)][0] <= 250)
                                #or (int(z-0.02*sin) >= 0 and int(z-0.02*sin) < len(HeightMap) and HeightMap[int(x)][int(z-0.02*sin)][0] <= 250))):
                                s[6] = 9999
                                break
                    """
                    s[5] = diff
                    #if d < 19:
                    s[6] = d#1/d
                    #else:
                        #s[6] = 9999
                else:
                    s[6] = 9999

    #sprites = sprites.sort(key=lambda x: x[6], reverse=True) # sort by distance
    sprites = sprites[sprites[:, 6].argsort()]
    #sp[:, 6].argsort()

    # check and add a sprite limit
    # if it has priority then it is not counted toward the limit
    amt = 0
    for s in sprites:
        if s[4] == True:
            if s[6] < 15:
                if s[11] == True:
                    s[6] = 1/s[6]
                elif amt <= 20:
                    s[6] = 1/s[6]
                    amt += 1
                else:
                    break
            else:
                break

    # sort the sprites again
    sprites = sprites[sprites[:, 6].argsort()]
    
    return sprites


# sprite class
class Sprite:
    # create a new sprite
    def __init__(self, images, size = 1, position = (0, 0, 0), permanence = False, direction = 0, priority=False):
        self.Sprites = images
        self.Size = size
        self.Position = Vector3(position[0]/34, position[1]*100, position[2]/34)#Vector3(position[0]/34, position[1]*100, position[2]/34)
        self.Direction = numpy.deg2rad(direction)
        self.Enabled = True
        self.Active = True
        self.Shadows = True
        self.Priority = priority
        self.Permanent = permanence
        self.SpriteID = 0

        # variables just for calculating order
        self.Angle = 0
        self.Distance = 0
        self.dir2p = 0

    # change the position of the sprite
    def set_position(self, position=(0, 0, 0)):
        self.Position.x = position[0]/34
        self.Position.y = position[1]*100
        self.Position.z = position[2]/34

    # change the rotation of the sprite
    def set_rotation(self, rotation = 0):
        self.Direction = numpy.deg2rad(rotation)

# particle subclass
class Particle(Sprite):
    # create a new particle
    def __init__(self, image, size = 1, position = (0, 0, 0), lifetime = 1):
        super().__init__(image, size, position, False)
        self.Lifetime = lifetime*60

    def increment_timer(self):
        self.Lifetime -= 1
        if self.Lifetime == 0:
            self.Enabled = False
            return True
        return False

# camera class
class Camera:
    # create the engine
    def __init__(self, Resolution = 2.0, Window = (800, 600), BaseCFrame = (0.0, 0.0, 0.0, 0.0), DefaultCollision=False):
        self.Width, self.Height = Window # set the window size

        self.WIN = pygame.display.set_mode((self.Width, self.Height))

        # set the rendering properties
        if Resolution < 0.3:
            Resolution = 1
        hres = int(120*Resolution) # horizontal resolution
        vres = int(200*Resolution) # vertical resolution

        self.Resolution = (hres, vres)

        self.GlobalCollision = DefaultCollision

        # set  the base position and rotation (in radians)
        x, y, z, rot = BaseCFrame
        self.CFrame = CFrame(x, float(y), z, numpy.deg2rad(rot+0.005))

        self.Sky_Size = 1
        self.MapScale = 30

        # create a default array for colors being stored
        self.WallColors = numpy.array([(255, 0, 255) for i in range(251)])
        self.WallShadows = numpy.array([(255, 0, 255) for i in range(251)])

        # create a default array for wall heights
        self.WallHeights = numpy.array([(4, 0) for i in range(251)])

        # create the wall collisions
        self.WallCollisions = numpy.array([DefaultCollision for i in range(251)])

        # create the array for wall attributes
        #self.WallAttributes = numpy.array([()])

        # create an empty array of sprites
        self.Sprites = []#numpy.array([[9999, 0, 0, 0, False, 0.0, 0, 0, 0, 1, 0, 0]])
        self.SpriteImg = []

        # create an empty list of particles in memory
        # particle limit is what is entered as i
        self.Particles = numpy.array([[0, 0, 0, 0, False, 0.0, 0, 0, 0, 1, 0, False, 0] for i in range(50)])
        #self.PImg = get_image("Assets/Sprites/DriftParticle.png")

        self.Frame = numpy.random.uniform(0, 0, (hres, vres, 3)) # generate the frame

        self.Compensation = 1
        self.HasShadows = True

        #self.move_parallel(0.1) # lazy way to fix initial lag spike when moving


    ## Sprite Application ##

    # add a sprite
    def add_sprite(self, sprite):
        SpriteID = len(self.Sprites)
        sprite.SpriteID = SpriteID

        c = (34.1/self.Compensation)

        # idk what I am doing here but this was the only thing that worked
        if len(self.Sprites) == 0:
            self.Sprites.append([SpriteID, sprite.Size, sprite.Position.x*c, sprite.Direction, sprite.Enabled, sprite.Angle, sprite.Distance, sprite.Position.z*c, 0, len(sprite.Sprites), 0, sprite.Priority, 0])
            numpy.array(self.Sprites)
        else:
            self.Sprites = numpy.append(self.Sprites, [[SpriteID, sprite.Size, sprite.Position.x*c, sprite.Direction, sprite.Enabled, sprite.Angle, sprite.Distance, sprite.Position.z*c, 0, len(sprite.Sprites), 0, sprite.Priority, 0]], axis=0)
        self.SpriteImg.append(sprite)
        #self.Sprites.append(sprite)

    # convert a spritesheet
    def get_sprites(self, sprite_path, length, x, y):
        sheet = pygame.image.load(sprite_path).convert_alpha()
        sprites = []
        for i in range(length):
            xx = i*x
            #for j in range(y):
                #yy = j*32
            sprites.append(sheet.subsurface(xx, 0, x, y))
        sprite = sprites[0]
        # scale the sprite to the render resolution
        spsize = numpy.asarray(sprite.get_size())*self.Resolution[0]/800

        return sprites, spsize

    # update a sprite attribute
    """
    def update_sprite(self, sprite, attr, param):
        setattr(sprite, attr, param)
        sp_id = sprite.SpriteID
    """

    # creating particle effects
    def create_particle(self, size, pos, lifetime, img_id=0):
        # table of sprites:     image,  size,   positionx,   direction,  enabled,    angle,  distance,  positionz,  dir2p,  sprite amt,  positiony, priority,  lifetime
        # indexes:                     0         1            2                3              4             5             6             7              8            9                10           11             12
        # create the particle
        #self.Particles.append([image, size, pos[0], 0, True, 0, 0, pos[2], 0, pos[1], lifetime])
        for p in self.Particles:
            if p[4] == False:
                p[0] = img_id
                p[1] = size
                p[2] = pos[0]#*(34.1/self.Compensation)
                p[4] = True
                p[7] = pos[2]#*(34.1/self.Compensation)
                p[10] = pos[1]
                p[12] = lifetime
                break

    # incrementing the lifetime of a particle effect
    def increment_particles(self):
        for pi in range(len(self.Particles)):
            if self.Particles[pi][4] == True:
                self.Particles[pi][12] -= 1
                if self.Particles[pi][12] <= 0:
                    self.Particles[pi][4] = False


    # trash collection function
    # clears inactive sprites in order to speed up the program
    def trash_collection(self):
        to_keep = []
        off = 0
        for sprite in self.Sprites:
            sp_id = sprite[0]
            # check if it has permanence and if it is inactive
            if not (self.SpriteImg[sp_id].Permanent == False and self.SpriteImg[sp_id].Enabled == False):
                to_keep.append(sprite)


    ## Texture Application ##

    # apply a sky texture
    def set_sky(self, image, size=1):
        self.Sky = pygame.surfarray.array3d(pygame.transform.scale(image, (360, self.Resolution[1]*size)))

    # apply a floor texture
    def set_floor(self, texture, scale=30):
        self.Floor = texture
        self.MapScale = scale

    # apply a map texture
    # same as floor except it does not repeat
    def set_map(self, texture, scale=30):
        self.Map = texture
        self.MapScale = scale
        self.Compensation = (len(texture)-1)/scale

    # apply a height map
    def set_height_map(self, height_map):
        self.HeightMap = height_map

    # load wall textures
    def load_textures(self, textures):
        #cID = 300
        WT = []
        # loop through the dictionary of textures
        for wall_id, path in textures.items():
            # load the image
            img = pygame.image.load(path)
            surf = pygame.surfarray.array3d(img)
            WT.append([wall_id, surf])
        self.WallTextures = numpy.array(WT)


    ## Walls ##
    
    # store a wall (height map item) color
    def set_wall_color(self, wall_id, r=0, g=0, b=0):
        self.WallColors[wall_id] = (r, g, b)

    # store a table of wall colors
    def set_wall_colors(self, color_table):
        for wall_id, color in color_table.items():
            self.WallColors[wall_id] = color
            if wall_id <= 150:
                self.prepare_shadow(wall_id, color) # precalculates the shadow color

    # set the height of a wall
    # wall id is the R value of the RGB of the wall in the height map
    def set_wall_height(self, wall_id, height=2, y=0):
        if wall_id <= 250:
            self.WallHeights[wall_id] = (height, y)

    # set multiple wall heights
    def set_wall_heights(self, wall_table):
        for wall_id, properties in wall_table.items():
            self.set_wall_height(wall_id, properties[0], properties[1])

    # set the collision of a wall
    def set_wall_collision(self, wall_id, collision=True):
        if wall_id <= 250:
            self.WallCollisions[wall_id] = collision

    # set a table of wall collisions
    def set_wall_collisions(self, wall_table):
        for wall_id, collision in wall_table.items():
            self.set_wall_collision(wall_id, collision)

    # prepare the wall shadow colors
    def prepare_shadow(self, wall_id, color):
        shade = 0.55
        #self.WallColors[wall_id + 100] = (color[0]*0.45, color[1]*0.45, color[2]*0.45)
        self.WallShadows[wall_id] = (color[0]*shade, color[1]*shade, color[2]*shade)


    ## Motion ##
    # t is a variable to make speed independent from frame rate

    def set_position(self, position=(0, 0, 0)):
        self.CFrame.Position = Vector3(float(position[0]), float(position[1]), float(position[2]))

    def set_offset(self, x=0, y=0, z=0, rot=0, offsetx=0, offsety=0, offsetz=0):
        cos, sin = numpy.cos(rot), numpy.sin(rot)
        comp = 34.1/self.Compensation
        self.set_position((x*comp + offsetx*cos, y/15 + offsety, z*comp + offsetz*sin))

    def set_rotation(self, rotation=(0.0, 0.0)):
        self.CFrame.Rotation = Vector2(numpy.deg2rad(rotation[0]), numpy.deg2rad(rotation[1]))

    def move_parallel(self, units=0.0, t=20):
        rot = self.CFrame.Rotation.x
        cX = self.CFrame.Position.x
        cZ = self.CFrame.Position.z
        nX = cX + numpy.cos(rot)*((units/100)*(t/10))
        nZ = cZ + numpy.sin(rot)*((units/100)*(t/10))
        
        if hasattr(self, "HeightMap") and self.GlobalCollision == True:
            hm = self.HeightMap
            wc = self.WallCollisions
            # convert it to the coordinates read by heightmap array
            ccX = cX/30*(len(hm)-1)
            cnX = nX/30*(len(hm)-1)
            ccZ = cZ/30*(len(hm[0])-1)
            cnZ = nZ/30*(len(hm[0])-1)
            offs = 1
            #print(ccZ, cnZ, cnZ + offs, hm[int(cnX)][int(cnZ + offs)][0], hm[int(cnX)][int(cnZ - offs)][0])
            if (int(cnX) >= 0 and int(cnX) < len(hm) and int(cnX - offs) >= 0 and int(cnX + offs) < len(hm)
                    and cnZ >= 0 and int(cnZ) < len(hm[0]) and int(cnZ - offs) >= 0 and int(cnZ + offs) < len(hm[0])):
                # check collision conditions
                if not(has_collision(hm, cnX-offs, cnZ, wc) or has_collision(hm, cnX+offs, cnZ, wc)
                       or has_collision(hm, cnX, cnZ-offs, wc) or has_collision(hm, cnX, cnZ+offs, wc)):
                    self.CFrame.Position.x = nX
                    self.CFrame.Position.z = nZ
                elif not (has_collision(hm, ccX-offs, cnZ, wc) or has_collision(hm, ccX+0.2, cnZ, wc)
                       or has_collision(hm, ccX, cnZ-offs, wc) or has_collision(hm, ccX, cnZ+0.2, wc)):
                    self.CFrame.Position.z = nZ
                elif not(has_collision(hm, cnX-offs, ccZ, wc) or has_collision(hm, cnX+offs, ccZ, wc)
                       or has_collision(hm, cnX, ccZ-offs, wc) or has_collision(hm, cnX, ccZ+offs, wc)):
                    self.CFrame.Position.x = nX

                    
            else:
                self.CFrame.Position.x = nX
                self.CFrame.Position.z = nZ
        else:
            self.CFrame.Position.x = nX
            self.CFrame.Position.z = nZ

    def move_perpendicular(self, units=0.0, t=20):
        rot = self.CFrame.Rotation
        self.CFrame.Position.x = self.CFrame.Position.x - numpy.sin(rot)*(units/100)*(t/10)
        self.CFrame.Position.z = self.CFrame.Position.z + numpy.cos(rot)*(units/100)*(t/10)

    # move forward relative to the rotation
    def forward(self, units=0.0, t=20):
        self.move_parallel(units, t)

    # move backward relative to the rotation
    def backward(self, units=0.0, t=20):
        self.move_parallel(-units, t)

    # move left relative to the rotation
    def move_left(self, units=0.0, t=20):
        self.move_perpendicular(-units, t)

    # move right relative to the rotation
    def move_right(self, units=0.0, t=20):
        self.move_perpendicular(units, t)


    ## Rotation ##

    def turn_x(self, units=0.0, t=20):
        self.CFrame.Rotation.x = (self.CFrame.Rotation.x + (units/100)*(t/10))#%360

    def turn_y(self, units=0.0, t=20):
        self.CFrame.Rotation.y = (self.CFrame.Rotation.y + (units/100)*(t/10))#%360

    # turn left
    def turn_left(self, units=0.0, t=20):
        self.turn_x(-units, t)

    # turn right
    def turn_right(self, units=0.0, t=20):
        self.turn_x(units, t)

    # turn down
    def turn_down(self, units=0.0, t=20):
        self.turn_y(-units, t)

    # turn up
    def turn_up(self, units=0.0, t=20):
        self.turn_y(units, t)


    ## Drawing ##

    # get the camera frame
    def get_frame(self):
        comp = self.Compensation
        return create_frame(self.Frame, self.Resolution,
                                  self.CFrame.Position.x/comp, -self.CFrame.Position.y/10, self.CFrame.Position.z/comp, self.CFrame.Rotation.x, self.CFrame.Rotation.y, self.HasShadows,
                                  getattr(self, "WallHeights", None), getattr(self, "WallColors", None), getattr(self, "WallShadows", None),# getattr(self, "WallTexture", None),
                                  getattr(self, "Sky", None),
                                  getattr(self, "Floor", None), getattr(self, "Map", None), self.MapScale, getattr(self, "HeightMap", None),
                                  getattr(self, "WallTextures", None))

    # get the camera surface

    # preload the camera
    def preload(self):
        # call the frame function so numba compiles it
        # does not apply it to the window
        self.get_frame()
        self.Sprites = sort_sprites(numpy.array(self.Sprites), self.CFrame.Position.x, self.CFrame.Position.z, self.CFrame.Rotation.x, 1, getattr(self, "HeightMap", None))

    # draw the window
    def draw(self):
        # redraw the frame
        self.Frame = self.get_frame()

        # make the surface and scale it to the window
        surface = pygame.surfarray.make_surface(self.Frame)
        surface = pygame.transform.scale(surface, (self.Width, self.Height))

        ## Sprites ##
        pos, rot = self.CFrame.Position, self.CFrame.Rotation

        comp = self.Compensation

        # loop through each sprite
        # later attempt to speed this process up with numba
        """
        for sprite in self.Sprites:
            if sprite.Enabled == True:
                # calculate the angle to make sure it is within the player's vision
                angle = numpy.arctan((sprite.Position.z-pos.z)/(sprite.Position.x-pos.x))
                if abs(pos.x + numpy.cos(angle) - sprite.Position.x) > abs(pos.x - sprite.Position.x):
                    angle = (angle - numpy.pi)%(2 * numpy.pi)

                diff = (rot-angle)%(2*numpy.pi)
                if diff > 10.5*numpy.pi/6 or diff < 1.5*numpy.pi/6:
                    dir2p = ((((sprite.Direction - angle)%(2*numpy.pi))/numpy.pi)*12)# - 3*numpy.pi/4)%(2*numpy.pi))*3)-1#/(numpy.pi/2)
                    sprite.dir2p = dir2p
                    d = numpy.sqrt((pos.x - sprite.Position.x)**2 + (pos.z - sprite.Position.z)**2) # distance from camera
                        # calculate if there is a wall in front of them
                    
                        if hasattr(self, "HeightMap"):
                            x, z = pos.x, pos.z
                            cos, sin = 0.01*(x - sprite.Position.x)/d, 0.01*(z - sprite.Position.z)/d
                            for i in range(int(d/0.01)):
                                x, z = x + cos, z + sin
                                if x >= 0 and x < len(self.HeightMap) and z >= 0 and z < len(self.HeightMap[0]) and self.HeightMap[int(x)][int(z)][0] <= 250:
                                    d = 9999
                    
                    sprite.Angle = diff
                    sprite.Distance = 1/d
                else:
                    sprite.Distance = 9999
        
        self.Sprites.sort(key=lambda x: x.Distance, reverse=True) # sort by distance
        """
        # first reset sprite pos
        for s in self.Sprites:
            sp_id = int(s[0])
            if sp_id < len(self.SpriteImg):
                s[2] = self.SpriteImg[sp_id].Position.x#*(34.1/self.Compensation)
                s[3] = self.SpriteImg[sp_id].Direction
                s[7] = self.SpriteImg[sp_id].Position.z#*(34.1/self.Compensation)
                s[4] = self.SpriteImg[sp_id].Enabled
        self.Sprites = sort_sprites(numpy.array(self.Sprites), self.CFrame.Position.x, self.CFrame.Position.z, self.CFrame.Rotation.x, comp, getattr(self, "HeightMap", None))
        for sprite in self.Sprites:
            sp_id = int(sprite[0])
            if sprite[6] > 10: # if it is within render distance
                break
            elif sprite[4] == False: # if it is not enabled
                continue
            types = sprite[9]
            dir2p = int(numpy.floor(sprite[8]))
            correction = numpy.cos(sprite[6]) # corrects fish eye effect again
            mn = min(sprite[6], 2)
            if mn >= 2: # if too small
                continue
            scaling = mn/correction
            size = numpy.asarray(self.SpriteImg[sp_id].Sprites[0].get_size())*sprite[1]
            # calculate coordinates on screen
            x = self.Width/2 - (self.Width)*numpy.sin(sprite[5]) - scaling*size[0]/2
            y = self.Height/2 + (self.Height/2)*scaling - scaling*size[1]/2 + ((self.Height/4)*self.CFrame.Position.y/10)*scaling - ((self.SpriteImg[sp_id].Position.y)*scaling)# - (-self.CFrame.Position.y*20)*scaling#self.Height/25)*scaling

            # x and y position for the shadow
            sx = self.Width/2 - (self.Width)*numpy.sin(sprite[5]) - scaling*(size[0]*1.05)/2
            sy = self.Height/2 + (self.Height/2)*scaling - (50*scaling) + ((self.Height/4)*self.CFrame.Position.y/10)*scaling#- (-self.CFrame.Position.y*20)*scaling

            # calculating the opacity of the shadow
            h = (self.SpriteImg[sp_id].Position.y/100)
            op = 1
            if h > 0:
                op = 1/h
            if x > 0 and y > 0:
                # decide whether it is a "3D" sprite or not
                if types > 1:
                    if dir2p <= sprite[9]-1 or dir2p == sprite[9]*2:
                        d = 0
                        if dir2p == sprite[9]*2:
                            d = 0
                        else:
                            d = dir2p
                        s = pygame.transform.scale(self.SpriteImg[sp_id].Sprites[d].copy(), abs(scaling*size))
                    else:
                        s = pygame.transform.scale(pygame.transform.flip(self.SpriteImg[sp_id].Sprites[int(sprite[9]*2)-1-dir2p].copy(), True, False), abs(scaling*size))
                else:
                    s = pygame.transform.scale(self.SpriteImg[sp_id].Sprites[0].copy(), abs(scaling*size))

                # create the shadow sprite
                if sprite[6] > 0.1 and self.SpriteImg[sp_id].Shadows:
                    simg = ShadowImg.copy()
                    simg.set_alpha(op*200)
                    shadow = pygame.transform.scale(simg, (abs(scaling*size[0]*1.05), abs(scaling*(size[0]/2.25))))
                    surface.blit(shadow, (sx, sy))
                surface.blit(s, (x, y))


        self.Particles = sort_sprites(self.Particles, self.CFrame.Position.x, self.CFrame.Position.z, self.CFrame.Rotation.x, comp, getattr(self, "HeightMap", None))
        for p in self.Particles:
            if p[6] > SpriteDistance: # if it is within render distance
                break
            elif p[4] == False: # if it is not enabled
                continue
            dir2p = int(numpy.floor(p[8]))
            correction = numpy.cos(p[6]) # corrects fish eye effect again
            mn = min(p[6], 2)
            if mn == 2: # if too small
                continue
            scaling = mn/correction
            size = numpy.asarray(self.PImg[int(p[0])].get_size())*p[1]
            # calculate coordinates on screen
            x = self.Width/2 - (self.Width)*numpy.sin(p[5]) - scaling*size[0]/2
            y = self.Height/2 + (self.Height/2)*scaling - scaling*size[1]/2 - ((p[10])*scaling) + ((self.Height/4)*self.CFrame.Position.y/10)*scaling#- (-self.CFrame.Position.y*20)*scaling
            if x > 0 and y > 0:
                #s = pygame.transform.scale(p[0], abs(scaling*size))
                s = pygame.transform.scale(self.PImg[int(p[0])].copy(), abs(scaling*size))
                surface.blit(s, (x, y))
        """
        for sprite in self.Sprites:
            if sprite.Distance > SpriteDistance: # if it is within render distance
                break
            types, dir2p = len(sprite.Sprites), int(numpy.floor(sprite.dir2p))
            correction = numpy.cos(sprite[6]) # corrects fish eye effect again
            mn = min(sprite.Distance, 2)
            if mn == 2: # if too small
                break
            scaling = mn/correction
            size = numpy.asarray(self.SpriteImg[sp_id][0].get_size())*sprite[1]
            # calculate coordinates on screen
            x = self.Width/2 - (self.Width)*numpy.sin(sprite[5]) - scaling*size[0]/2
            y = self.Height/2 + (self.Height/2)*scaling - scaling*size[1]/2 - (sprite[2][1])*scaling
            if x > 0 and y > 0:
                if types > 1:
                    if dir2p <= 11:
                        s = pygame.transform.scale(sprite.SpriteImg[sp_id].Sprites[dir2p], abs(scaling*size))
                    else:
                        s = pygame.transform.scale(pygame.transform.flip(sprite.SpriteImg[sp_id].Sprites[23-dir2p], True, False), abs(scaling*size))
                else:
                    s = pygame.transform.scale(sprite.SpriteImg[sp_id].Sprites[0], abs(scaling*size))
                surface.blit(s, (x, y))
        """
        self.WIN.blit(surface, (0, 0))

        #pygame.display.update() # refresh the display

## Image Management ##
    
# get image from file path/name
def get_image(path):
    return pygame.image.load(path)
    
# parse an image into an array
def parse_texture(image):
    return pygame.surfarray.array3d(image)

# parse a skybox into an array (DEPRICATED)
"""
def parse_skybox(image):
    return pygame.surfarray.array3d(pygame.transform.scale(image, (360, 250)))
"""
