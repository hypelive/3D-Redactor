import unittest
import sys
import os
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                             os.path.pardir))
from source.geometry import Vector3, Matrix  # qt


class GeometryTests(unittest.TestCase):
    def test_vector_create(self):
        vector = Vector3(1, 2, 3)
        self.assertEqual(vector.x, 1)
        self.assertEqual(vector.y, 2)
        self.assertEqual(vector.z, 3)

    def test_vector_multiply(self):
        vector1 = Vector3(1, 0, 0)
        vector2 = Vector3(0, 1, 0)
        self.assertEqual(vector1 * vector2, Vector3(0, 0, 1))
        vector1 = Vector3(1, 2, 3)
        vector2 = Vector3(2, 3, 1)
        self.assertEqual(vector1 * vector2, Vector3(-7, 5, -1))
        vector1 = Vector3(1, 2, 3)
        mult = 12
        self.assertEqual(vector1 * mult, Vector3(12, 24, 36))

    def test_matrix_create(self):
        matrix = Matrix(2, 2, 1, 1, 0, 0)
        self.assertEqual(matrix[0], [1, 1])
        self.assertEqual(matrix[1], [0, 0])

    def test_matrix_multiply(self):
        self.assertEqual((Matrix(2, 3, 1, 0, 0, 0, 1, 0) *
                          Matrix(3, 1, 1, 0, 0)).to_tuple(), (1, 0))
        self.assertEqual((Matrix(3, 3, 1, 2, 3, 2, 3, 1, 4, 1, 2) *
                          Matrix(3, 2, 2, 2, 3, 1, 1, 2)).to_tuple(),
                         (11, 10, 14, 9, 13, 13))
        self.assertEqual((Matrix(3, 3, 1, 0, 0, 0, 0, -1, 0, 1, 0) *
                          Matrix(3, 3, 0, 0, -1, 1, 0, 0, 0, 1, 0)
                          ).to_tuple(),
                         (0, 0, -1, 0, -1, 0, 1, 0, 0))

    def test_matrix_transpose(self):
        self.assertEqual(Matrix(2, 2, 1, 0, 1, 1).transpose().to_tuple(),
                         (1, 1, 0, 1))
        self.assertEqual(Matrix(3, 3, 1, 4, 1, 2, 2, 7,
                                13, 5, 3).transpose().to_tuple(),
                         (1, 2, 13, 4, 2, 5, 1, 7, 3))

    def test_distance_vector(self):
        self.assertAlmostEqual(Vector3.distance(Vector3(0, 0, 0),
                                                Vector3(12, 13, 14)),
                               22.5610283, delta=1e-5)
