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

        self.assertTrue(
            math.fabs(model.matrix_of_display.transpose()[0][0]) < 1e-15)
        self.assertTrue(
            math.fabs(model.matrix_of_display.transpose()[0][1]) < 1e-15)
        self.assertTrue(
            math.fabs(model.matrix_of_display.transpose()[0][2] + 1) < 1e-15)
        self.assertTrue(
            math.fabs(model.matrix_of_display.transpose()[1][0]) < 1e-15)
        self.assertTrue(
            math.fabs(model.matrix_of_display.transpose()[1][1] + 1) < 1e-15)
        self.assertTrue(
            math.fabs(model.matrix_of_display.transpose()[1][2]) < 1e-15)
        self.assertTrue(
            math.fabs(model.matrix_of_display.transpose()[2][0] - 1) < 1e-15)
        self.assertTrue(
            math.fabs(model.matrix_of_display.transpose()[2][1]) < 1e-15)
        self.assertTrue(
            math.fabs(model.matrix_of_display.transpose()[2][2]) < 1e-15)

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

    @unittest.skip
    def test_display_in_perspective_basis(self):
        model = Model()
        model.is_perspective = True
        model._set_display_basis([Vector3(0, 0, 1), Vector3(0, 1, 0),
                                  Vector3(-1, 0, 0)])

        c = model.get_display_on_display_plate(model.basis[0])
        self.assertEqual(c.x, 0)
        self.assertEqual(c.y, 0)
        self.assertEqual(c.z, 0)

        a = model.get_display_on_display_plate(model.basis[2])
        self.assertAlmostEqual(a.x, 0.3, delta=1e-10)
        self.assertEqual(a.y, 0)
        self.assertEqual(a.z, 0)

        b = model.get_display_on_display_plate(model.basis[1])
        self.assertEqual(b.x, 0)
        self.assertAlmostEqual(b.y, 0.3, delta=1e-10)
        self.assertEqual(b.z, 0)

    @unittest.skip
    def test_display_in_perspective(self):
        model = Model()
        model.is_perspective = True
        model._set_display_basis([Vector3(0, 0, 1), Vector3(0, 1, 0),
                                  Vector3(-1, 0, 0)])

        a = model.get_display_on_display_plate(Vector3(0, 1, 1))
        self.assertAlmostEqual(a.x, 0.3, delta=1e-10)
        self.assertAlmostEqual(a.y, 0.3, delta=1e-10)
        self.assertEqual(a.z, 0)

    @unittest.skip
    def test_display_with_matrix(self):
        model = Model()
        model.is_perspective = True
        model._set_display_basis([Vector3(0, 0, 1), Vector3(0, 1, 0),
                                  Vector3(-1, 0, 0)])

        a = model.display_vector(Vector3(0, 1, 1))
        self.assertAlmostEqual(a[0], 0, delta=1e-10)
        self.assertAlmostEqual(a[1], 0.3, delta=1e-10)
        self.assertAlmostEqual(a[2], 0, delta=1e-10)
