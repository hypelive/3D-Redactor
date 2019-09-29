import sys
from PyQt5 import QtGui, QtWidgets, QtCore, QtPrintSupport #here is matrix,  https://www.learnpyqt.com/courses/custom-widgets/bitmap-graphics/
import model
from geometry import Matrix, Vector3, Point

class RedactorWindow(QtWidgets.QMainWindow):

    def __init__(self):
        super().__init__()
        self.model = None
        self.initGUI()

    def initGUI(self):
        self.setGeometry(0, 0, 480, 270)  #x y wide tall
        icon = QtGui.QIcon('textures\\icon.png')
        self.setWindowIcon(icon)
        self.setWindowTitle('Black Box redactor')

        self.label = QtWidgets.QLabel(self)
        canvas = QtGui.QPixmap(1200, 625)
        canvas.fill(QtGui.QColor('gray'))
        self.label.setPixmap(canvas)
        self.setCentralWidget(self.label)
        painter = QtGui.QPainter(self.label.pixmap())
        pen = QtGui.QPen()
        pen.setWidth(40)
        pen.setColor(QtGui.QColor('red'))
        painter.setPen(pen)
        painter.drawPoint(50, 100)
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
        for obj in self.model.objects:
            if isinstance(obj, Point):
                display_coord = (self.model.matrix_of_display * Matrix(3, 1, obj.x, obj.y, obj.z)).to_tuple()
                #print point with radius in display coord

    def init_new_model(self):
        self.model = model.Model()

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