"""
Python rewrite of the VPSC code included in Labella.js.

Originally modified from:
    https://github.com/tgdwyer/WebCola/blob/master/WebCola/src/vpsc.ts

"""

from sys import maxsize

class PositionStats(object):
    def __init__(self, scale):
        self.scale = scale
        self.AB = 0
        self.AD = 0
        self.A2 = 0

    def addVariable(self, v):
        ai = self.scale / v.scale
        bi = v.offset / v.scale
        wi = v.weight
        self.AB += wi * ai * bi
        self.AD += wi * ai * v.desiredPosition
        self.A2 += wi * ai * ai

    def getPosn(self):
        return (self.AD - self.AB) / self.A2

class Constraint(object):
    def __init__(self, left, right, gap, equality=None):
        if (equality is None):
            equality = False
        self.left = left
        self.right = right
        self.gap = gap
        self.equality = equality
        self.active = False
        self.unsatisfiable = False

    def slack(self):
        if self.unsatisfiable:
            return maxsize
        return (self.right.scale * self.right.position() - self.gap -
                self.left.scale * self.left.position())

    def __repr__(self):
        s = ("Constraint(left=%r, right=%r, gap=%r, equality=%r)" % 
                (self.left, self.right, self.gap, self.equality))
        return s
    def __str__(self):
        return repr(self)

class Variable(object):
    def __init__(self, desiredPosition, weight=None, scale=None):
        if weight is None:
            weight = 1
        if scale is None:
            scale = 1
        self.desiredPosition = desiredPosition
        self.weight = weight
        self.scale = scale
        self.offset = 0
        self.node = None

    def dfdv(self):
        return 2.0 * self.weight * (self.position() - self.desiredPosition)

    def position(self):
        return ((self.block.ps.scale * self.block.posn + self.offset) /
                self.scale)

    def visitNeighbours(self, prev, f):
        def ff(c, _next):
            return c.active and prev != _next and f(c, _next)
        for c in self.cOut:
            ff(c, c.right)
        for c in self.cIn:
            ff(c, c.left)

    def __repr__(self):
        s = ("Variable(desiredPos=%r, weight=%r, scale=%r, offset=%r)" % 
                (self.desiredPosition, self.weight, self.scale, self.offset))
        return s
    def __str__(self):
        return repr(self)

class Block(object):
    def __init__(self, v):
        self.vars = []
        v.offset = 0
        self.ps = PositionStats(v.scale)
        self.addVariable(v)

    def addVariable(self, v):
        v.block = self
        self.vars.append(v)
        self.ps.addVariable(v)
        self.posn = self.ps.getPosn()

    def updateWeightedPosition(self):
        self.ps.AB = 0
        self.ps.AD = 0
        self.ps.A2 = 0
        for i in range(len(self.vars)):
            self.ps.addVariable(self.vars[i])
        self.posn = self.ps.getPosn()

    def compute_lm(self, v, u, postAction):
        dfdv = v.dfdv()
        _self = self
        def f(c, _next):
            nonlocal dfdv
            _dfdv = _self.compute_lm(_next, v, postAction)
            if _next == c.right:
                dfdv += _dfdv * c.left.scale
                c.lm = _dfdv
            else:
                dfdv += _dfdv * c.right.scale
                c.lm = -_dfdv
            postAction(c)
        v.visitNeighbours(u, f)
        return dfdv / v.scale

    def populateSplitBlock(self, v, prev):
        _self = self
        def f(c, _next):
            _next.offset = v.offset
            if _next == c.right:
                _next.offset += c.gap
            else:
                _next.offset -= c.gap
            _self.addVariable(_next)
            _self.populateSplitBlock(_next, v)
        v.visitNeighbours(prev, f)

    def traverse(self, visit, acc, v, prev):
        _self = self
        if not v:
            v = self.vars[0]
        if not prev:
            prev = None
        def f(c, _next):
            acc.push(visit(c))
            _self.traverse(visit, acc, _next, v)
        v.visitNeighbours(prev, f)

    def findMinLM(self):
        m = None
        def f(c):
            nonlocal m
            if not c.equality and (m is None or c.lm < m.lm):
                m = c
        self.compute_lm(self.vars[0], None, f)
        return m

    def findMinLMBetween(self, lv, rv):
        def f(x):
            pass
        self.compute_lm(lv, None, f)
        m = None
        def f(c, _next):
            nonlocal m
            if (not c.equality and c.right == _next and (m is None or c.lm <
                m.lm)):
                m = c
        self.findPath(lv, None, rv, f)
        return m

    def findPath(self, v, prev, to, visit):
        _self = self
        endFound = False
        def f(c, _next):
            nonlocal endFound
            if (not endFound and (_next == to or _self.findPath(_next, v, to,
                visit))):
                endFound = True
                visit(c, _next)
        v.visitNeighbours(prev, f)
        return endFound

    def isActiveDirectedPathBetween(self, u, v):
        if u == v:
            return True
        for i in range(len(u.cOut)-1, -1, -1):
            c = u.cOut[i]
            if c.active and self.isActiveDirectedPathBetween(c.right, v):
                return True
        return False

    @classmethod
    def split(cls, c):
        c.active = False
        return [Block.createSplitBlock(c.left),
                Block.createSplitBlock(c.right)]

    @classmethod
    def createSplitBlock(cls, startVar):
        b = Block(startVar)
        b.populateSplitBlock(startVar, None)
        return b

    def splitBetween(self, vl, vr):
        c = self.findMinLMBetween(vl, vr)
        if not c is None:
            bs = Block.split(c)
            return {'constraint': c, 'lb': bs[0], 'rb': bs[1] }
        return None

    def mergeAcross(self, b, c, dist):
        c.active = True
        for i in range(len(b.vars)):
            v = b.vars[i]
            v.offset += dist
            self.addVariable(v)
        self.posn = self.ps.getPosn()

    def cost(self):
        _sum = 0
        for i in range(len(self.vars)-1, -1, -1):
            v = self.vars[i]
            d = v.position() - v.desiredPosition
            _sum += d * d * v.weight
        return _sum


