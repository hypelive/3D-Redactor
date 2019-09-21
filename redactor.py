import sys
from PyQt5 import QtGui, QtWidgets, QtCore  #here is matrix

class RedactorWindow(QtWidgets.QWidget):

    def __init__(self):
        super().__init__()
        self.initGUI()

    def initGUI(self):
        self.setGeometry(0, 0, 480, 270)  #x y wide tall
        icon = QtGui.QIcon('textures\\icon.png')
        self.setWindowIcon(icon)
        self.setWindowTitle('Black Box redactor')
        but = QtWidgets.QPushButton('123', self)
        but.setGeometry(5, 5, 100, 20)
        self.showMaximized()