import unittest

from labella import vpsc

def make_variables(variables):
    vs = []
    for var in variables:
        if isinstance(var, int):
            v = vpsc.Variable(var)
        else:
            v = vpsc.Variable(**var)
        vs.append(v)
    return vs

def make_constraints(constraints, vs):
    cs = []
    for con in constraints:
        c = vpsc.Constraint(vs[con['left']], vs[con['right']], con['gap'])
        cs.append(c)
    return cs

class VpscTestCase(unittest.TestCase):

    PRECISION = 4

    def get_solution(self, variables, constraints, expected):
        vs = make_variables(variables)
        cs = make_constraints(constraints, vs)
        solver = vpsc.Solver(vs, cs)
        solver.solve()
        rnd_exp = [round(x, self.PRECISION) for x in expected]
        rnd_res = [round(v.position(), self.PRECISION) for v in vs]
        return rnd_exp, rnd_res

    def test_no_splits(self):
        variables = [
                {'desiredPosition': 2},
                {'desiredPosition': 9},
                {'desiredPosition': 9},
                {'desiredPosition': 9},
                {'desiredPosition': 2}]
        constraints = [
                {'left': 0, 'right': 4, 'gap': 3},
                {'left': 0, 'right': 1, 'gap': 3},
                {'left': 1, 'right': 2, 'gap': 3},
                {'left': 2, 'right': 4, 'gap': 3},
                {'left': 3, 'right': 4, 'gap': 3}
                ]
        expected = [1.4, 4.4, 7.4, 7.4, 10.4]
        rnd_exp, rnd_res = self.get_solution(variables, constraints, expected)
        self.assertEqual(rnd_exp, rnd_res)

    def test_simple_scale(self):
        variables = [
                {'desiredPosition': 0, 'weight': 1, 'scale': 2},
                {'desiredPosition': 0, 'weight': 1, 'scale': 1}
                ]
        constraints = [
                {'left': 0, 'right': 1, 'gap': 2}
                ]
        expected = [-0.8, 0.4]
        rnd_exp, rnd_res = self.get_solution(variables, constraints, expected)
        self.assertEqual(rnd_exp, rnd_res)

    def test_simple_scale_2(self):
        variables = [
                {'desiredPosition': 1, 'weight': 1, 'scale': 3},
                {'desiredPosition': 1, 'weight': 1, 'scale': 2},
                {'desiredPosition': 1, 'weight': 1, 'scale': 4}
                ]
        constraints = [
                {'left': 0, 'right': 1, 'gap': 2},
                {'left': 1, 'right': 2, 'gap': 2}
                ]
        expected = [0.2623, 1.3934, 1.1967]
        rnd_exp, rnd_res = self.get_solution(variables, constraints, expected)
        self.assertEqual(rnd_exp, rnd_res)

    def test_nontrivial_merging(self):
        variables = [4, 6, 9, 2, 5]
        constraints = [
                {'left': 0, 'right': 2, 'gap': 3},
                {'left': 0, 'right': 3, 'gap': 3},
                {'left': 1, 'right': 4, 'gap': 3},
                {'left': 2, 'right': 4, 'gap': 3},
                {'left': 2, 'right': 3, 'gap': 3},
                {'left': 3, 'right': 4, 'gap': 3},
                ]
        expected = [0.5, 6, 3.5, 6.5, 9.5]
        rnd_exp, rnd_res = self.get_solution(variables, constraints, expected)
        self.assertEqual(rnd_exp, rnd_res)

    def test_next(self):
        variables = [5, 6, 7, 4, 3]
        constraints = [
                {'left': 0, 'right': 4, 'gap': 3},
                {'left': 1, 'right': 2, 'gap': 3},
                {'left': 2, 'right': 3, 'gap': 3},
                {'left': 2, 'right': 4, 'gap': 3},
                {'left': 3, 'right': 4, 'gap': 3},
                ]
        expected = [5, 0.5, 3.5, 6.5, 9.5]
        rnd_exp, rnd_res = self.get_solution(variables, constraints, expected)
        self.assertEqual(rnd_exp, rnd_res)

    def test_split_block_activate_different_constraint(self):
        variables = [7, 1, 6, 0, 2]
        constraints = [
                {'left': 0, 'right': 3, 'gap': 3},
                {'left': 0, 'right': 1, 'gap': 3},
                {'left': 1, 'right': 4, 'gap': 3},
                {'left': 2, 'right': 4, 'gap': 3},
                {'left': 2, 'right': 3, 'gap': 3},
                {'left': 3, 'right': 4, 'gap': 3},
                ]
        expected = [0.8, 3.8, 0.8, 3.8, 6.8]
        rnd_exp, rnd_res = self.get_solution(variables, constraints, expected)
        self.assertEqual(rnd_exp, rnd_res)

    def test_nontrivial_split(self):
        variables = [0, 9, 1, 9, 5, 1, 2, 1, 6, 3]
        constraints = [
                {'left': 0, 'right': 3, 'gap': 3 },
                {'left': 1, 'right': 8, 'gap': 3 },
                {'left': 1, 'right': 6, 'gap': 3 },
                {'left': 2, 'right': 6, 'gap': 3 },
                {'left': 3, 'right': 5, 'gap': 3 },
                {'left': 3, 'right': 6, 'gap': 3 },
                {'left': 3, 'right': 7, 'gap': 3 },
                {'left': 4, 'right': 8, 'gap': 3 },
                {'left': 4, 'right': 7, 'gap': 3 },
                {'left': 5, 'right': 8, 'gap': 3 },
                {'left': 5, 'right': 7, 'gap': 3 },
                {'left': 5, 'right': 8, 'gap': 3 },
                {'left': 6, 'right': 9, 'gap': 3 },
                {'left': 7, 'right': 8, 'gap': 3 },
                {'left': 7, 'right': 9, 'gap': 3 },
                {'left': 8, 'right': 9, 'gap': 3 }]
        expected = [-3.71429, 4, 1, -0.714286, 2.28571, 2.28571, 7, 5.28571,
                8.28571, 11.2857]
        rnd_exp, rnd_res = self.get_solution(variables, constraints, expected)
        self.assertEqual(rnd_exp, rnd_res)

    def test_6(self):
        variables = [
		{'desiredPosition': 7, 'weight': 1 },
		{'desiredPosition': 0, 'weight': 1 },
		{'desiredPosition': 3, 'weight': 1 },
		{'desiredPosition': 1, 'weight': 1 },
		{'desiredPosition': 4, 'weight': 1 }
		]
        constraints = [
		{'left': 0, 'right': 3, 'gap': 3 },
		{'left': 0, 'right': 2, 'gap': 3 },
		{'left': 1, 'right': 4, 'gap': 3 },
		{'left': 1, 'right': 4, 'gap': 3 },
		{'left': 2, 'right': 3, 'gap': 3 },
		{'left': 3, 'right': 4, 'gap': 3 }
		]
        expected = [-0.75, 0, 2.25, 5.25, 8.25]
        rnd_exp, rnd_res = self.get_solution(variables, constraints, expected)
        self.assertEqual(rnd_exp, rnd_res)

    def test_7(self):
        variables = [
                {'desiredPosition': 4, 'weight': 1 },
                {'desiredPosition': 2, 'weight': 1 },
                {'desiredPosition': 3, 'weight': 1 },
                {'desiredPosition': 1, 'weight': 1 },
                {'desiredPosition': 8, 'weight': 1 }
                ]
        constraints = [
                {'left': 0, 'right': 4, 'gap': 3 },
                {'left': 0, 'right': 2, 'gap': 3 },
                {'left': 1, 'right': 3, 'gap': 3 },
                {'left': 2, 'right': 3, 'gap': 3 },
                {'left': 2, 'right': 4, 'gap': 3 },
                {'left': 3, 'right': 4, 'gap': 3 }
                ]
        expected = [-0.5, 2, 2.5, 5.5, 8.5]
        rnd_exp, rnd_res = self.get_solution(variables, constraints, expected)
        self.assertEqual(rnd_exp, rnd_res)

    def test_8(self):
        variables = [
                {'desiredPosition': 3, 'weight': 1 },
                {'desiredPosition': 4, 'weight': 1 },
                {'desiredPosition': 0, 'weight': 1 },
                {'desiredPosition': 5, 'weight': 1 },
                {'desiredPosition': 6, 'weight': 1 }
                ]
        constraints = [
                {'left': 0, 'right': 1, 'gap': 3 },
                {'left': 0, 'right': 2, 'gap': 3 },
                {'left': 1, 'right': 2, 'gap': 3 },
                {'left': 1, 'right': 4, 'gap': 3 },
                {'left': 2, 'right': 3, 'gap': 3 },
                {'left': 2, 'right': 3, 'gap': 3 },
                {'left': 3, 'right': 4, 'gap': 3 },
                {'left': 3, 'right': 4, 'gap': 3 }
                ]
        expected = [-2.4, 0.6, 3.6, 6.6, 9.6]
        rnd_exp, rnd_res = self.get_solution(variables, constraints, expected)
        self.assertEqual(rnd_exp, rnd_res)

    def test_9(self):
        variables = [
                {'desiredPosition': 8, 'weight': 1 },
                {'desiredPosition': 2, 'weight': 1 },
                {'desiredPosition': 6, 'weight': 1 },
                {'desiredPosition': 5, 'weight': 1 },
                {'desiredPosition': 3, 'weight': 1 }]
        constraints = [
                {'left': 0, 'right': 4, 'gap': 3 },
                {'left': 0, 'right': 3, 'gap': 3 },
                {'left': 1, 'right': 2, 'gap': 3 },
                {'left': 1, 'right': 4, 'gap': 3 },
                {'left': 2, 'right': 3, 'gap': 3 },
                {'left': 2, 'right': 4, 'gap': 3 },
                {'left': 3, 'right': 4, 'gap': 3 }]
        expected = [3.6, 0.6, 3.6, 6.6, 9.6]
        rnd_exp, rnd_res = self.get_solution(variables, constraints, expected)
        self.assertEqual(rnd_exp, rnd_res)

if __name__ == '__main__':
    unittest.main()
