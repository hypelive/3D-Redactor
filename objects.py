from geometry import Vector3


class Point:
    WIDTH = 10
    RESIZABLE = False

    def __init__(self, x: float, y: float, z: float):
        self.x = x
        self.y = y
        self.z = z

    def __add__(self, other):
        if isinstance(other, Vector3):
            self.x += other.x
            self.y += other.y
            self.z += other.z

    def to_vector3(self):
        return Vector3(self.x, self.y, self.z)

    def to_string(self):
        return f'pt,{float(self.x)},{float(self.y)},{float(self.z)}'

    @staticmethod
    def from_string(str_representation):
        params = str_representation.split(',')
        return Point(float(params[1]), float(params[2]),
                     float(params[3]))


class Line:
    WIDTH = 5
    RESIZABLE = False

    def __init__(self, start: Point, end: Point):
        self.start = start
        self.end = end

    def to_string(self):
        return f'ln!|{self.start.to_string()}||{self.end.to_string()}|'

    @staticmethod
    def from_string(str_representation: str, objects):
        str_points = str_representation.split('|')
        points = []
        for obj in objects:
            if (obj.to_string() == str_points[1] or
                    obj.to_string() == str_points[3]):
                points.append(obj)
        return Line(points[0], points[1])


class Polygon:
    WIDTH = 5
    RESIZABLE = False

    def __init__(self, points):
        self.points = [point for point in points]

    def to_string(self):
        str_representation = 'pg!'
        for point in self.points:
            str_representation += f'|{point.to_string()}|'
        return str_representation

    @staticmethod
    def from_string(str_representation, objects):
        str_points = str_representation.split('|')
        points = []
        for obj in objects:
            fl = False
            for i in range(1, len(str_points), 2):
                if obj.to_string() == str_points[i]:
                    fl = True
            if fl:
                points.append(obj)
        return Polygon(points)


class Sphere:
    RESIZABLE = True

    def __init__(self, point: Point, radius=20.0):
        self.point = point
        self.radius = radius

    def __add__(self, other):
        if isinstance(other, Vector3):
            self.point + other

    def resize(self, value):
        self.radius += value

    def to_string(self):
        return f'sp!{self.point.to_string()}!{int(self.point.radius)}'

    @staticmethod
    def from_string(str_representation, objects):
        params = str_representation.split('!')
        for obj in objects:
            if obj.to_string() == params[1]:
                return Sphere(obj, float(params[2]))


class Cylinder:
    RESIZABLE = False

    def __init__(self, line: Line, radius=20.0):
        self.line = line
        self.radius = radius

    def to_string(self):
        return f'ln!{self.line.to_string()}!{self.radius}'

    @staticmethod
    def from_string(str_representation: str, objects):
        params = str_representation.split('!')
        for obj in objects:
            if (obj.to_string() == params[1]):
                return Cylinder(obj, float(params[2]))
