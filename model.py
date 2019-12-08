from geometry import Vector3, Matrix
from objects import Point, Line, Polygon, Sphere, Cylinder
import json
import numpy as np


class Model:
    def __init__(self):
        self.basis = (Vector3(1, 0, 0), Vector3(0, 1, 0), Vector3(0, 0, 1))
        self.origin = Point(0, 0, 0)
        self.display_plate_basis = [Vector3(0, 0, 1), Vector3(0, 1, 0),
                                    Vector3(-1, 0, 0)]
        self.interract = [Vector3(0, 0, 1), Vector3(0, 1, 0),
                          Vector3(-1, 0, 0)]
        self.display_plate_origin = Vector3(7, 0, 0)
        self.focus = self.display_plate_origin - \
            (self.display_plate_basis[2] * 3)
        self.objects = []
        self.is_perspective = True
        self.matrix_of_display = None
        self.update_display_matrix(None)

    def add_point(self, vector: Vector3):
        vector += self.display_plate_origin
        self.objects.append(Point(vector.x, vector.y, vector.z))

    def add_line(self, point1, point2):
        self.objects.append(Line(point1, point2))

    def add_polygon(self, points):  # for variable count of points
        self.objects.append(Polygon(points))

    def add_sphere(self, vector: Vector3):
        point = Point(vector.x, vector.y, vector.z)
        point.WIDTH = 0
        self.objects.append(point)
        self.objects.append(Sphere(point))

    def display_vector(self, vector: Vector3) -> tuple:
        return (self.matrix_of_display *
                vector).to_tuple()

    def undisplay_vector(self, vector: Vector3) -> tuple:
        return (self.matrix_of_display.transpose() *
                vector).to_tuple()

    def _set_display_basis(self, basis: list):
        self.display_plate_basis = basis
        self.update_display_matrix(None)

    def move_focus(self, value: float):
        self.focus += self.display_plate_basis[2] * value
        self.update_display_matrix(None)

    def move_display_origin(self, x_value: float, y_value: float):
        self.display_plate_origin += (self.display_plate_basis[0]*x_value +
                                      self.display_plate_basis[1]*y_value)
        self.update_display_matrix(None)

    def update_display_matrix(self, ort_matrix: Matrix) -> None:
        if not ort_matrix:
            if not self.is_perspective:
                a = self.display_plate_basis[0]
                b = self.display_plate_basis[1]
                c = self.display_plate_basis[2]
            else:  # we dont need to display when no channges
                a = self.get_display_on_display_plate(self.basis[1])
                b = self.get_display_on_display_plate(self.basis[2])
                c = self.get_display_on_display_plate(self.basis[0])
            self.interract[0] = a
            self.interract[1] = b
            self.interract[2] = c
            self.matrix_of_display = Matrix(
                3, 3, a.x, a.y, a.z, b.x, b.y, b.z, c.x, c.y, c.z)

        else:
            self.display_plate_basis[0] = Vector3(*((ort_matrix *
                                                     self.display_plate_basis[0]).to_tuple()))
            self.display_plate_basis[1] = Vector3(*((ort_matrix *
                                                     self.display_plate_basis[1]).to_tuple()))
            self.display_plate_basis[2] = Vector3(*((ort_matrix *
                                                     self.display_plate_basis[2]).to_tuple()))
            self.focus = self.display_plate_origin - \
                (self.display_plate_basis[2] * 3)
            self.update_display_matrix(None)

    def get_display_on_display_plate(self, vector: Vector3) -> Vector3:
        A = self.display_plate_basis[2].x
        B = self.display_plate_basis[2].y
        C = self.display_plate_basis[2].z
        line_vector = self.focus - vector
        t = -(A*(vector.x - self.display_plate_origin.x) +
              B*(vector.y - self.display_plate_origin.y) +
              C*(vector.z - self.display_plate_origin.z)) / (A*line_vector.x +
                                                             B*line_vector.y +
                                                             C*line_vector.z)
        x = line_vector.x*t + vector.x - self.display_plate_origin.x
        y = line_vector.y*t + vector.y - self.display_plate_origin.y
        z = line_vector.z*t + vector.z - self.display_plate_origin.z

        a = np.array([[self.display_plate_basis[0].x, self.display_plate_basis[1].x, self.display_plate_basis[2].x],
                      [self.display_plate_basis[0].y, self.display_plate_basis[1].y,
                          self.display_plate_basis[2].y],
                      [self.display_plate_basis[0].z, self.display_plate_basis[1].z, self.display_plate_basis[2].z]])
        b = np.array([x, y, z])
        solve = np.linalg.solve(a, b)
        return Vector3(solve[0], solve[1], solve[2])

    def get_plate_equation_value(self, x, y, z):
        a = self.display_plate_basis[2].x
        b = self.display_plate_basis[2].y
        c = self.display_plate_basis[2].z
        return (a*(x - self.display_plate_origin.x) +
                b*(y - self.display_plate_origin.y) +
                c*(z - self.display_plate_origin.z))

    def save(self, file):
        file.write(str(self))

    def open(self, file):
        line = next(file)
        objects = line.split(' ')
        self.basis = (Vector3.from_string(objects[0]),
                      Vector3.from_string(objects[1]),
                      Vector3.from_string(objects[2]))

        line = next(file)
        self.origin = Point.from_string(line)

        line = next(file)
        objects = line.split(' ')
        self.display_plate_basis = [Vector3.from_string(objects[0]),
                                    Vector3.from_string(objects[1]),
                                    Vector3.from_string(objects[2])]

        destringers = {
            'pt': Point.from_string,
            'ln': Line.from_string,
            'pg': Polygon.from_string,
            'sp': Sphere.from_string,
            'cl': Cylinder.from_string
        }

        for line in file:
            if not line:
                return
            obj = destringers[line[0:2]](line, self.objects)
            self.objects.append(obj)

        self.update_display_matrix(None)

    def __str__(self):  # стиль стилем, конечно, но разве так не лучше?
        str_representation = f'''{str(self.basis[0])} {str(self.basis[1])} {str(self.basis[2])}
{str(self.origin)}
{str(self.display_plate_basis[0])} {str(self.display_plate_basis[1])} {str(self.display_plate_basis[2])}
'''
        for obj in self.objects:
            str_representation += f'{str(obj)}\n'
        return str_representation
