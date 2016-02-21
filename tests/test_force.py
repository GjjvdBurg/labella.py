
import unittest

from labella.force import Force, DEFAULT_OPTIONS
from labella.node import Node

class ForceTestCase(unittest.TestCase):

    def test_nodes(self):
        force = Force()

        # it should return current value when called without argument
        self.assertEqual(force.nodes(), [])
        force.nodes([1])
        self.assertEqual(force.nodes(), [1])
        # it should set value when called with an argument
        force.nodes([1])
        self.assertEqual(force.nodes(), [1])

    def test_options(self):
        force = Force()

        # it should return current value when called without an argument
        self.assertEqual(force.options, DEFAULT_OPTIONS)

        # it should set value when called with an argument
        force.set_options({'maxPos': 200})
        self.assertEqual(force.options['maxPos'], 200)
        force.set_options({'maxPos': 400, 'stubWidth': 30})
        self.assertEqual(force.options['maxPos'], 400)
        self.assertEqual(force.options['stubWidth'], 30)

    def test_compute_1(self):
        # should find location for the nodes that make them not overlap
        nodes = [
                Node(1, 50),
                Node(2, 50),
                Node(3, 50),
                Node(3, 50),
                Node(3, 50),
                Node(304, 50),
                Node(454, 50),
                Node(454, 50),
                Node(454, 50),
                Node(804, 50),
                Node(804, 70),
                Node(804, 50),
                Node(804, 50),
                Node(854, 50),
                Node(854, 50),
            ]
        force = Force()
        force.nodes(nodes)
        force.compute()

        current_pos = [n.currentPos for n in nodes]
        expected_pos = [25, 78, 131, 184, 237, 304, 401, 454, 507, 673, 736,
                799, 852, 905, 958]
        self.assertEqual(current_pos, expected_pos)

    def test_compute_2(self):
        # should respect the maxPos option
        nodes = [
                Node(1, 50),
                Node(2, 50),
                Node(3, 50),
                Node(3, 50),
                Node(3, 50),
                Node(304, 50),
                Node(454, 50),
                Node(454, 50),
                Node(454, 50),
                Node(804, 50),
                Node(804, 70),
                Node(804, 50),
                Node(804, 50),
                Node(854, 50),
                Node(854, 50),
            ]
        force = Force({'maxPos': 904})
        force.nodes(nodes)
        force.compute()

        for node in nodes:
            self.assertLessEqual(node.currentRight(), 904)

    def test_compute_3(self):
        # should respect the minPos option
        nodes = [
                Node(1, 50),
                Node(2, 50),
                Node(3, 50),
                Node(3, 50),
                Node(3, 50),
                Node(304, 50),
                Node(454, 50),
                Node(454, 50),
                Node(454, 50),
                Node(804, 50),
                Node(804, 70),
                Node(804, 50),
                Node(804, 50),
                Node(854, 50),
                Node(854, 50),
            ]
        force = Force({'minPos': 30})
        force.nodes(nodes)
        force.compute()

        for node in nodes:
            self.assertGreater(node.currentRight(), 30) # is this right?
            self.assertGreaterEqual(node.currentLeft(), 30)


if __name__ == '__main__':
    unittest.main()
