
import unittest

from labella.distributor import Distributor
from labella.node import Node

class DistributorTestCase(unittest.TestCase):

    def test_computeRequiredWidth_1(self):
        options = {
                'algorithm': 'overlap',
                'layerWidth': 960,
                'density': 0.85,
                'nodeSpacing': 3,
                'stubWidth': 1
                }
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
                Node(854, 50)]
        exp_out = 812
        dist = Distributor(options)
        self.assertEqual(exp_out, dist.computeRequiredWidth(nodes))

    def test_computeRequiredWidth_2(self):
        options = {
                'algorithm': 'overlap',
                'layerWidth': 960,
                'density': 0.85,
                'nodeSpacing': 3,
                'stubWidth': 1
                }
        nodes = [
                Node(1,   100),
                Node(2,   100),
                Node(3,   100),
                Node(3,   100),
                Node(3,   100),
                Node(304, 100),
                Node(454, 100),
                Node(454, 100),
                Node(454, 100),
                Node(804, 100),
                Node(804, 100),
                Node(804, 100),
                Node(804, 100),
                Node(854, 100),
                Node(854, 100)]
        exp_out = 1542
        dist = Distributor(options)
        self.assertEqual(exp_out, dist.computeRequiredWidth(nodes))

    def test_estimatedRequiredLayers_1(self):
        options = {
                'algorithm': 'overlap',
                'layerWidth': 960,
                'density': 0.85,
                'nodeSpacing': 3,
                'stubWidth': 1
                }
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
                Node(854, 50)]
        exp_out = 1
        dist = Distributor(options)
        self.assertEqual(exp_out, dist.estimateRequiredLayers(nodes))

    def test_estimateRequiredLayers_2(self):
        options = {
                'algorithm': 'overlap',
                'layerWidth': 960,
                'density': 0.85,
                'nodeSpacing': 3,
                'stubWidth': 1
                }
        nodes = [
                Node(1,   100),
                Node(2,   100),
                Node(3,   100),
                Node(3,   100),
                Node(3,   100),
                Node(304, 100),
                Node(454, 100),
                Node(454, 100),
                Node(454, 100),
                Node(804, 100),
                Node(804, 100),
                Node(804, 100),
                Node(804, 100),
                Node(854, 100),
                Node(854, 100)]
        exp_out = 2
        dist = Distributor(options)
        self.assertEqual(exp_out, dist.estimateRequiredLayers(nodes))

    def test_estimateRequiredLayers_3(self):
        options = {
                'algorithm': 'overlap',
                'layerWidth': None,
                'density': 0.85,
                'nodeSpacing': 3,
                'stubWidth': 1
                }
        nodes = [
                Node(1,   100),
                Node(2,   100),
                Node(3,   100),
                Node(3,   100),
                Node(3,   100),
                Node(304, 100),
                Node(454, 100),
                Node(454, 100),
                Node(454, 100),
                Node(804, 100),
                Node(804, 100),
                Node(804, 100),
                Node(804, 100),
                Node(854, 100),
                Node(854, 100)]
        exp_out = 1
        dist = Distributor(options)
        self.assertEqual(exp_out, dist.estimateRequiredLayers(nodes))

    def test_countIdealOverlaps(self):
        options = {
                'algorithm': 'overlap',
                'layerWidth': 960,
                'density': 0.85,
                'nodeSpacing': 3,
                'stubWidth': 1
                }
        nodes = [
                Node(1,   100),
                Node(2,   100),
                Node(3,   100),
                Node(3,   100),
                Node(3,   100),
                Node(304, 100),
                Node(454, 100),
                Node(454, 100),
                Node(454, 100),
                Node(804, 100),
                Node(804, 100),
                Node(804, 100),
                Node(804, 100),
                Node(854, 100),
                Node(854, 100)]
        dist = Distributor(options)
        exp_out = [5, 5, 5, 5, 5, 1, 3, 3, 3, 6, 6, 6, 6, 6, 6]
        dist.countIdealOverlaps(nodes)
        for i in range(len(exp_out)):
            self.assertEqual(exp_out[i], nodes[i].overlapCount)

    def test_algorithm_simple_1(self):
        options = {
                'algorithm': 'simple',
                'layerWidth': 960,
                'density': 0.85,
                'nodeSpacing': 3,
                'stubWidth': 1
                }
        nodes = [
                Node(1,   100),  #  0
                Node(2,   100),  #  1
                Node(3,   100),  #  2
                Node(3,   100),  #  3
                Node(3,   100),  #  4
                Node(304, 100),  #  5
                Node(454, 100),  #  6
                Node(454, 100),  #  7
                Node(454, 100),  #  8
                Node(804, 100),  #  9
                Node(804, 100),  # 10
                Node(804, 100),  # 11
                Node(804, 100),  # 12
                Node(854, 100),  # 13
                Node(854, 100)]  # 14
        nodedict = {i:n for i, n in enumerate(nodes)}
        dist = Distributor(options)
        layers = dist.distribute(nodes)

        self.assertEqual(layers[0][0], nodedict[0])
        self.assertTrue(layers[0][1].isStub())
        self.assertEqual(layers[0][2], nodedict[2])
        self.assertTrue(layers[0][3].isStub())
        self.assertEqual(layers[0][4], nodedict[4])
        self.assertTrue(layers[0][5].isStub())
        self.assertEqual(layers[0][6], nodedict[6])
        self.assertTrue(layers[0][7].isStub())
        self.assertEqual(layers[0][8], nodedict[8])
        self.assertTrue(layers[0][9].isStub())
        self.assertEqual(layers[0][10], nodedict[10])
        self.assertTrue(layers[0][11].isStub())
        self.assertEqual(layers[0][12], nodedict[12])
        self.assertTrue(layers[0][13].isStub())
        self.assertEqual(layers[0][14], nodedict[14])

        self.assertEqual(layers[1][0], nodedict[1])
        self.assertEqual(layers[1][1], nodedict[3])
        self.assertEqual(layers[1][2], nodedict[5])
        self.assertEqual(layers[1][3], nodedict[7])
        self.assertEqual(layers[1][4], nodedict[9])
        self.assertEqual(layers[1][5], nodedict[11])
        self.assertEqual(layers[1][6], nodedict[13])

    def test_algorithm_simple_2(self):
        options = {
                'algorithm': 'simple',
                'layerWidth': 960,
                'density': 0.85,
                'nodeSpacing': 3,
                'stubWidth': 1
                }
        nodes = [
                Node(1,   100),  #  0
                Node(2,   200),  #  1
                Node(3,   100),  #  2
                Node(3,   200),  #  3
                Node(3,   50),  #  4
                Node(304, 200),  #  5
                Node(454, 50),  #  6
                Node(454, 200),  #  7
                Node(454, 90),  #  8
                Node(804, 200),  #  9
                Node(804, 90),  # 10
                Node(804, 200),  # 11
                Node(804, 50),  # 12
                Node(854, 200),  # 13
                Node(854, 70)]  # 14
        nodedict = {i:n for i, n in enumerate(nodes)}
        dist = Distributor(options)
        layers = dist.distribute(nodes)

        self.assertEqual(layers[0][0], nodedict[0])
        self.assertTrue(layers[0][1].isStub())
        self.assertTrue(layers[0][2].isStub())
        self.assertEqual(layers[0][3], nodedict[3])
        self.assertTrue(layers[0][4].isStub())
        self.assertTrue(layers[0][5].isStub())
        self.assertEqual(layers[0][6], nodedict[6])
        self.assertTrue(layers[0][7].isStub())
        self.assertTrue(layers[0][8].isStub())
        self.assertEqual(layers[0][9], nodedict[9])
        self.assertTrue(layers[0][10].isStub())
        self.assertTrue(layers[0][11].isStub())
        self.assertEqual(layers[0][12], nodedict[12])
        self.assertTrue(layers[0][13].isStub())
        self.assertTrue(layers[0][14].isStub())

        self.assertEqual(layers[1][0], nodedict[1])
        self.assertTrue(layers[1][1].isStub())
        self.assertEqual(layers[1][2], nodedict[4])
        self.assertTrue(layers[1][3].isStub())
        self.assertEqual(layers[1][4], nodedict[7])
        self.assertTrue(layers[1][5].isStub())
        self.assertEqual(layers[1][6], nodedict[10])
        self.assertTrue(layers[1][7].isStub())
        self.assertEqual(layers[1][8], nodedict[13])

        self.assertEqual(layers[2][0], nodedict[2])
        self.assertEqual(layers[2][1], nodedict[5])
        self.assertEqual(layers[2][2], nodedict[8])
        self.assertEqual(layers[2][3], nodedict[11])
        self.assertEqual(layers[2][4], nodedict[14])

    def test_algorithm_overlap_1(self):
        options = {
                'algorithm': 'overlap',
                'layerWidth': 960,
                'density': 0.85,
                'nodeSpacing': 3,
                'stubWidth': 1
                }
        nodes = [
                Node(1,   100),  #  0
                Node(2,   100),  #  1
                Node(3,   99),  #  2
                Node(3,   100),  #  3
                Node(3,   101),  #  4
                Node(304, 100),  #  5
                Node(454, 99),  #  6
                Node(454, 100),  #  7
                Node(454, 101),  #  8
                Node(804, 98),  #  9
                Node(804, 99),  # 10
                Node(804, 100),  # 11
                Node(804, 101),  # 12
                Node(854, 99),  # 13
                Node(854, 100)]  # 14
        nodedict = {i:n for i, n in enumerate(nodes)}
        dist = Distributor(options)
        layers = dist.distribute(nodes)

        self.assertEqual(layers[0][0], nodedict[7])
        self.assertEqual(layers[0][1], nodedict[8])
        self.assertEqual(layers[0][2], nodedict[3])
        self.assertEqual(layers[0][3], nodedict[4])
        self.assertEqual(layers[0][4], nodedict[13])
        self.assertEqual(layers[0][5], nodedict[14])
        self.assertEqual(layers[0][6], nodedict[5])
        self.assertTrue(layers[0][7].isStub())
        self.assertTrue(layers[0][8].isStub())
        self.assertTrue(layers[0][9].isStub())
        self.assertTrue(layers[0][10].isStub())
        self.assertTrue(layers[0][11].isStub())
        self.assertTrue(layers[0][12].isStub())
        self.assertTrue(layers[0][13].isStub())
        self.assertTrue(layers[0][14].isStub())

        self.assertEqual(layers[1][0], nodedict[10])
        self.assertEqual(layers[1][1], nodedict[11])
        self.assertEqual(layers[1][2], nodedict[12])
        self.assertEqual(layers[1][3], nodedict[0])
        self.assertEqual(layers[1][4], nodedict[1])
        self.assertEqual(layers[1][5], nodedict[2])
        self.assertEqual(layers[1][6], nodedict[6])
        self.assertTrue(layers[1][7].isStub())

        self.assertEqual(layers[2][0], nodedict[9])

    def test_algorithm_overlap_2(self):
        options = {
                'algorithm': 'overlap',
                'layerWidth': 960,
                'density': 0.85,
                'nodeSpacing': 3,
                'stubWidth': 1
                }
        nodes = [
                Node(1,   100),  #  0
                Node(2,   200),  #  1
                Node(3,   100),  #  2
                Node(3,   200),  #  3
                Node(3,   50),   #  4
                Node(304, 200),  #  5
                Node(454, 50),   #  6
                Node(454, 200),  #  7
                Node(454, 90),   #  8
                Node(804, 200),  #  9
                Node(804, 90),   # 10
                Node(804, 200),  # 11
                Node(804, 50),   # 12
                Node(854, 200),  # 13
                Node(854, 70)]   # 14
        nodedict = {i:n for i, n in enumerate(nodes)}
        dist = Distributor(options)
        layers = dist.distribute(nodes)

        self.assertEqual(layers[0][0], nodedict[4])
        self.assertEqual(layers[0][1], nodedict[13])
        self.assertEqual(layers[0][2], nodedict[14])
        self.assertEqual(layers[0][3], nodedict[6])
        self.assertEqual(layers[0][4], nodedict[8])
        self.assertEqual(layers[0][5], nodedict[5])
        self.assertTrue(layers[0][6].isStub())
        self.assertTrue(layers[0][7].isStub())
        self.assertTrue(layers[0][8].isStub())
        self.assertTrue(layers[0][9].isStub())
        self.assertTrue(layers[0][10].isStub())
        self.assertTrue(layers[0][11].isStub())
        self.assertTrue(layers[0][12].isStub())
        self.assertTrue(layers[0][13].isStub())
        self.assertTrue(layers[0][14].isStub())

        self.assertEqual(layers[1][0], nodedict[11])
        self.assertEqual(layers[1][1], nodedict[12])
        self.assertEqual(layers[1][2], nodedict[2])
        self.assertEqual(layers[1][3], nodedict[3])
        self.assertEqual(layers[1][4], nodedict[7])
        self.assertTrue(layers[1][5].isStub())
        self.assertTrue(layers[1][6].isStub())
        self.assertTrue(layers[1][7].isStub())
        self.assertTrue(layers[1][8].isStub())

        self.assertEqual(layers[2][0], nodedict[9])
        self.assertEqual(layers[2][1], nodedict[0])
        self.assertEqual(layers[2][2], nodedict[1])
        self.assertEqual(layers[2][3], nodedict[10])


if __name__ == '__main__':
    unittest.main()
