
import unittest

from labella.node import Node

class NodeTestCase(unittest.TestCase):

    def test_no_overlap(self):
        n1 = Node(10, 10)
        n2 = Node(30, 10)
        self.assertEqual(n1.distanceFrom(n2), 10)

    def test_touching(self):
        n1 = Node(10, 10)
        n2 = Node(20, 10)
        self.assertEqual(n1.distanceFrom(n2), 0)

    def test_overlap(self):
        n1 = Node(10, 10)
        n2 = Node(10, 10)
        self.assertEqual(n1.distanceFrom(n2), -10)

if __name__ == '__main__':
    unittest.main()
