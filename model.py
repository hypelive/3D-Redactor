from geometry import Vector3, Matrix
from objects import Point, Line, Polygon, Sphere, Cylinder
import json


class Model:
    def __init__(self):
        self.basis = (Vector3(1, 0, 0), Vector3(0, 1, 0), Vector3(0, 0, 1))
        self.origin = Point(0, 0, 0)
        self.display_plate_basis = [Vector3(0, 1, 0), Vector3(0, 0, 1),
                                    Vector3(-1, 0, 0)]
        #self.display_plate_origin = Point(0, 0, -10)
        self.objects = []
        self.matrix_of_display = None
        self.update_display_matrix(None)

    def add_point(self):
        self.objects.append(Point(0, 0, 0))

    def add_line(self, point1, point2):
        self.objects.append(Line(point1, point2))

    def add_polygon(self, points):  # for variable count of points
        self.objects.append(Polygon(points))

    def add_sphere(self):
        point = Point(0, 0, 0)
        point.WIDTH = 0
        self.objects.append(point)
        self.objects.append(Sphere(point))

    def display_vector(self, vector: Vector3) -> tuple:
        displayed_coordinates = (self.matrix_of_display.transpose() *
                                 vector).to_tuple()
        return displayed_coordinates[:2]

    def update_display_matrix(self, ort_matrix: Matrix) -> None:
        if not ort_matrix:
            a = self.display_plate_basis[0]
            b = self.display_plate_basis[1]
            c = self.display_plate_basis[2]
            self.matrix_of_display = Matrix(
                3, 3, a.x, b.x, c.x, a.y, b.y, c.y, a.z, b.z, c.z)
        else:
            self.display_plate_basis[0] = Vector3(*((ort_matrix *
                                                     self.display_plate_basis[0]).to_tuple()))
            self.display_plate_basis[1] = Vector3(*((ort_matrix *
                                                     self.display_plate_basis[1]).to_tuple()))
            self.display_plate_basis[2] = Vector3(*((ort_matrix *
                                                     self.display_plate_basis[2]).to_tuple()))
            self.update_display_matrix(None)

    def save(self, filename: str):
        with open(filename, 'w', encoding='utf8') as file:
            file.write(self.to_string())
    
    def save_j(self, filename: str):
        with open(filename, 'w', encoding='utf8') as file:
            file.write(json.dumps(self.__dict__()))

    def open(self, filename: str):
        with open(filename, 'r', encoding='utf8') as file:

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

            for line in file:
                if not line:
                    return
                obj = None
                if line.startswith('pt'):
                    obj = Point.from_string(line)
                elif line[0:2] == 'ln':
                    obj = Line.from_string(line, self.objects)
                elif line[0:2] == 'pg':
                    obj = Polygon.from_string(line, self.objects)
                elif line[0:2] == 'sp':
                    obj = Sphere.from_string(line, self.objects)
                elif line[0:2] == 'cl':
                    obj = Cylinder.from_string(line, self.objects)
                self.objects.append(obj)

            self.update_display_matrix(None)

    def open_j(self, filename: str):
        dedictors = {
            '__Line__': Line.__dedict__,
            '__Polygon': Polygon.__dedict__
        }
        with open(filename, 'r', encoding='utf8') as file:
            model_dict = json.loads(file.read())
        if not '__Model__' in model_dict:
            raise Exception('unknown save file')
        self.basis = [Vector3(vector['x'], vector['y'], vector['z']) for vector in model_dict['basis'] if '__Vector3__' in vector]
        self.origin = Point(model_dict['origin']['x'], model_dict['origin']['y'], model_dict['origin']['z'])
        self.display_plate_basis = [Vector3(vector['x'], vector['y'], vector['z']) for vector in model_dict['display_plate_basis'] if '__Vector3__' in vector]
        for obj in model_dict['objects']:
            if '__Point__' in obj:
                self.objects.append(Point.__dedict__(obj))
        for obj in model_dict['objects']:
            for key in dedictors:
                if key in obj:
                    self.objects.append(dedictors[key](obj, self.objects)) 


    def to_string(self):  # стиль стилем, конечно, но разве так не лучше?
        str_representation = f'''{self.basis[0].to_string()} {self.basis[1].to_string()} {self.basis[2].to_string()}
{self.origin.to_string()}
{self.display_plate_basis[0].to_string()} {self.display_plate_basis[1].to_string()} {self.display_plate_basis[2].to_string()}
'''
        for obj in self.objects:
            str_representation += f'{obj.to_string()}\n'
        return str_representation

    def __dict__(self):
        return {
            '__Model__': True,
            'basis': [vector.__dict__() for vector in self.basis],
            'origin': self.origin.__dict__(),
            'display_plate_basis': [vector.__dict__() for vector in self.display_plate_basis],
            'objects': [obj.__dict__() for obj in self.objects]
        }