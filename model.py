from geometry import Point, Line, Polygon, Vector3, Matrix


class Model:
    def __init__(self):
        self.basis = (Vector3(1, 0, 0), Vector3(0, 1, 0), Vector3(0, 0, 1))
        self.origin = Point(0, 0, 0, 0)
        self.display_plate_basis = [Vector3(0, 1, 0), Vector3(0, 0, 1),
                                    Vector3(-1, 0, 0)]
        #self.display_plate_origin = Point(0, 0, -10, 0)
        self.objects = []
        self.matrix_of_display = None
        self.update_display_matrix(None)

    def add_point(self):
        self.objects.append(Point(0, 0, 0))

    def add_line(self, point1, point2):
        self.objects.append(Line(point1, point2))

    def add_polygon(self, points):  # for variable count of points
        self.objects.append(Polygon(points, Vector3(1, 0, 0)))

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

    def open(self, filename: str):
        with open(filename, 'r', encoding='utf8') as file:

            line = file.readline()
            objects = line.split(' ')
            self.basis = (Vector3.from_string(objects[0]),
                          Vector3.from_string(objects[1]),
                          Vector3.from_string(objects[2]))

            line = file.readline()
            self.origin = Point.from_string(line)

            line = file.readline()
            objects = line.split(' ')
            self.display_plate_basis = [Vector3.from_string(objects[0]),
                                        Vector3.from_string(objects[1]),
                                        Vector3.from_string(objects[2])]

            for line in file:
                if not line:
                    return
                obj = None
                if line[0:2] == 'pt':
                    obj = Point.from_string(line)
                elif line[0:2] == 'ln':
                    obj = Line.from_string(line, self.objects)
                elif line[0:2] == 'pg':
                    obj = Polygon.from_string(line, self.objects)
                self.objects.append(obj)

            self.update_display_matrix(None)

    def to_string(self):#стиль стилем, конечно, но разве так не лучше?
        str_representation = f'''{self.basis[0].to_string()} {self.basis[1].to_string()} {self.basis[2].to_string()}
{self.origin.to_string()}
{self.display_plate_basis[0].to_string()} {self.display_plate_basis[1].to_string()} {self.display_plate_basis[2].to_string()}
'''
        for obj in self.objects:
            str_representation += f'{obj.to_string()}\n'
        return str_representation
