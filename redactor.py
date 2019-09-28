import sys
from PyQt5 import QtGui, QtWidgets, QtCore #here is matrix,  https://www.learnpyqt.com/courses/custom-widgets/bitmap-graphics/
import model
from geometry import Matrix, Vector3

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

    def get_display_vector_on_plate_of_display(self, vector):
        normal_vector = self.model.display_plate_basis[0] * self.model.display_plate_basis[1]
        temp = -(normal_vector.x*vector.x + normal_vector.y*vector.y +
                 normal_vector.z*vector.z) / (normal_vector.x*normal_vector.x +
                 normal_vector.y*normal_vector.y + normal_vector.z*normal_vector.z)
        displayed_vector = Vector3(normal_vector.x*temp + vector.x,
                                   normal_vector.y*temp + vector.y,
                                   normal_vector.z*temp + vector.z)
        matrix = Matrix(3, 3, self.model.display_plate_basis[0].x, self.model.display_plate_basis[2].x,
                        displayed_vector.x, self.model.display_plate_basis[0].y,
                        self.model.display_plate_basis[1].y, displayed_vector.y,
                        self.model.display_plate_basis[0].z, self.model.display_plate_basis[0].z,
                        displayed_vector.z)
        return matrix.solve_matrix_by_gauss()

    def get_matrix_of_display(self):
        a = self.get_display_vector_on_plate_of_display(self.model.basis[0])
        b = self.get_display_vector_on_plate_of_display(self.model.basis[1])
        c = self.get_display_vector_on_plate_of_display(self.model.basis[2])
        self.matrix_of_display = Matrix(2, 3, a[0], b[0], c[0], a[1], b[1], c[1]) 

        return self.matrix_of_display
        

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