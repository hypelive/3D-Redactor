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
        self.display_plate_origin = Vector3(1000, 0, 0)
        self.objects = []
        self.is_perspective = False
        self.matrix_of_display = None
        self.update_display_matrix(None)

    def add_point(self, vector: Vector3):
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

    def update_display_matrix(self, ort_matrix: Matrix) -> None:
        if not ort_matrix:
            a = self.display_plate_basis[0]
            b = self.display_plate_basis[1]
            c = self.display_plate_basis[2]
            self.matrix_of_display = Matrix(
                3, 3, a.x, a.y, a.z, b.x, b.y, b.z, c.x, c.y, c.z)
        else:
            self.display_plate_basis[0] = Vector3(*((ort_matrix *
                                                     self.display_plate_basis[0]).to_tuple()))
            self.display_plate_basis[1] = Vector3(*((ort_matrix *
                                                     self.display_plate_basis[1]).to_tuple()))
            self.display_plate_basis[2] = Vector3(*((ort_matrix *
                                                     self.display_plate_basis[2]).to_tuple()))
            self.update_display_matrix(None)

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
