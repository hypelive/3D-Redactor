from geometry import Point, Line, Plate, Vector3, Vector2, Matrix


class Model():
    def __init__(self):
        self.basis = (Vector3(1, 0, 0), Vector3(0, 1, 0), Vector3(0, 0, 1))
        self.origin = Point(0, 0, 0, 0)
        self.display_plate_basis = [Vector3(0, 1, 0), Vector3(0, 0, 1), Vector3(-1, 0, 0)]
        self.display_plate_origin = Point(0, 0, -10, 0)
        self.objects = []
        self.matrix_of_display = None
        self.update_matrix_of_display(None)

    def add_point(self):
        self.objects.append(Point(0, 0, 0))

    def add_line(self, point1, point2):
        self.objects.append(Line(point1, point2, 5))

    def add_plate(self, point1, point2, point3, point4):
        self.objects.append(Plate(Line(point1, point2, 5),
                                  Line(point3, point4, 5), 5,
                                  Vector3(1, 0, 0)))

    def get_display_vector_on_plate_of_display(self, vector: Vector3) -> tuple:
        displayed_coordinates = (self.matrix_of_display.transpose() * vector).to_tuple()
        return displayed_coordinates[:2]
        

    def update_matrix_of_display(self, ort_matrix: Matrix) -> None:
        if not ort_matrix:
            a = self.display_plate_basis[0]
            b = self.display_plate_basis[1]
            c = self.display_plate_basis[2]
            self.matrix_of_display = Matrix(
                3, 3, a.x, b.x, c.x, a.y, b.y, c.y, a.z, b.z, c.z)
        else:
            self.display_plate_basis[0] = Vector3(*((ort_matrix * self.display_plate_basis[0]).to_tuple()))
            self.display_plate_basis[1] = Vector3(*((ort_matrix * self.display_plate_basis[1]).to_tuple()))
            self.display_plate_basis[2] = Vector3(*((ort_matrix * self.display_plate_basis[2]).to_tuple()))
            self.update_matrix_of_display(None)
