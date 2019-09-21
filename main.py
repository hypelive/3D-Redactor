import sys
from PyQt5 import QtGui, QtWidgets  #here is matrix

def main():
    application = QtWidgets.QApplication(sys.argv)
    window = QtWidgets.QWidget()
    window.setGeometry(0, 0, 480, 270)  #x y wide tall
    layout = QtWidgets.QVBoxLayout()
    layout.addWidget(QtWidgets.QPushButton("choose file..."))
    layout.addWidget(QtWidgets.QLineEdit("enter the filename"))
    window.setLayout(layout)
    window.show()
    application.exec_()


if __name__ == "__main__":
    main()