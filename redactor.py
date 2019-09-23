import sys
from PyQt5 import QtGui, QtWidgets, QtCore #here is matrix,  https://www.learnpyqt.com/courses/custom-widgets/bitmap-graphics/
import geometry

class RedactorWindow(QtWidgets.QWidget):

    def __init__(self):
        super().__init__()
        self.initGUI()

    def initGUI(self):
        self.setGeometry(0, 0, 480, 270)  #x y wide tall
        icon = QtGui.QIcon('textures\\icon.png')
        self.setWindowIcon(icon)
        self.setWindowTitle('Black Box redactor')

        but = QtWidgets.QPushButton('N', self)
        but.setGeometry(10, 15, 30, 20)
        #btn.clicked.connect(self.fu())

        but = QtWidgets.QPushButton('O', self)
        but.setGeometry(50, 15, 30, 20)

        but = QtWidgets.QPushButton('S', self)
        but.setGeometry(90, 15, 30, 20)

        but = QtWidgets.QPushButton('Pt', self)
        but.setGeometry(0, 150, 30, 30)

        but = QtWidgets.QPushButton('Ln', self)
        but.setGeometry(0, 185, 30, 30)

        but = QtWidgets.QPushButton('Pln', self)
        but.setGeometry(0, 220, 30, 30)

        self.showMaximized()