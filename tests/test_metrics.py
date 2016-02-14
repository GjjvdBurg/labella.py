
import unittest

from labella import metrics
from labella.node import Node

class MetricsTestCase(unittest.TestCase):

    def test_displacement(self):
        nodes = [
                Node(1, 50),
                Node(2, 50),
                Node(804, 50),
                Node(854, 50)
                ]
        # should return 0 if the input is empty
        self.assertEqual(metrics.displacement([]), 0)
        # should return sum of the displacements
        self.assertEqual(metrics.displacement(nodes), 0)
        nodes[0].currentPos = 10
        nodes[1].currentPos = 10
        self.assertEqual(metrics.displacement([nodes]), 17.0/4.0)

    def test_pathLength(self):
        n1 = Node(1, 50)
        n1.currentPos = 20
        n2 = Node(2, 50)
        n3 = Node(804, 50)
        stub = n3.createStub()
        n3.currentPos = 810
        n4 = Node(854, 50)
        n4.currentPos = 800
        stub4 = n4.createStub()
        stub4.currentPos = 700
        stub4_2 = stub4.createStub()

        # should return 0 if the input is empty
        self.assertEqual(metrics.pathLength([]), 0)
        # should return sum of the displacements from leaves to stubs up to 
        # root
        self.assertEqual(metrics.pathLength([n1]), 19)
        self.assertEqual(metrics.pathLength([n2]), 0)
        self.assertEqual(metrics.pathLength([n3]), 6)
        self.assertEqual(metrics.pathLength([n4, stub4, stub4_2]), 254)
        self.assertEqual(metrics.pathLength([[n1, n2, n3, stub4_2], [stub4], 
            [n4]]), 279/4)

    def test_overflowSpace(self):
        nodes = [
                Node(1, 50),
                Node(-30, 50),
                Node(804, 50),
                Node(854, 50)
                ]
        # should return 0 if both minPos and maxPos are not set
        self.assertEqual(metrics.overflowSpace(nodes), 0)
        # should return the amount of pixels that exceed boundary
        self.assertEqual(metrics.overflowSpace(nodes, 0), 74)
        self.assertEqual(metrics.overflowSpace(nodes, None, 800), 79)
        self.assertEqual(metrics.overflowSpace(nodes, 0, 800), 74+79)

    def test_overDensitySpace(self):
        nodes = [
                Node(1, 50),
                Node(2, 50),
                Node(804, 50),
                Node(854, 50)
                ]
        # should return 0 if the density or layerWidth is not defined
        self.assertEqual(metrics.overDensitySpace([]), 0)
        self.assertEqual(metrics.overDensitySpace(nodes), 0)
        self.assertEqual(metrics.overDensitySpace(nodes, 0.75), 0)
        self.assertEqual(metrics.overDensitySpace(nodes, None, 1000), 0)
        # should return the amount of pixels exceeding specified density
        self.assertEqual(metrics.overDensitySpace(nodes, 0.75, 1000), 0)
        self.assertEqual(metrics.overDensitySpace(nodes, 0.1, 1000), 100)
        self.assertEqual(metrics.overDensitySpace([nodes, nodes], 0.1, 1000), 
                200)

    def test_overlapCount(self):
        nodes = [
                Node(0, 50),
                Node(50, 50),
                Node(800, 50),
                Node(801, 50)
                ]
        # should return 0 if the input is empty
        self.assertEqual(metrics.overlapCount([]), 0)
        # should return number of times nodes on the same layer overlaps
        self.assertEqual(metrics.overlapCount(nodes), 1)
        self.assertEqual(metrics.overlapCount([nodes, nodes]), 2)
        # should take buffer into consideration
        self.assertEqual(metrics.overlapCount(nodes, 2), 2)
        self.assertEqual(metrics.overlapCount([nodes, nodes], 3), 4)

    def test_overlapSpace(self):
        nodes = [
                Node(0, 50),
                Node(50, 50),
                Node(800, 50),
                Node(801, 50)
                ]
        # should return 0 if the input is empty
        self.assertEqual(metrics.overlapSpace([]), 0)
        # should return space that nodes on the same layer overlaps on average
        self.assertEqual(metrics.overlapSpace(nodes), 49/4)
        self.assertEqual(metrics.overlapSpace([nodes, nodes]), 49*2/8)

    def test_weightedAllocation(self):
        nodes = [
                Node(0, 50),
                Node(50, 50),
                Node(800, 50),
                Node(801, 50)
                ]
        # should return 0 if the input is empty
        self.assertEqual(metrics.weightedAllocation([]), 0)
        # should return 0 if the output is in one row
        self.assertEqual(metrics.weightedAllocation(nodes), 0)
        # should return number of nodes weighted by layer index
        self.assertEqual(metrics.weightedAllocation([nodes, nodes]), 4)
        self.assertEqual(metrics.weightedAllocation([nodes, nodes, nodes]), 
                4+8)

    def test_weightedAllocatedSpace(self):
        nodes = [
                Node(0, 50),
                Node(50, 50),
                Node(800, 50),
                Node(801, 50)
                ]
        # should return 0 if the input is empty
        self.assertEqual(metrics.weightedAllocatedSpace([]), 0)
        # should return 0 if the output is in one row
        self.assertEqual(metrics.weightedAllocatedSpace(nodes), 0)
        # should return width of thed nodes weighted by layer index
        self.assertEqual(metrics.weightedAllocatedSpace([nodes, nodes]), 200)
        self.assertEqual(metrics.weightedAllocatedSpace([nodes, nodes, 
            nodes]), 200 + 400)

if __name__ == '__main__':
    unittest.main()
