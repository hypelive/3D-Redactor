import unittest
import model
from geometry import Vector3

class RedactorTests(unittest.TestCase):
    def test_display(self):
        self.model = model.Model()
        normal_vector = self.model.display_plate_basis[0] * self.model.display_plate_basis[1]
        temp = -(normal_vector.x*self.model.basis[0].x + normal_vector.y*self.model.basis[0].y +
                 normal_vector.z*self.model.basis[0].z) / (normal_vector.x*normal_vector.x +
                 normal_vector.y*normal_vector.y + normal_vector.z*normal_vector.z)
        self.assertEqual(temp, 0)