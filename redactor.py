import sys
import time
from PyQt5 import QtGui, QtWidgets, QtCore, QtPrintSupport
import model
from geometry import Matrix, Vector3, Point, Line, Polygon
import math


class RedactorWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        self.model = None

        self.split_coordinates = [600, 315]
        self.axiss_size = 250
        self.axiss_width = 3 
        self.points_display_table = {}
        self.point_buffer = []

        self.last_x = None
        self.last_y = None
        self.last_time_clicked = time.time()

        self.modes = {
            QtCore.Qt.Key_Q: "drag object",
            QtCore.Qt.Key_E: "drag plate",
            QtCore.Qt.Key_L: "line",
            QtCore.Qt.Key_P: "polygon"}

        self.display_axiss = False

        rotate_angle = math.pi / 90
        self.rotate = {
            QtCore.Qt.Key_D: Matrix(3, 3, math.cos(rotate_angle),
                                    -math.sin(rotate_angle), 0,
                                    math.sin(rotate_angle),
                                    math.cos(rotate_angle),
                                    0, 0, 0, 1),
            QtCore.Qt.Key_W: Matrix(3, 3, 1, 0, 0, 0,
                                    math.cos(rotate_angle),
                                    -math.sin(rotate_angle), 0,
                                    math.sin(rotate_angle),
                                    math.cos(rotate_angle)),
            QtCore.Qt.Key_A: Matrix(3, 3, math.cos(-rotate_angle),
                                    -math.sin(-rotate_angle), 0,
                                    math.sin(-rotate_angle),
                                    math.cos(-rotate_angle),
                                    0, 0, 0, 1),
            QtCore.Qt.Key_S: Matrix(3, 3, 1, 0, 0, 0,
                                    math.cos(-rotate_angle),
                                    -math.sin(-rotate_angle), 0,
                                    math.sin(-rotate_angle),
                                    math.cos(-rotate_angle))
        }

        self.mode = "drag plate"
        self.object_to_interact = None

        self.initGUI()

    def initGUI(self):
        self.setGeometry(0, 0, 1200, 625)  # x y wide tall
        icon = QtGui.QIcon('textures\\icon.png')
        self.setWindowIcon(icon)
        self.setWindowTitle('Black Box editor')
        self.label = QtWidgets.QLabel(self)

        canvas = QtGui.QPixmap(1200, 625)
        canvas.fill(QtGui.QColor('grey'))
        self.label.setPixmap(canvas)
        self.setCentralWidget(self.label)

        painter = QtGui.QPainter(self.label.pixmap())
        pen = QtGui.QPen()
        pen.setWidth(40)
        pen.setColor(QtGui.QColor('red'))
        painter.setPen(pen)
        painter.end()

        but = QtWidgets.QPushButton('N', self)
        but.setGeometry(1080, 600, 30, 20)
        but.clicked.connect(self.init_new_model)

        but = QtWidgets.QPushButton('O', self)
        but.setGeometry(1120, 600, 30, 20)
        but.clicked.connect(self.open_model)

        but = QtWidgets.QPushButton('S', self)
        but.setGeometry(1160, 600, 30, 20)
        but.clicked.connect(self.save_model)

        but = QtWidgets.QPushButton('Pt', self)
        but.setGeometry(1150, 520, 40, 30)
        but.clicked.connect(self.add_point)

        but = QtWidgets.QPushButton('Ln', self)
        but.setGeometry(1150, 480, 40, 30)
        but.clicked.connect(self.add_line)

        but = QtWidgets.QPushButton('Pln', self)
        but.setGeometry(1150, 440, 40, 30)
        but.clicked.connect(self.add_polygon)

    def update_display(self):
        painter = QtGui.QPainter(self.label.pixmap())
        painter.setPen(QtGui.QPen(QtCore.Qt.red, 5, QtCore.Qt.SolidLine))
        painter.setBrush(QtGui.QBrush(QtCore.Qt.red))
        painter.fillRect(0, 0, 1200, 625, QtGui.QGradient.Preset(12))

        if self.display_axiss:
            self.draw_coordinates_system(painter)

        for obj in self.model.objects:
            if isinstance(obj, Point):
                self.paint_point(obj, painter)
            elif isinstance(obj, Line):
                self.paint_line(obj, painter)
            elif isinstance(obj, Polygon):
                self.paint_polygon(obj, painter)
        painter.drawText(15, 15, f"selected mode: {self.mode}")
        painter.end()
        self.update()

    def draw_coordinates_system(self, painter : QtGui.QPainter): #can vinesti v method
        painter.setPen(QtGui.QPen(QtCore.Qt.blue, self.axiss_width,
                                 QtCore.Qt.SolidLine))
        self.paint_point(self.model.origin, painter)
        
        painter.setPen(QtGui.QPen(QtCore.Qt.green, self.axiss_width,
                                 QtCore.Qt.SolidLine))
        temp_point = Point(self.model.basis[0].x * self.axiss_size,
                          self.model.basis[0].y * self.axiss_size,
                          self.model.basis[0].z * self.axiss_size, 5)
        self.paint_point(temp_point, painter)
        self.paint_line(Line(self.model.origin, temp_point, 5), painter)
        
        painter.setPen(QtGui.QPen(QtCore.Qt.black, self.axiss_width,
                                 QtCore.Qt.SolidLine))
        temp_point = Point(self.model.basis[1].x * self.axiss_size,
                          self.model.basis[1].y * self.axiss_size,
                          self.model.basis[1].z * self.axiss_size, 5)
        self.paint_point(temp_point, painter)
        self.paint_line(Line(self.model.origin, temp_point, 5), painter)
        
        painter.setPen(QtGui.QPen(QtCore.Qt.yellow, self.axiss_width,
                                 QtCore.Qt.SolidLine))
        temp_point = Point(self.model.basis[2].x * self.axiss_size,
                          self.model.basis[2].y * self.axiss_size,
                          self.model.basis[2].z * self.axiss_size, 5)
        self.paint_point(temp_point, painter)
        self.paint_line(Line(self.model.origin, temp_point, 5), painter)
        
        painter.setPen(QtGui.QPen(QtCore.Qt.red, 5, QtCore.Qt.SolidLine))

    def paint_point(self, point, painter):
        display_coord = self.model.get_display_vector_on_plate_of_display(point.to_vector3())
        width = max(5, 2*point.radius)
        self.points_display_table[point] = (display_coord[0] +
                                            self.split_coordinates[0],
                                            display_coord[1] +
                                            self.split_coordinates[1])
        painter.drawEllipse(self.points_display_table[point][0] - width / 2,
                            self.points_display_table[point][1] - width / 2,
                            width, width)

    def paint_line(self, line, painter):
        painter.pen().setWidth(max(5, 2*line.radius))
        painter.drawLine(
            *(self.points_display_table[line.start]),
            *(self.points_display_table[line.end]))

    def paint_polygon(self, polygon, painter):#rework
        painter.pen().setWidth(max(5, 2*polygon.first_line.radius))
        painter.drawConvexPolygon(QtCore.QPointF(*(self.points_display_table[polygon.first_line.start])),
                                    QtCore.QPointF(*(self.points_display_table[polygon.first_line.end])),
                                    QtCore.QPointF(*(self.points_display_table[polygon.second_line.start])),
                                    QtCore.QPointF(*(self.points_display_table[polygon.second_line.end])))

    def mousePressEvent(self, event):
        if not self.model:
            return
        if self.mode == "line":
            self.update_object_to_interact(event)
            if (self.object_to_interact):
                self.point_buffer.append(self.object_to_interact)
            if len(self.point_buffer) == 2:
                self.model.add_line(self.point_buffer[0],
                                    self.point_buffer[1])
                self.mode = "drag object"
                self.point_buffer = []
        if self.mode == "polygon":
            self.update_object_to_interact(event)
            if (self.object_to_interact):
                self.point_buffer.append(self.object_to_interact)
            if len(self.point_buffer) == 4:
                self.model.add_polygon(self.point_buffer[0],
                                       self.point_buffer[1],
                                       self.point_buffer[2],
                                       self.point_buffer[3])
                self.mode = "drag object"
                self.point_buffer = []
        self.object_to_interact = None
        self.last_x = event.x()  # 0
        self.last_y = event.y()  # 0
        self.last_time_clicked = time.time()
        self.update_display()

    def mouseMoveEvent(self, event: QtGui.QMouseEvent):
        if not self.model:
            return
        if self.mode == "drag object":
            if time.time() - self.last_time_clicked < 0.15:
                if not self.object_to_interact:  # in seconds
                    self.update_object_to_interact(event)
                if self.object_to_interact:
                    self.object_to_interact + (
                        self.model.display_plate_basis[0]*
                        (event.x() - self.last_x) +
                        self.model.display_plate_basis[1]
                        *(event.y() - self.last_y))
            else:
                self.object_to_interact = None
        elif self.mode == "drag plate":
            if time.time() - self.last_time_clicked < 0.15:
                self.split_coordinates[0] += (event.x() - self.last_x) 
                self.split_coordinates[1] += (event.y() - self.last_y)
        self.last_x = event.x()  # 0
        self.last_y = event.y()  # 0
        self.last_time_clicked = time.time()
        self.update_display()

    def keyPressEvent(self, event: QtGui.QKeyEvent):
        if not self.model:
            return
        if event.key() == QtCore.Qt.Key_CapsLock:
            self.display_axiss = not self.display_axiss
        elif event.key() in self.modes:
            self.mode = self.modes[event.key()]
            self.point_buffer = []
        elif event.key() in self.rotate:
            self.model.update_matrix_of_display(self.rotate[event.key()])
        self.update_display()

    def update_object_to_interact(self, event): #rework too distance
        self.object_to_interact = None
        for obj in self.model.objects:
            if obj in self.points_display_table:
                distance = math.sqrt((event.x() - self.points_display_table[obj][0])*
                                    (event.x() - self.points_display_table[obj][0]) +
                                    (event.y() - self.points_display_table[obj][1])*
                                    (event.y() - self.points_display_table[obj][1]))
                if obj.radius > distance:
                    self.object_to_interact = obj
                    break

    def init_new_model(self):
        self.model = model.Model()
        self.update_display()

    def open_model(self):
        pass

    def save_model(self):
        pass

    def add_point(self):
        if self.model:
            self.model.add_point()
            self.update_display()

    def add_line(self):
        if self.model:
            self.mode = self.modes[QtCore.Qt.Key_L]
            self.update_display()

    def add_polygon(self):
        if self.model:
            self.mode = self.modes[QtCore.Qt.Key_P]
            self.update_display()
