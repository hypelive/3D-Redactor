import unittest
from model import Model
from geometry import Vector3, Matrix
from redactor import RedactorWindow
import math

class RedactorTests(unittest.TestCase):
    def test_display(self):
        model = Model()
        self.assertEqual(model.get_display_vector_on_plate_of_display(
                         Vector3(1, 0, 0)), (1, 0))
        self.assertEqual(model.get_display_vector_on_plate_of_display(
                         Vector3(0, 1, 0)), (0, 1))                 
        self.assertEqual(model.get_display_vector_on_plate_of_display(
                         Vector3(12, 18, 32)), (12, 18))

    def test_matrix_of_display(self):
        model = Model()
        self.assertEqual(model.matrix_of_display[0], [1, 0, 0])
        self.assertEqual(model.matrix_of_display[1], [0, 1, 0])

    def test_rotate_plate_of_display_x(self):
        model = Model()
        rotate_angle = math.pi / 2
        model.update_matrix_of_display(Matrix(3, 3, math.cos(rotate_angle),
                                       -math.sin(rotate_angle), 0,
                                       math.sin(rotate_angle),
                                       math.cos(rotate_angle),
                                       0, 0, 0, 1))
        self.assertTrue(math.fabs(model.display_plate_basis[0].x) < 1e-10)
        self.assertTrue(math.fabs(model.display_plate_basis[0].y - 1) < 1e-10)
        self.assertTrue(math.fabs(model.display_plate_basis[0].x) < 1e-10)
        self.assertTrue(math.fabs(model.display_plate_basis[1].x + 1) < 1e-10)
        self.assertTrue(math.fabs(model.display_plate_basis[0].x) < 1e-10)
        self.assertTrue(math.fabs(model.display_plate_basis[0].x) < 1e-10)

    def test_rotate_plate_of_display_z(self):
        model = Model()
        rotate_angle = math.pi / 2
        model.update_matrix_of_display(Matrix(3, 3, 1, 0, 0, 0,
                                              math.cos(rotate_angle),
                                              -math.sin(rotate_angle), 0,
                                              math.sin(rotate_angle),
                                              math.cos(rotate_angle)))
        self.assertTrue(math.fabs(model.display_plate_basis[0].x - 1) < 1e-10)
        self.assertTrue(math.fabs(model.display_plate_basis[0].y) < 1e-10)
        self.assertTrue(math.fabs(model.display_plate_basis[0].z) < 1e-10)
        self.assertTrue(math.fabs(model.display_plate_basis[1].x) < 1e-10)
        self.assertTrue(math.fabs(model.display_plate_basis[1].y) < 1e-10)
        self.assertTrue(math.fabs(model.display_plate_basis[1].z - 1) < 1e-10)

        self.assertEqual(model.matrix_of_display[0], [1, 0, 0])
        self.assertEqual(model.matrix_of_display[1], [0, 0, 1])
        
        

