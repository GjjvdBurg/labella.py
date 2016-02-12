
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

    def test_moveToIdealPosition(self):
        n = Node(10, 10)
        n.currentPos = 20
        self.assertNotEqual(n.currentPos, n.idealPos)
        n.moveToIdealPosition()
        self.assertEqual(n.currentPos, n.idealPos)

    def test_displacement(self):
        n = Node(10, 10)
        self.assertEqual(n.displacement(), 0)
        n.currentPos = 20
        self.assertEqual(n.displacement(), -10)
        n.currentPos = 0
        self.assertEqual(n.displacement(), 10)

    def test_overlapWithNode(self):
        n1 = Node(10, 10)
        n2 = Node(19, 10)
        n3 = Node(20, 10)
        n4 = Node(21, 10)
        n5 = Node(22, 10)
        self.assertTrue(n1.overlapWithNode(n2))
        self.assertFalse(n1.overlapWithNode(n3))
        self.assertFalse(n1.overlapWithNode(n4))

        self.assertTrue(n1.overlapWithNode(n2, 2))
        self.assertTrue(n1.overlapWithNode(n3, 2))
        self.assertTrue(n1.overlapWithNode(n4, 2))
        self.assertFalse(n1.overlapWithNode(n5, 2))

    def test_overlapWithPoint(self):
        n1 = Node(10, 10)
        self.assertFalse(n1.overlapWithPoint(4))
        self.assertTrue(n1.overlapWithPoint(5))
        self.assertTrue(n1.overlapWithPoint(10))
        self.assertTrue(n1.overlapWithPoint(15))
        self.assertFalse(n1.overlapWithPoint(16))

    def test_positionBefore(self):
        n1 = Node(10, 10)
        n2 = Node(19, 10)
        self.assertEqual(n1.positionBefore(n2), 9)
        self.assertEqual(n1.positionBefore(n2, 2), 7)

    def test_positionAfter(self):
        n1 = Node(10, 10)
        n2 = Node(19, 10)
        self.assertEqual(n1.positionAfter(n2), 29)
        self.assertEqual(n1.positionAfter(n2, 2), 31)

    def test_currentRight(self):
        n1 = Node(10, 10)
        n1.currentPos = 20
        self.assertEqual(n1.currentRight(), 25)

    def test_currentLeft(self):
        n1 = Node(10, 10)
        n1.currentPos = 20
        self.assertEqual(n1.currentLeft(), 15)

    def test_idealRight(self):
        n1 = Node(10, 10)
        self.assertEqual(n1.idealRight(), 15)

    def test_idealLeft(self):
        n1 = Node(10, 10)
        self.assertEqual(n1.idealLeft(), 5)

    def test_createStub(self):
        n1 = Node(10, 10)
        stub = n1.createStub(5)
        self.assertIsNotNone(stub)
        self.assertEqual(stub.width, 5)
        self.assertEqual(n1.idealPos, stub.idealPos)
        self.assertEqual(n1.data, stub.data)

    def test_removeStub(self):
        n1 = Node(10, 10)
        stub = n1.createStub(5)
        n1.removeStub()
        self.assertIsNone(n1.parent)
        self.assertIsNone(stub.child)

    def test_isStub(self):
        n1 = Node(10, 10)
        stub = n1.createStub(5)
        self.assertFalse(n1.isStub())
        self.assertTrue(stub.isStub())

    def test_getPathToRoot(self):
        n1 = Node(10, 10)
        self.assertEqual(n1.getPathToRoot(), [n1])
        n2 = n1.createStub(5)
        n3 = n2.createStub(5)
        self.assertEqual(n1.getPathToRoot(), [n1, n2, n3])

    def test_getPathFromRoot(self):
        n1 = Node(10, 10)
        self.assertEqual(n1.getPathFromRoot(), [n1])
        n2 = n1.createStub(5)
        n3 = n2.createStub(5)
        self.assertEqual(n1.getPathFromRoot(), [n3, n2, n1])

    def test_getPathToRootLength(self):
        n4 = Node(854, 50)
        n4.currentPos = 800
        stub4 = n4.createStub()
        stub4.currentPos = 700
        self.assertEqual(n4.getPathToRootLength(), 254)

    def test_getRoot(self):
        n1 = Node(10, 10)
        self.assertEqual(n1.getRoot(), n1)
        n2 = n1.createStub(5)
        self.assertEqual(n1.getRoot(), n2)
        n3 = n2.createStub(5)
        self.assertEqual(n1.getRoot(), n3)

    def test_getLayerIndex(self):
        n1 = Node(10, 10)
        self.assertEqual(n1.getLayerIndex(), 0)
        n1.layerIndex = 10
        self.assertEqual(n1.getLayerIndex(), 10)

    def test_clone(self):
        n1 = Node(10, 11, 'a')
        n1.currentPos = 20
        n1.layerIndex = 3
        n2 = n1.clone()
        self.assertEqual(n2.idealPos, 10)
        self.assertEqual(n2.width, 11)
        self.assertEqual(n2.data, 'a')
        self.assertEqual(n2.currentPos, 20)
        self.assertEqual(n2.layerIndex, 3)

if __name__ == '__main__':
    unittest.main()
