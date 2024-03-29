from .geometry import Vector3, Matrix
from .objects import Point, Line, Polygon, Sphere, Cylinder
from .serializable import Serializable
from .color import Color
import json


class Model:
    def __init__(self):
        self.basis = (Vector3(1, 0, 0), Vector3(0, 1, 0), Vector3(0, 0, 1))
        self.origin = Point(0, 0, 0)
        self.reset_display()
        self.objects = []

    def search_or_add(self, obj, *args):
        if isinstance(obj, Point):
            for model_obj in self.objects:
                if isinstance(model_obj, Point) and\
                        obj.almost_equal(model_obj):
                    return model_obj
            self.add_point(obj)

        return obj

    def add_point(self, vector, color=Color.ORANGE_LIGHT):
        if isinstance(vector, Vector3):
            self.objects.append(Point(vector.x, vector.y, vector.z,
                                      color=color))
        elif isinstance(vector, Point):
            self.objects.append(vector)

    def add_line(self, point1, point2, color, style):
        self.objects.append(Line(point1, point2, color=color, style=style))

    def add_polygon(self, points, border_color, border_style,
                    color, style):  # for variable count of points
        self.objects.append(Polygon(points,
                                    border_color=border_color,
                                    border_style=border_style,
                                    color=color, style=style))

    def add_sphere(self, vector: Vector3, border_color, border_style,
                   color, style):
        point = Point(vector.x, vector.y, vector.z)
        point.WIDTH = 0
        self.objects.append(point)
        self.objects.append(Sphere(point, border_color=border_color,
                                   border_style=border_style,
                                   color=color, style=style))

    def display_vector(self, vector: Vector3) -> tuple:
        return (self.matrix_of_display *
                vector).to_tuple()

    def undisplay_vector(self, vector: Vector3) -> tuple:
        return (self.matrix_of_display.transpose() *
                vector).to_tuple()

    def _set_display_basis(self, basis: list):
        self.display_plate_basis = basis
        self.update_display_matrix(None)

    def reset_display(self):
        self.display_plate_basis = [Vector3(0, 0, 1), Vector3(0, 1, 0),
                                    Vector3(-1, 0, 0)]
        self.display_plate_origin = Vector3(1000, 0, 0)
        self.matrix_of_display = None
        self.update_display_matrix(None)

    def update_display_matrix(self, ort_matrix: Matrix) -> None:
        if not ort_matrix:
            a = self.display_plate_basis[0]
            b = self.display_plate_basis[1]
            c = self.display_plate_basis[2]
            self.matrix_of_display = Matrix(
                3, 3, a.x, a.y, a.z, b.x, b.y, b.z, c.x, c.y, c.z)
        else:
            self.display_plate_basis[0] = Vector3(
                *((ort_matrix * self.display_plate_basis[0]).to_tuple()))
            self.display_plate_basis[1] = Vector3(
                *((ort_matrix * self.display_plate_basis[1]).to_tuple()))
            self.display_plate_basis[2] = Vector3(
                *((ort_matrix * self.display_plate_basis[2]).to_tuple()))
            self.update_display_matrix(None)

    def get_plate_equation_value(self, x, y, z):
        a = self.display_plate_basis[2].x
        b = self.display_plate_basis[2].y
        c = self.display_plate_basis[2].z
        return (a*(x - self.display_plate_origin.x) +
                b*(y - self.display_plate_origin.y) +
                c*(z - self.display_plate_origin.z))

    def get_cross(self, obj1, obj2):  # need check that cross in object
        if ((isinstance(obj1, Line) and isinstance(obj2, Polygon)) or
                (isinstance(obj1, Polygon) and isinstance(obj2, Line))):
            cross_vector = None
            if isinstance(obj1, Line):
                cross_vector = self.get_line_poly_cross(obj1, obj2)
            else:
                cross_vector = self.get_line_poly_cross(obj2, obj1)
            return cross_vector
        if isinstance(obj1, Line) and isinstance(obj2, Line):
            cross_vector = self.get_lines_cross(obj1, obj2)
            return cross_vector
        if isinstance(obj1, Polygon) and isinstance(obj2, Polygon):
            cross_line = self.get_polys_cross(obj1, obj2)
            return cross_line

    def get_line_poly_cross(self, line, polygon):
        normal_vector = polygon.get_normal_vector()
        guide_vector = line.get_guide_vector()
        devider = (normal_vector.x*guide_vector.x +
                   normal_vector.y*guide_vector.y +
                   normal_vector.z*guide_vector.z)
        if abs(devider) < 1e-4:
            return None
        t = (-(normal_vector.x*(line.start.x - polygon.points[0].x) +
               normal_vector.y*(line.start.y - polygon.points[0].y) +
               normal_vector.z*(line.start.z - polygon.points[0].z)) /
             devider)
        x = guide_vector.x*t + line.start.x
        y = guide_vector.y*t + line.start.y
        z = guide_vector.z*t + line.start.z
        return [Vector3(x, y, z)]

    def get_lines_cross(self, line1, line2):  # plates and line
        poly1 = Polygon([line2.start, line2.end, Point(1, 0, 0)])
        poly2 = Polygon([line2.start, line2.end, Point(0, 1, 0)])
        cross1 = self.get_line_poly_cross(line1, poly1)
        cross2 = self.get_line_poly_cross(line1, poly2)
        if cross1 == cross2:
            return cross1

    def get_polys_cross(self, poly1, poly2):
        buffer = []
        for line in poly1.get_surface():
            cross = self.get_line_poly_cross(line, poly2)
            if cross and line.is_inside_line(cross[0]):
                buffer.append(cross[0])

        return buffer

    def save(self, file):
        file.write(str(self))

    def open(self, file):
        basis = json.loads(next(file))
        self.basis = [Vector3(None, None, None).initialize(basis[i])
                      for i in range(len(basis))]

        origin = json.loads(next(file))
        self.origin = Point(None, None, None).initialize(origin)

        display_plate_basis = json.loads(next(file))
        self.display_plate_basis = [
            Vector3(None, None, None).initialize(display_plate_basis[i])
            for i in range(len(display_plate_basis))]

        for line in file:
            obj_dict = json.loads(line)
            if obj_dict['NAME'] == 'Point':
                self.objects.append(Point.from_dict(obj_dict))
            elif obj_dict['NAME'] == 'Line':
                self.objects.append(Line(None, None).initialize(
                    obj_dict, self.objects))
            elif obj_dict['NAME'] == 'Polygon':
                self.objects.append(Polygon(None).initialize(
                    obj_dict, self.objects))
            elif obj_dict['NAME'] == 'Sphere':
                self.objects.append(Sphere(None, None).initialize(
                    obj_dict, self.objects))

        self.update_display_matrix(None)

    def __str__(self):
        str_representation = f'''{json.dumps([vector.__dict__() for vector in self.basis])}
{json.dumps(self.origin.__dict__())}
{json.dumps([vector.__dict__() for vector in self.display_plate_basis])}
'''
        for obj in self.objects:
            str_representation += f'{json.dumps(obj.__dict__())}\n'
        return str_representation
