from geometry import Point, Line, Plate, Vector3, Vector2, Matrix

class Model():
    def __init__(self):
        self.basis = (Vector3(1, 0, 0), Vector3(0, 1, 0), Vector3(0, 0, 1))
        self.origin = Point(0, 0, 0, 0)
        self.display_plate_basis = [Vector3(1, 0, 0), Vector3(0, 1, 0)]
        self.normal_vector = self.display_plate_basis[0] * self.display_plate_basis[1]  #2d
        self.display_plate_origin = Point(0, 0, -10, 0)
        self.objects = []
        self.matrix_of_display = None
        self.update_matrix_of_display(None)

    def add_point(self):
        self.objects.append(Point(0, 0, 0, 10))

    def add_line(self, point1, point2):
        self.objects.append(Line(point1, point2, 5))

    def add_plate(self, point1, point2, point3, point4):
        self.objects.append(Plate(Line(point1, point2, 5),
                            Line(point3, point4, 5), 5,
                            Vector3(1, 0, 0)))

    def get_display_vector_on_plate_of_display(self, vector):
        temp = -(self.normal_vector.x*vector.x + self.normal_vector.y*vector.y +
                 self.normal_vector.z*vector.z) / (self.normal_vector.x*self.normal_vector.x +
                 self.normal_vector.y*self.normal_vector.y + self.normal_vector.z*self.normal_vector.z)
        displayed_vector = Vector3(self.normal_vector.x*temp + vector.x,
                                   self.normal_vector.y*temp + vector.y,
                                   self.normal_vector.z*temp + vector.z)
        matrix = Matrix(3, 3, self.display_plate_basis[0].x, self.display_plate_basis[1].x,
                        displayed_vector.x, self.display_plate_basis[0].y,
                        self.display_plate_basis[1].y, displayed_vector.y,
                        self.display_plate_basis[0].z, self.display_plate_basis[1].z,
                        displayed_vector.z)
        return matrix.solve_matrix_by_gauss()

    def update_matrix_of_display(self, ort_matrix : Matrix):
        if not ort_matrix:
            a = self.get_display_vector_on_plate_of_display(self.basis[0])
            b = self.get_display_vector_on_plate_of_display(self.basis[1])
            c = self.get_display_vector_on_plate_of_display(self.basis[2])
            self.matrix_of_display = Matrix(2, 3, a[0], b[0], c[0], a[1], b[1], c[1])
        else:
            #self.matrix_of_display = ort_matrix.transpose()*self.matrix_of_display*ort_matrix
            self.display_plate_basis[0] = Vector3(*((ort_matrix*self.display_plate_basis[0].to_matrix()).to_tuple()))
            self.display_plate_basis[1] = Vector3(*((ort_matrix*self.display_plate_basis[1].to_matrix()).to_tuple()))
            self.normal_vector = Vector3(*((ort_matrix*self.normal_vector.to_matrix()).to_tuple()))
            self.update_matrix_of_display(None)     

