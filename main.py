import sys
from PyQt5 import QtWidgets
import redactor


def main():
    application = QtWidgets.QApplication(sys.argv)
    redactor_window = redactor.RedactorWindow()
    redactor_window.setMaximumSize(redactor.RESOLUTION[0],
                                   redactor.RESOLUTION[1])
    redactor_window.show()
    application.exec_()


if __name__ == "__main__":
    main()
