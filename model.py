from geometry import Point, Line, Plate, Vector3, Vector2, Matrix

class Model():
    def __init__(self):
        self.basis = (Vector3(1, 0, 0), Vector3(0, 1, 0), Vector3(0, 0, 1))
        self.origin = Point(0, 0, 0, 0)
        self.display_plate_basis = (Vector3(1, 0, 1), Vector3(0, 1, 0))   #2d
        self.display_plate_origin = Point(0, 0, -10, 0)
        self.objects = []
        self.matrix_of_display = None
        self.update_matrix_of_display()

    def add_point(self):
        self.objects.append(Point(0, 0, 0, 100))

    def add_line(self, point1, point2):
        self.objects.append(Line(point1, point2, 5))

    def add_plate(self, point1, point2, point3, point4):
        self.objects.append(Plate(Line(point1, point2, 5),
                            Line(point3, point4, 5), 5,
                            Vector3(1, 0, 0)))

    def get_display_vector_on_plate_of_display(self, vector):
        normal_vector = self.display_plate_basis[0] * self.display_plate_basis[1]
        temp = -(normal_vector.x*vector.x + normal_vector.y*vector.y +
                 normal_vector.z*vector.z) / (normal_vector.x*normal_vector.x +
                 normal_vector.y*normal_vector.y + normal_vector.z*normal_vector.z)
        displayed_vector = Vector3(normal_vector.x*temp + vector.x,
                                   normal_vector.y*temp + vector.y,
                                   normal_vector.z*temp + vector.z)
        matrix = Matrix(3, 3, self.display_plate_basis[0].x, self.display_plate_basis[1].x,
                        displayed_vector.x, self.display_plate_basis[0].y,
                        self.display_plate_basis[1].y, displayed_vector.y,
                        self.display_plate_basis[0].z, self.display_plate_basis[1].z,
                        displayed_vector.z)
        return matrix.solve_matrix_by_gauss()

    def update_matrix_of_display(self):
        if not self.matrix_of_display:
            a = self.get_display_vector_on_plate_of_display(self.basis[0])
            b = self.get_display_vector_on_plate_of_display(self.basis[1])
            c = self.get_display_vector_on_plate_of_display(self.basis[2])
            self.matrix_of_display = Matrix(2, 3, a[0], b[0], c[0], a[1], b[1], c[1])
        else:
            #self.matrix_of_display * matrix of ortagonal display
            pass      

