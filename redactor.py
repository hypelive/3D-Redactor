import sys
from PyQt5 import QtGui, QtWidgets, QtCore #here is matrix,  https://www.learnpyqt.com/courses/custom-widgets/bitmap-graphics/
import geometry
import model

class RedactorWindow(QtWidgets.QWidget):

    def __init__(self):
        super().__init__()
        self.model = None
        self.initGUI()

    def initGUI(self):
        self.setGeometry(0, 0, 480, 270)  #x y wide tall
        icon = QtGui.QIcon('textures\\icon.png')
        self.setWindowIcon(icon)
        self.setWindowTitle('Black Box redactor')

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
        but.setGeometry(0, 150, 30, 30)
        but.clicked.connect(self.add_point)

        but = QtWidgets.QPushButton('Ln', self)
        but.setGeometry(0, 185, 30, 30)
        but.clicked.connect(self.add_line)

        but = QtWidgets.QPushButton('Pln', self)
        but.setGeometry(0, 220, 30, 30)
        but.clicked.connect(self.add_plate)

        self.showMaximized()

    def update(self):
        pass

    def display_model(self):
        pass

    def init_new_model(self):
        self.model = model.Model()

    def open_model(self):
        pass

    def save_model(self):
        pass

    def add_point(self):
        if self.model:
            self.model.add_point()

    def add_line(self):
        if self.model:
            self.model.add_line()
    
    def add_plate(self):
        if self.model:
            self.model.add_plate()