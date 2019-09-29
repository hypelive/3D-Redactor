import sys
import time
from PyQt5 import QtGui, QtWidgets, QtCore, QtPrintSupport #here is matrix,  https://www.learnpyqt.com/courses/custom-widgets/bitmap-graphics/
import model
from geometry import Matrix, Vector3, Point
import math

class RedactorWindow(QtWidgets.QMainWindow):

    def __init__(self):
        super().__init__()
        self.model = None
        self.display_table = {}
        self.last_x = None
        self.last_time_clicked = time.time()
        self.initGUI()

    def initGUI(self):
        self.setGeometry(0, 0, 480, 270)  #x y wide tall
        icon = QtGui.QIcon('textures\\icon.png')
        self.setWindowIcon(icon)
        self.setWindowTitle('Black Box redactor')

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
        but.setGeometry(10, 15, 30, 20)
        but.clicked.connect(self.init_new_model)

        but = QtWidgets.QPushButton('O', self)
        but.setGeometry(50, 15, 30, 20)
        but.clicked.connect(self.open_model)

        but = QtWidgets.QPushButton('S', self)
        but.setGeometry(90, 15, 30, 20)
        but.clicked.connect(self.save_model)

        but = QtWidgets.QPushButton('Pt', self)
        but.setGeometry(360, 15, 30, 30)
        but.clicked.connect(self.add_point)

        but = QtWidgets.QPushButton('Ln', self)
        but.setGeometry(400, 15, 30, 30)
        but.clicked.connect(self.add_line)

        but = QtWidgets.QPushButton('Pln', self)
        but.setGeometry(440, 15, 30, 30)
        but.clicked.connect(self.add_plate)

    def update_display(self):
        painter = QtGui.QPainter(self.label.pixmap())
        painter.setPen(QtGui.QPen(QtCore.Qt.red, 5, QtCore.Qt.SolidLine))
        painter.setBrush(QtGui.QBrush(QtCore.Qt.red))
        painter.fillRect(0, 0, 1200, 625, QtGui.QGradient.Preset(10))
        for obj in self.model.objects:
            if isinstance(obj, Point):
                display_coord = (self.model.matrix_of_display * Matrix(3, 1, obj.x, obj.y, obj.z)).to_tuple()
                self.display_table[obj] = (display_coord[0] + self.model.display_plate_origin.x,
                                           display_coord[1] + self.model.display_plate_origin.y)
                width = max(5, obj.radius)
                painter.drawEllipse(display_coord[0] + self.model.display_plate_origin.x,
                                    display_coord[1] + self.model.display_plate_origin.y, width, width)
        painter.end()
        self.update()

    def mouseMoveEvent(self, event):
        #object_to_move = None
        #for obj in self.display_table:   #it doesn't works
        #    if obj.radius*4 > math.sqrt((event.x() - self.display_table[obj][0])*(event.x() - self.display_table[obj][0]) +
        #                              (event.y() - self.display_table[obj][1])*(event.y() - self.display_table[obj][1])):
        #        dist = math.sqrt((event.x() - self.display_table[obj][0])*(event.x() - self.display_table[obj][0]) +
        #                              (event.y() - self.display_table[obj][1])*(event.y() - self.display_table[obj][1]))
        #        object_to_move = obj
        #        break
        if time.time() - self.last_time_clicked > 0.3: #in seconds
            self.last_x = event.x()
            self.last_y = event.y()
            self.last_time_clicked = time.time()
        #elif object_to_move:
        #    object_to_move += Vector3(event.x() - self.last_x,
        #                              event.y() - self.last_y,
        #                              0)
        else:
            self.model.display_plate_origin += Vector3(event.x() - self.last_x,
                                                       event.y() - self.last_y,
                                                       0)
            self.last_x = event.x()
            self.last_y = event.y()
        self.update_display()

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
            self.model.add_line()
    
    def add_plate(self):
        if self.model:
            self.model.add_plate()