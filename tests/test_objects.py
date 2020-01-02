import unittest
import sys
import os
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                             os.path.pardir))
from source.objects import Point, Line, Polygon, Sphere
from source.geometry import Vector3


class ObjectTests(unittest.TestCase):
    def test_point_to_vector(self):
        self.assertEqual(Point(12, 4, 3).to_vector3(), Vector3(12, 4, 3))

    def test_get_guide_vector(self):
        self.assertEqual(Line(Point(12, 3, 4),
                              Point(0, 0, 4)).get_guide_vector(),
                         Vector3(-12, -3, 0))

    def test_is_inside_line(self):
        line = Line(Point(0, 0, 12), Point(3, 4, 12))
        self.assertFalse(line.is_inside_line(None))
        self.assertFalse(line.is_inside_line(Point(0, 0, 0)))
        self.assertTrue(line.is_inside_line(Point(1, 4/3, 12)))

    def test_get_normal_vector(self):
        vector = Polygon([Point(0, 1, 0), Point(1, 0, 0),
                          Point(0, 0, 1)]).get_normal_vector()
        self.assertEqual(vector.x, -1)
        self.assertEqual(vector.y, -1)
        self.assertEqual(vector.z, -1)
