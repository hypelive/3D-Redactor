import sys
import time
from PyQt5 import QtGui, QtWidgets, QtCore  #here is matrix
import redactor
from geometry import Matrix


def main():
    application = QtWidgets.QApplication(sys.argv)
    redactor_window = redactor.RedactorWindow()
    application.exec_()


if __name__ == "__main__":
    main()