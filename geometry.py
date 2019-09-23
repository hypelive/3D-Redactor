class Point():
    def __init__(self, x : float, y : float):
        self.x = x
        self.y = y

class Line():
    def __init__(self, start : Point, end : Point):
        self.start = start
        self.end = end

class Square():
    def __init__(self, first_line : Line, second_line : Line):
        self.first_line = first_line
        self.second_line = second_line
