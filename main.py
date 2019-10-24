import sys
from PyQt5 import QtWidgets
import redactor


def main():
    application = QtWidgets.QApplication(sys.argv)
    redactor_window = redactor.RedactorWindow()
    redactor_window.setFixedSize(1200, 625)
    redactor_window.show()
    application.exec_()


if __name__ == "__main__":
    main()