class Blocks(object):
    def __init__(self, vs):
        self.vs = vs
        n = len(vs)
        self._list = [None]*n
        for i in range(len(vs)-1, -1, -1):
            b = Block(vs[i])
            self._list[i] = b
            b.blockInd = i

    def cost(self):
        _sum = 0
        for i in range(len(self._list)-1, -1, -1):
            _sum += self._list[i].cost()
        return _sum

    def insert(self, b):
        b.blockInd = len(self._list)
        self._list.append(b)

    def remove(self, b):
        swapBlock = self._list[-1]
        if not b == swapBlock:
            self._list[b.blockInd] = swapBlock
            swapBlock.blockInd = b.blockInd
        self._list = self._list[:-1]

    def merge(self, c):
        l = c.left.block
        r = c.right.block
        dist = c.right.offset - c.left.offset - c.gap
        if len(l.vars) < len(r.vars):
            r.mergeAcross(l, c, dist)
            self.remove(l)
        else:
            l.mergeAcross(r, c, -dist)
            self.remove(r)

    def forEach(self, f):
        for b in self._list:
            f(b)

    def updateBlockPositions(self):
        for b in self._list:
            b.updateWeightedPosition()

    def split(self, inactive):
        self.updateBlockPositions()
        for b in self._list:
            v = b.findMinLM()
            if (not v is None and v.lm < Solver.LAGRANGIAN_TOLERANCE):
                b = v.left.block
                newblocks = Block.split(v)
                for nb in newblocks:
                    self.insert(nb)
                self.remove(b)
                inactive.append(v)

class Solver(object):

    LAGRANGIAN_TOLERANCE = -1e-4
    ZERO_UPPERBOUND = -1e-10

    def __init__(self, vs, cs):
        self.vs = vs
        self.cs = cs
        for v in vs:
            v.cIn = []
            v.cOut = []
        for c in cs:
            c.left.cOut.append(c)
            c.right.cIn.append(c)
        self.inactive = cs[:]
        for c in self.inactive:
            c.active = False
        self.bs = None

    def cost(self):
        return self.bs.cost()

    def setStartingPositions(self, ps):
        self.inactive = self.cs[:]
        for c in self.inactive:
            c.active = False
        self.bs = Blocks(self.vs)
        for i, b in enumerate(self.bs):
            b.posn = ps[i]

    def setDesiredPositions(self, ps):
        for i, v in enumerate(self.vs):
            v.desiredPosition = ps[i]

    def mostViolated(self):
        minSlack = maxsize
        v = None
        l = self.inactive
        n = len(l)
        deletePoint = n
        for i in range(n):
            c = l[i]
            if c.unsatisfiable:
                continue
            slack = c.slack()
            if c.equality or slack < minSlack:
                minSlack = slack
                v = c
                deletePoint = i
                if c.equality:
                    break
        if deletePoint != n and (minSlack < Solver.ZERO_UPPERBOUND and not
                v.active or v.equality):
            l[deletePoint] = l[n - 1]
            l = l[:-1]
        return v

    def satisfy(self):
        if self.bs is None:
            self.bs = Blocks(self.vs)
        self.bs.split(self.inactive)
        v = self.mostViolated()
        while (v) and (v.equality or v.slack() < Solver.ZERO_UPPERBOUND and 
                not v.active):
            lb = v.left.block
            rb = v.right.block
            if lb != rb:
                self.bs.merge(v)
            else:
                if lb.isActiveDirectedPathBetween(v.right, v.left):
                    # Cycle found
                    v.unsatisfiable = True
                    v = self.mostViolated()
                    continue
                split = lb.splitBetween(v.left, v.right)
                if not split is None:
                    self.bs.insert(split['lb'])
                    self.bs.insert(split['rb'])
                    self.bs.remove(lb)
                    self.inactive.append(split['constraint'])
                else:
                    v.unsatisfiable = True
                    v = self.mostViolated()
                    continue
                if v.slack() >= 0:
                    self.inactive.append(v)
                else:
                    self.bs.merge(v)

    def solve(self):
        self.satisfy()
        lastcost = maxsize
        cost = self.bs.cost()
        while abs(lastcost - cost) > 0.0001:
            self.satisfy()
            lastcost = cost
            cost = self.bs.cost()
        return cost
