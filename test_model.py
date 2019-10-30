import unittest
from model import Model
from geometry import Vector3, Matrix
import math

class RedactorTests(unittest.TestCase):
    def test_display(self):
        model = Model()
        self.assertEqual(model.get_display_vector_on_plate_of_display(
                         Vector3(1, 0, 0)), (0, 0))
        self.assertEqual(model.get_display_vector_on_plate_of_display(
                         Vector3(0, 1, 0)), (1, 0))                 
        self.assertEqual(model.get_display_vector_on_plate_of_display(
                         Vector3(0, 0, 1)), (0, 1))
    
    def test_display_complex_vector(self):
        model = Model()
        self.assertEqual(model.get_display_vector_on_plate_of_display(
                         Vector3(1, 2, 3)), (2, 3))

    def test_matrix_of_display(self):
        model = Model()
        self.assertEqual(model.matrix_of_display[0], [0, 0, -1])
        self.assertEqual(model.matrix_of_display[1], [1, 0, 0])
        self.assertEqual(model.matrix_of_display[2], [0, 1, 0])

    def test_rotate_plate_of_display_z(self):
        model = Model()
        rotate_angle = math.pi / 2
        model.update_matrix_of_display(Matrix(3, 3, 1, 0, 0, 0,
                                              math.cos(rotate_angle),
                                              -math.sin(rotate_angle), 0,
                                              math.sin(rotate_angle),
                                              math.cos(rotate_angle)))

        self.assertTrue(math.fabs(model.matrix_of_display[0][0]) < 1e-15)
        self.assertTrue(math.fabs(model.matrix_of_display[0][1]) < 1e-15)
        self.assertTrue(math.fabs(model.matrix_of_display[0][2] + 1) < 1e-15)
        self.assertTrue(math.fabs(model.matrix_of_display[1][0]) < 1e-15)
        self.assertTrue(math.fabs(model.matrix_of_display[1][1] + 1) < 1e-15)
        self.assertTrue(math.fabs(model.matrix_of_display[1][2]) < 1e-15)
        self.assertTrue(math.fabs(model.matrix_of_display[2][0] - 1) < 1e-15)
        self.assertTrue(math.fabs(model.matrix_of_display[2][1]) < 1e-15)
        self.assertTrue(math.fabs(model.matrix_of_display[2][2]) < 1e-15)

    def test_display_model(self):
        model = Model()
        self.assertEqual(model.get_display_vector_on_plate_of_display(Vector3(1, 0, 0)), (0, 0))
        self.assertEqual(model.get_display_vector_on_plate_of_display(Vector3(0, 1, 0)), (1, 0))
        self.assertEqual(model.get_display_vector_on_plate_of_display(Vector3(0, 0, 1)), (0, 1))
        
        
        

