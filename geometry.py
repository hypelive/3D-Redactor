class Vector3():
    def __init__(self, x : float, y : float, z : float):
        self.x = x
        self.y = y
        self.z = z

    def __mul__(self, other):  #vectornoe multiply
        if isinstance(other, Vector3):
            return Vector3(self.y*other.z - self.z*other.y,
                           self.z*other.x - self.x*other.z,
                           self.x*other.y - self.y*other.x)

    def __eq__(self, other):
        return (isinstance(other, Vector3) and self.x == other.x and
               self.y == other.y and self.z == other.z)

class Vector2():
    def __init__(self, x : float, y : float):
        self.x = x
        self.y = y

class Point():
    def __init__(self, x : float, y : float, z : float, radius : float):
        self.x = x
        self.y = y
        self.z = z
        self.radius = radius
    
    def __add__(self, other):
        if isinstance(other, Vector3):
            return Point(self.x + other.x, self.y + other.y, self.z + other.z, self.radius)

class Line():
    def __init__(self, start : Point, end : Point, radius : float):
        self.start = start
        self.end = end
        self.radius = radius

class Plate():
    def __init__(self, first_line : Line, second_line : Line, radius : float, normal : Vector3):
        self.first_line = first_line
        self.second_line = second_line
        self.radius = radius
        self.normal = normal

class Matrix():
    def __init__(self, string : int, column : int, *args : float):
        self.table = []
        self.zero_string = [0 for _ in range(column)]
        self.column = column
        for _ in range(string):
            self.table.append([])
        for i in range(column * string):
            self.table[i // column].append(args[i])

    def __getitem__(self, key):
        return self.table[key]

    def delete_string(self, key):  #do we need it?
        self.table.remove(self.table[key])

    def solve_matrix_by_gauss(self):
        n = 0
        while(n < len(self.table)):
            while self.zero_string in self.table:
                self.table.remove(self.zero_string)
            if (n >= len(self.table)):
                break #delete zero strings
            temp = self.table[n][n]
            for i in range(self.column):
                self.table[n][i] = self.table[n][i] / temp  #first elem is 1 then
            for i in range(len(self.table)):
                if i != n:
                    temp = self.table[i][n]
                    for j in range(n, self.column):
                        self.table[i][j] = self.table[i][j] - temp*self.table[n][j]
            n += 1
        return tuple([string[self.column - 1] for string in self.table])
    
    def __mul__(self, other):  #only for matix 2x3 * 3x1
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
            #return Matrix(2, 1, self.table[0][0]*other[0][0] + self.table[0][1]*other[1][0] +
                            #self.table[0][2]*other[2][0], self.table[1][0]*other[0][0] +
                            #self.table[1][1]*other[1][0] + self.table[1][0]*other[2][0])

    def to_tuple(self):
        line = []
        for string in self.table:
            for element in string:
                line.append(element)
        return tuple(line)


