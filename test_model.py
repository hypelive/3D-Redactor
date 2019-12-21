import unittest
from model import Model
from geometry import Vector3, Matrix  # qt
import math


class RedactorTests(unittest.TestCase):
    def test_display(self):
        model = Model()
        model._set_display_basis([Vector3(0, 1, 0), Vector3(0, 0, 1),
                                  Vector3(-1, 0, 0)])
        self.assertEqual(model.display_vector(
                         Vector3(1, 0, 0)), (0, 0, -1))
        self.assertEqual(model.display_vector(
                         Vector3(0, 1, 0)), (1, 0, 0))
        self.assertEqual(model.display_vector(
                         Vector3(0, 0, 1)), (0, 1, 0))

    def test_display_complex_vector(self):
        model = Model()
        model._set_display_basis([Vector3(0, 1, 0), Vector3(0, 0, 1),
                                  Vector3(-1, 0, 0)])
        self.assertEqual(model.display_vector(
                         Vector3(1, 2, 3)), (2, 3, -1))

    def test_matrix_of_display(self):
        model = Model()
        model._set_display_basis([Vector3(0, 1, 0), Vector3(0, 0, 1),
                                  Vector3(-1, 0, 0)])
        self.assertEqual(model.matrix_of_display.transpose()[0], [0, 0, -1])
        self.assertEqual(model.matrix_of_display.transpose()[1], [1, 0, 0])
        self.assertEqual(model.matrix_of_display.transpose()[2], [0, 1, 0])

    def test_rotate_plate_of_display_z(self):
        model = Model()
        model._set_display_basis([Vector3(0, 1, 0), Vector3(0, 0, 1),
                                  Vector3(-1, 0, 0)])
        rotate_angle = math.pi / 2
        model.update_display_matrix(Matrix(3, 3, 1, 0, 0, 0,
                                           math.cos(rotate_angle),
                                           -math.sin(rotate_angle), 0,
                                           math.sin(rotate_angle),
                                           math.cos(rotate_angle)))

        self.assertAlmostEqual(model.matrix_of_display.transpose()[0][0],
                               0.0, delta=1e-15)
        self.assertAlmostEqual(model.matrix_of_display.transpose()[0][1],
                               0.0, delta=1e-15)
        self.assertAlmostEqual(model.matrix_of_display.transpose()[0][2],
                               -1.0, delta=1e-15)
        self.assertAlmostEqual(model.matrix_of_display.transpose()[1][0],
                               0.0, delta=1e-15)
        self.assertAlmostEqual(model.matrix_of_display.transpose()[1][1],
                               -1.0, delta=1e-15)
        self.assertAlmostEqual(model.matrix_of_display.transpose()[1][2],
                               0.0, delta=1e-15)
        self.assertAlmostEqual(model.matrix_of_display.transpose()[2][0],
                               1.0, delta=1e-15)
        self.assertAlmostEqual(model.matrix_of_display.transpose()[2][1],
                               0.0, delta=1e-15)
        self.assertAlmostEqual(0, model.matrix_of_display.transpose()[2][2],
                               delta=1e-15)

    def test_display_model(self):
        model = Model()
        model._set_display_basis([Vector3(0, 1, 0), Vector3(0, 0, 1),
                                  Vector3(-1, 0, 0)])
        self.assertEqual(model.display_vector(
            Vector3(1, 0, 0)), (0, 0, -1))
        self.assertEqual(model.display_vector(
            Vector3(0, 1, 0)), (1, 0, 0))
        self.assertEqual(model.display_vector(
            Vector3(0, 0, 1)), (0, 1, 0))

    def test_undisplay_vector(self):
        model = Model()
        model._set_display_basis([Vector3(0, 1, 0), Vector3(0, 0, 1),
                                  Vector3(-1, 0, 0)])
        self.assertEqual(model.undisplay_vector(
                         Vector3(0, 0, -1)), (1, 0, 0))
        self.assertEqual(model.undisplay_vector(
                         Vector3(1, 0, 0)), (0, 1, 0))
        self.assertEqual(model.undisplay_vector(
                         Vector3(0, 1, 0)), (0, 0, 1))

    def test_undisplay_complex_vector(self):
        model = Model()
        model._set_display_basis([Vector3(0, 1, 0), Vector3(0, 0, 1),
                                  Vector3(-1, 0, 0)])
        self.assertEqual(model.undisplay_vector(
                         Vector3(2, 3, -1)), (1, 2, 3))