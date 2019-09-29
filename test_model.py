import unittest
from model import Model
from geometry import Vector3
from redactor import RedactorWindow

class RedactorTests(unittest.TestCase):
    def test_display(self):
        model = Model()
        self.assertEqual(model.get_display_vector_on_plate_of_display(
                         Vector3(1, 0, 1)), (1, 0))
        self.assertEqual(model.get_display_vector_on_plate_of_display(
                         Vector3(12, 18, 32)), (22, 18))

    def test_matrix_of_display(self):
        model = Model()
        self.assertEqual(model.matrix_of_display[0], [0.5, 0, 0.5])
        self.assertEqual(model.matrix_of_display[1], [0, 1, 0])
