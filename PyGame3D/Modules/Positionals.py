# A bunch of classes that have to do with positionals

# Vector2 Instance
# holds 2 values: x and y

class Vector2:
    def __init__(self, x = 0, y = 0):
        self.x = x
        self.y = y

    def __str__(self):
        return "("+str(self.x)+", "+str(self.z)+")"


# Vector3 Instance
# holds 3 values: x, y, and z

class Vector3:
    def __init__(self, x = 0, y = 0, z = 0):
        self.x = x
        self.y = y
        self.z = z

    def __str__(self):
        return "("+str(self.x)+", "+str(self.y)+", "+str(self.z)+")"


# Coordinate Frame (CFrame) Instance
# holds an x coordinate, y coordinate, z coordinate, and rotation

class CFrame:
    def __init__(self, x = 0, y = 0, z = 0, rotx = 0, roty = 0):
        self.Position = Vector3(x, y, z)
        self.Rotation = Vector2(rotx, roty)

    def __str__(self):
        return "("+str(self.Position)+", "+str(self.Rotation)+")"

    #def __init__(self, Position = Vector3.new(0, 0, 0), Rotation = 0):
        #self.Position = Position
        #self.Rotation = Rotation
