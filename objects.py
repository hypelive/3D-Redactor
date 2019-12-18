from geometry import Vector3
import json


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

    def __str__(self):
        return f'pt,{float(self.x)},{float(self.y)},{float(self.z)}'

    @staticmethod
    def from_string(str_representation, objects=None):
        params = str_representation.split(',')
        return Point(float(params[1]), float(params[2]),
                     float(params[3]))


class Line:
    WIDTH = 5
    RESIZABLE = False

    def __init__(self, start: Point, end: Point):
        self.start = start
        self.end = end

    def get_guide_vector(self):
        return Vector3(self.end.x - self.start.x,
                       self.end.y - self.start.y,
                       self.end.z - self.start.z)

    def is_inside_line(self, vector: Vector3) -> bool:
        if not vector:
            return False
        return abs(Vector3.distance(self.start.to_vector3(),
                                    self.end.to_vector3()) -
                   Vector3.distance(self.start.to_vector3(), vector) -
                   Vector3.distance(self.end.to_vector3(), vector)) < 1e-8

    def __add__(self, other):
        if isinstance(other, Vector3):
            self.start + other
            self.end + other

    def __str__(self):
        return f'ln!|{str(self.start)}||{str(self.end)}|'

    @staticmethod
    def from_string(str_representation: str, objects):
        str_points = str_representation.split('|')
        points = []
        for obj in objects:
            if (str(obj) == str_points[1] or
                    str(obj) == str_points[3]):
                points.append(obj)
        return Line(points[0], points[1])


class Polygon:
    WIDTH = 5
    RESIZABLE = False

    def __init__(self, points):
        self.points = [point for point in points]

    def get_normal_vector(self):
        return (Vector3(self.points[1].x - self.points[0].x,
                        self.points[1].y - self.points[0].y,
                        self.points[1].z - self.points[0].z) *
                Vector3(self.points[2].x - self.points[0].x,
                        self.points[2].y - self.points[0].y,
                        self.points[2].z - self.points[0].z))

    def get_surface(self):
        for i in range(1, len(self.points) + 1):
            yield Line(self.points[i - 1], self.points[i % len(self.points)])

    def __add__(self, other):
        if isinstance(other, Vector3):
            for point in self.points:
                point + other

    def __str__(self):
        str_representation = 'pg!'
        for point in self.points:
            str_representation += f'|{str(point)}|'
        return str_representation

    @staticmethod
    def from_string(str_representation, objects):
        str_points = str_representation.split('|')
        points = []
        for obj in objects:
            fl = False
            for i in range(1, len(str_points), 2):
                if str(obj) == str_points[i]:
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

    def __str__(self):
        return f'sp!{str(self.point)}!{int(self.point.WIDTH)}'

    @staticmethod
    def from_string(str_representation, objects):
        params = str_representation.split('!')
        for obj in objects:
            if str(obj) == params[1]:
                return Sphere(obj, float(params[2]))


class Cylinder:
    RESIZABLE = False

    def __init__(self, line: Line, radius=20.0):
        self.line = line
        self.radius = radius

    def __str__(self):
        return f'ln!{str(self.line)}!{self.radius}'

    @staticmethod
    def from_string(str_representation: str, objects):
        params = str_representation.split('!')
        for obj in objects:
            if (str(obj) == params[1]):
                return Cylinder(obj, float(params[2]))
