from .geometry import Vector3
from .serializable import Serializable
import json
from .color import Color
from .borderStyle import BorderStyle
from .surfaceStyle import SurfaceStyle


class Point(Serializable):
    WIDTH = 10
    RESIZABLE = False
    NAME = 'Point'

    def __init__(self, x: float, y: float, z: float,
                 color=Color.ORANGE_LIGHT):
        self.x = x
        self.y = y
        self.z = z
        self.color = color
        super().__init__(['x', 'y', 'z', 'color'])

    def __add__(self, other):
        if isinstance(other, Vector3):
            self.x += other.x
            self.y += other.y
            self.z += other.z

    def to_vector3(self):
        return Vector3(self.x, self.y, self.z)

    def __str__(self):
        return f'pt,{float(self.x)},{float(self.y)},{float(self.z)}'

    def extra_initialize(self, objects):
        self.color = Color(self.color)

    def set_style(self, drawer):
        self.color = drawer.point_color

    def almost_equal(self, point):
        return abs(self.x - point.x) < 1e-5 and\
            abs(self.y - point.y) < 1e-5 and\
            abs(self.z - point.z) < 1e-5

    @staticmethod
    def from_string(str_representation, objects=None):
        params = str_representation.split(',')
        return Point(float(params[1]), float(params[2]),
                     float(params[3]))

    @staticmethod
    def from_dict(obj_dict):
        point = Point(None, None, None)
        point.initialize(obj_dict)
        return point


class Line(Serializable):
    WIDTH = 5
    RESIZABLE = False
    NAME = 'Line'

    def __init__(self, start: Point, end: Point,
                 color=Color.ORANGE_LIGHT, style=BorderStyle.SOLID):
        self.start = start
        self.end = end
        self.color = color
        self.style = style
        super().__init__(['start', 'end', 'color', 'style'])

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

    def extra_initialize(self, objects):
        start = Point.from_dict(self.start)
        end = Point.from_dict(self.end)

        self.start = None
        self.end = None

        self.color = Color(self.color)
        self.style = BorderStyle(self.style)

        for obj in objects:
            if self.start and self.end:
                return
            if not self.start and str(start) == str(obj):
                self.start = obj
            if not self.end and str(end) == str(obj):
                self.end = obj

    def set_style(self, drawer):
        self.color = drawer.line_color
        self.style = drawer.line_style

    @staticmethod
    def from_string(str_representation: str, objects):
        str_points = str_representation.split('|')
        points = []
        for obj in objects:
            if (str(obj) == str_points[1] or
                    str(obj) == str_points[3]):
                points.append(obj)
        return Line(points[0], points[1])


class Polygon(Serializable):
    WIDTH = 5
    RESIZABLE = False
    NAME = 'Polygon'

    def __init__(self, points,
                 color=Color.ORANGE_DARK, style=SurfaceStyle.SOLID,
                 border_color=Color.ORANGE_LIGHT, border_style=BorderStyle.SOLID):
        if points:
            self.points = [point for point in points]
        self.color = color
        self.style = style
        self.border_color = border_color
        self.border_style = border_style
        super().__init__(['points', 'color',
                          'border_color', 'style', 'border_style'])

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

    def extra_initialize(self, objects):
        points = [Point.from_dict(point_dict) for point_dict in self.points]

        self.points = [None for _ in range(len(self.points))]

        self.color = Color(self.color)
        self.style = SurfaceStyle(self.style)
        self.border_color = Color(self.border_color)
        self.border_style = BorderStyle(self.border_style)

        for obj in objects:
            if all(self.points):
                return
            for i in range(len(self.points)):
                if not self.points[i] and str(points[i]) == str(obj):
                    self.points[i] = obj

    def set_style(self, drawer):
        self.color = drawer.polygon_color
        self.style = drawer.polygon_style
        self.border_color = drawer.polygon_border_color
        self.border_style = drawer.polygon_border_style

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


class Sphere(Serializable):
    RESIZABLE = True
    NAME = 'Sphere'

    def __init__(self, point: Point, radius=20.0,
                 color=Color.ORANGE_DARK, style=SurfaceStyle.SOLID,
                 border_color=Color.ORANGE_LIGHT, border_style=BorderStyle.SOLID):
        self.point = point
        self.radius = radius
        self.color = color
        self.style = style
        self.border_color = border_color
        self.border_style = border_style
        super().__init__(['point', 'radius', 'color',
                          'border_color', 'style', 'border_style'])

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

    def extra_initialize(self, objects):
        point = Point.from_dict(self.point)

        self.point = None

        self.color = Color(self.color)
        self.style = SurfaceStyle(self.style)
        self.border_color = Color(self.border_color)
        self.border_style = BorderStyle(self.border_style)

        for obj in objects:
            if self.point:
                return
            if not self.point and str(point) == str(obj):
                self.point = obj

    def set_style(self, drawer):
        self.color = drawer.sphere_color
        self.style = drawer.sphere_style
        self.border_color = drawer.sphere_border_color
        self.border_style = drawer.sphere_border_style


class Cylinder(Serializable):
    RESIZABLE = False

    def __init__(self, line: Line, radius=20.0):
        self.line = line
        self.radius = radius
        super().__init__(['line', 'radius'])

    def __str__(self):
        return f'ln!{str(self.line)}!{self.radius}'

    @staticmethod
    def from_string(str_representation: str, objects):
        params = str_representation.split('!')
        for obj in objects:
            if (str(obj) == params[1]):
                return Cylinder(obj, float(params[2]))
