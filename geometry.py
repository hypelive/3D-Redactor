class Vector3():
    def __init__(self, x : float, y : float, z : float):
        self.x = x
        self.y = y
        self.z = z

    def __add__(self, other):
        if isinstance(other, Vector3):
            return Vector3(self.x + other.x,
                           self.y + other.y,
                           self.z + other.z)

    def __mul__(self, other):  #vectornoe multiply
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
            self.x += other.x
            self.y += other.y
            self.z += other.z

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
            if temp == 0:
                n += 1
                continue
            for i in range(self.column):
                self.table[n][i] = self.table[n][i] / temp  #first elem is 1 then
            for i in range(len(self.table)):
                if i != n:
                    temp = self.table[i][n]
                    for j in range(n, self.column):
                        self.table[i][j] = self.table[i][j] - temp*self.table[n][j]
            n += 1
        return tuple([string[self.column - 1] for string in self.table])
    
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


