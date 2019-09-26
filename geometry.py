class Vector3():
    def __init__(self, x : float, y : float, z : float):
        self.x = x
        self.y = y
        self.z = z

class Vector2():
    def __init__(self, x : float, y : float):
        self.x = x
        self.y = y

class Point():
    def __init__(self, x : float, y : float, z : float, radius : float):
        self.x = x
        self.y = y
        self.z = z
        self.radius = radius

class Line():
    def __init__(self, start : Point, end : Point, radius : float):
        self.start = start
        self.end = end
        self.radius = radius

class Plate():
    def __init__(self, first_line : Line, second_line : Line, radius : float, normal : Vector3):
        self.first_line = first_line
        self.second_line = second_line
        self.radius = radius
        self.normal = normal