
import unittest

from labella.scale import LinearScale

class LinearScaleTestCase(unittest.TestCase):

    def test_domain_1(self):
        # defaults to [0, 1]
        x = LinearScale()
        self.assertEqual(x.domain(), [0, 1])
        self.assertAlmostEqual(x(0.5), 0.5)

    def test_range_1(self):
        # defaults to [0, 1]
        x = LinearScale()
        self.assertEqual(x.range(), [0, 1])
        self.assertAlmostEqual(x.invert(0.5), 0.5)

    def test_clamp_1(self):
        # defaults to false
        x = LinearScale()
        self.assertFalse(x.clamp())
        self.assertAlmostEqual(x(-0.5), -0.5)
        self.assertAlmostEqual(x(1.5), 1.5)

    def test_clamp_2(self):
        # can clamp to domain
        x = LinearScale().clamp(True)
        self.assertAlmostEqual(x(-0.5), 0)
        self.assertAlmostEqual(x(0.5), 0.5)
        self.assertAlmostEqual(x(1.5), 1)

        x = LinearScale().domain([1, 0]).clamp(True)
        self.assertAlmostEqual(x(-0.5), 1)
        self.assertAlmostEqual(x(0.5), 0.5)
        self.assertAlmostEqual(x(1.5), 0)

    def test_clamp_3(self):
        # can clamp to the range
        x = LinearScale().clamp(True)
        self.assertAlmostEqual(x.invert(-0.5), 0)
        self.assertAlmostEqual(x.invert(0.5), 0.5)
        self.assertAlmostEqual(x.invert(1.5), 1)

        x = LinearScale().range([1, 0]).clamp(True)
        self.assertAlmostEqual(x.invert(-0.5), 1)
        self.assertAlmostEqual(x.invert(0.5), 0.5)
        self.assertAlmostEqual(x.invert(1.5), 0)

    def test_map(self):
        # maps a number to a number
        x = LinearScale().domain([1, 2])
        self.assertAlmostEqual(x(0.5), -0.5)
        self.assertAlmostEqual(x(1), 0)
        self.assertAlmostEqual(x(1.5), 0.5)
        self.assertAlmostEqual(x(2), 1)
        self.assertAlmostEqual(x(2.5), 1.5)

    def test_invert_1(self):
        # maps a number to a number
        x = LinearScale().range([1, 2])
        self.assertAlmostEqual(x.invert(0.5), -0.5)
        self.assertAlmostEqual(x.invert(1), 0)
        self.assertAlmostEqual(x.invert(1.5), 0.5)
        self.assertAlmostEqual(x.invert(2), 1)
        self.assertAlmostEqual(x.invert(2.5), 1.5)

    def test_ticks_1(self):
        # generates tixcks of varying degree
        x = LinearScale()
        exp = [0, 1]
        res = [float(y) for y in list(map(x.tickFormat(1), x.ticks(1)))]
        for i, j in zip(res, exp):
            self.assertEqual(i, j)

        exp = [0, 0.5, 1]
        res = [float(y) for y in list(map(x.tickFormat(2), x.ticks(2)))]
        for i, j in zip(res, exp):
            self.assertEqual(i, j)

        exp = [0, 0.2, 0.4, 0.6, 0.8, 1]
        res = [float(y) for y in list(map(x.tickFormat(5), x.ticks(5)))]
        for i, j in zip(res, exp):
            self.assertEqual(i, j)

        exp = [0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
        res = [float(y) for y in list(map(x.tickFormat(10), x.ticks(10)))]
        for i, j in zip(res, exp):
            self.assertEqual(i, j)

    def test_ticks_2(self):
        # generates tixcks of varying degree
        x = LinearScale([1, 0])
        exp = [0, 1]
        res = [float(y) for y in list(map(x.tickFormat(1), x.ticks(1)))]
        for i, j in zip(res, exp):
            self.assertEqual(i, j)

        exp = [0, 0.5, 1]
        res = [float(y) for y in list(map(x.tickFormat(2), x.ticks(2)))]
        for i, j in zip(res, exp):
            self.assertEqual(i, j)

        exp = [0, 0.2, 0.4, 0.6, 0.8, 1]
        res = [float(y) for y in list(map(x.tickFormat(5), x.ticks(5)))]
        for i, j in zip(res, exp):
            self.assertEqual(i, j)

        exp = [0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
        res = [float(y) for y in list(map(x.tickFormat(10), x.ticks(10)))]
        for i, j in zip(res, exp):
            self.assertEqual(i, j)

    def test_ticks_3(self):
        # formats ticks with the appropriate precision
        x = LinearScale([0.123456789, 1.23456789])
        res = list(map(x.tickFormat(1), x.ticks(1)))[0]
        self.assertEqual(res, "1")

        res = list(map(x.tickFormat(2), x.ticks(2)))[0]
        self.assertEqual(res, "0.5")

        res = list(map(x.tickFormat(4), x.ticks(4)))[0]
        self.assertEqual(res, "0.2")

        res = list(map(x.tickFormat(8), x.ticks(8)))[0]
        self.assertEqual(res, "0.2")

        res = list(map(x.tickFormat(16), x.ticks(16)))[0]
        self.assertEqual(res, "0.2")

        res = list(map(x.tickFormat(32), x.ticks(32)))[0]
        self.assertEqual(res, "0.15")

        res = list(map(x.tickFormat(64), x.ticks(64)))[0]
        self.assertEqual(res, "0.14")

        res = list(map(x.tickFormat(128), x.ticks(128)))[0]
        self.assertEqual(res, "0.13")

        res = list(map(x.tickFormat(256), x.ticks(256)))[0]
        self.assertEqual(res, "0.125")

    def test_nice_1(self):
        # nices the domain, extending it to round numbers
        x = LinearScale().domain([1.1, 10.9]).nice()
        self.assertEqual(x.domain(), [1, 11])

        x = LinearScale().domain([10.9, 1.1]).nice()
        self.assertEqual(x.domain(), [11, 1])

        x = LinearScale().domain([0.7, 11.001]).nice()
        self.assertEqual(x.domain(), [0, 12])

        x = LinearScale().domain([123.1, 6.7]).nice()
        self.assertEqual(x.domain(), [130, 0])

        x = LinearScale().domain([0, 0.49]).nice()
        self.assertEqual(x.domain(), [0, 0.5])

        x = LinearScale().domain([-0.1, 51.1]).nice(8)
        self.assertEqual(x.domain(), [-10, 60])

    def test_nice_2(self):
        # has no effect on degenerate domains
        x = LinearScale().domain([0, 0]).nice()
        self.assertEqual(x.domain(), [0, 0])

        x = LinearScale().domain([0.5, 0.5]).nice()
        self.assertEqual(x.domain(), [0.5, 0.5])

    def test_nice_3(self):
        # accepts a tick count to control nicing step
        x = LinearScale().domain([12, 87]).nice(5)
        self.assertEqual(x.domain(), [0, 100])

        x = LinearScale().domain([12, 87]).nice(10)
        self.assertEqual(x.domain(), [10, 90])

        x = LinearScale().domain([12, 87]).nice(100)
        self.assertEqual(x.domain(), [12, 87])

    def test_copy_1(self):
        # changes to the domain are isolated
        x = LinearScale()
        y = x.copy()
        x.domain([1, 2])
        self.assertEqual(y.domain(), [0, 1])
        self.assertEqual(x(1), 0)
        self.assertEqual(y(1), 1)
        y.domain([2, 3])
        self.assertEqual(x(2), 1)
        self.assertEqual(y(2), 0)
        self.assertEqual(x.domain(), [1, 2])
        self.assertEqual(y.domain(), [2, 3])

    def test_copy_2(self):
        # change to the range are isolated
        x = LinearScale()
        y = x.copy()
        x.range([1, 2])
        self.assertEqual(x.invert(1), 0)
        self.assertEqual(y.invert(1), 1)
        self.assertEqual(y.range(), [0, 1])
        y.range([2, 3])
        self.assertEqual(x.invert(2), 1)
        self.assertEqual(y.invert(2), 0)
        self.assertEqual(x.range(), [1, 2])
        self.assertEqual(y.range(), [2, 3])

    def test_copy_3(self):
        # changes to clamping are isolated
        x = LinearScale().clamp(True)
        y = x.copy()
        x.clamp(False)
        self.assertEqual(x(2), 2)
        self.assertEqual(y(2), 1)
        self.assertTrue(y.clamp())
        y.clamp(False)
        self.assertEqual(x(2), 2)
        self.assertEqual(y(2), 2)
        self.assertFalse(x.clamp())
