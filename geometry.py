from PyQt5 import QtCore

class Vector3:
    def __init__(self, x: float, y: float, z: float):
        self.x = x
        self.y = y
        self.z = z

    def __add__(self, other):
        if isinstance(other, Vector3):
            return Vector3(self.x + other.x,
                           self.y + other.y,
                           self.z + other.z)

    def __mul__(self, other):
        if isinstance(other, Vector3):
            return Vector3(self.y*other.z - self.z*other.y,
                           self.z*other.x - self.x*other.z,
                           self.x*other.y - self.y*other.x)
        elif isinstance(other, float) or isinstance(other, int):
            return Vector3(self.x*other, self.y*other, self.z*other)

    def __eq__(self, other):
        return (isinstance(other, Vector3) and self.x == other.x and
                self.y == other.y and self.z == other.z)

    def to_matrix(self):
        return Matrix(3, 1, self.x, self.y, self.z)

    def to_tuple(self):
        return(self.x, self.y, self.z)

    def to_string(self):
        return f'{float(self.x)},{float(self.y)},{float(self.z)}'

    @staticmethod
    def from_string(str_representation):
        params = str_representation.split(',')
        return Vector3(float(params[0]), float(params[1]), float(params[2]))


class Point:
    def __init__(self, x: float, y: float, z: float, radius = 10):
        self.x = x
        self.y = y
        self.z = z
        self.radius = radius

    def __add__(self, other):
        if isinstance(other, Vector3):
            self.x += other.x
            self.y += other.y
            self.z += other.z
    
    def to_vector3(self):
        return Vector3(self.x, self.y, self.z)

    def paint(self, painter, points_display_table):
        width = max(5, 2*self.radius)
        painter.drawEllipse(points_display_table[self][0] - width / 2,
                            points_display_table[self][1] - width / 2,
                            width, width)
    
    def to_string(self):
        return f'pt,{float(self.x)},{float(self.y)},{float(self.z)},{int(self.radius)}'
    
    @staticmethod
    def from_string(str_representation):
        params = str_representation.split(',')
        return Point(float(params[1]), float(params[2]), float(params[3]), int(params[4][:-1]))


class Line:
    def __init__(self, start: Point, end: Point, radius = 5):
        self.start = start
        self.end = end
        self.radius = radius

    def paint(self, painter, points_display_table):
        painter.pen().setWidth(max(5, 2*self.radius))
        painter.drawLine(
            *(points_display_table[self.start]),
            *(points_display_table[self.end]))
    
    def to_string(self):
        return f'ln?|{self.start.to_string()}||{self.end.to_string()}|?{self.radius}'
    
    @staticmethod
    def from_string(str_representation: str, objects):
        params = str_representation.split('?')
        str_points = str_representation.split('|')
        points = []
        for obj in objects:
            if obj.to_string() == str_points[1] or obj.to_string() == str_points[3]:
                points.append(obj)
        return Line(points[0], points[1], int(params[2][:-1]))


class Polygon:
    def __init__(self, points, normal: Vector3,
                radius = 5):
        self.points = [point for point in points]
        self.radius = radius
        self.normal = normal

    def paint(self, painter, points_display_table):
        painter.pen().setWidth(max(5, 2*self.radius))
        painter.drawConvexPolygon(*[QtCore.QPointF(*(points_display_table[point])) for point in self.points])

    def to_string(self):
        str_representation = 'pg!'
        for point in self.points:
            str_representation += f'|{point.to_string()}|'
        str_representation += f'!({self.normal.to_string()})!{self.radius}'
        return str_representation
    
    @staticmethod
    def from_string(str_representation, objects):
        params = str_representation.split('!')
        str_points = str_representation.split('|')
        points = []
        for obj in objects:
            fl = False
            for i in range(1, len(str_points), 2):
                if obj.to_string() == str_points[i]:
                    fl = True 
            if fl:
                points.append(obj)
        return Polygon(points, Vector3.from_string(params[2][1:-1]), int(params[3][:-1]))


class Matrix:
    def __init__(self, string: int, column: int, *args: float):
        self.table = []
        self.zero_string = [0 for _ in range(column)]
        self.column = column
        for _ in range(string):
            self.table.append([])
        for i in range(column * string):
            self.table[i // column].append(args[i])

    def __getitem__(self, key):
        return self.table[key]

    def __mul__(self, other):
        if isinstance(other, Matrix):
            if self.column != len(other.table):
                raise ValueError("Incorrect multiply")
            ceils = []
            for i in range(len(self.table)):
                for j in range(other.column):
                    res = 0
                    for x in range(self.column):
                        res += self[i][x]*other[x][j]
                    ceils.append(res)
            return Matrix(len(self.table), other.column, *ceils)
        if isinstance(other, Vector3):
            return self * (other.to_matrix())

    def transpose(self):
        if len(self.table) != self.column:
            raise ValueError()
        ceils = []
        for i in range(self.column):
            for j in range(self.column):
                ceils.append(self[j][i])
        return Matrix(self.column, self.column, *ceils)

    def to_tuple(self):
        line = []
        for string in self.table:
            for element in string:
                line.append(element)
        return tuple(line)
