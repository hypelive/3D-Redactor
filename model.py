from geometry import Point, Line, Plate, Vector3, Vector2

class Model():
    def __init__(self):
        self.basis = (Vector3(1, 0, 0), Vector3(0, 1, 0), Vector3(0, 0, 1))
        self.origin = Point(0, 0, 0, 0)
        self.display_plate_basis = (Vector3(1, 0, 0), Vector3(0, 1, 0))   #2d
        self.display_plate_origin = Point(0, 0, -10, 0)
        self.objects = []

    def add_point(self):
        pass

    def add_line(self):
        pass

    def add_plate(self):
        pass


