
class Node(object):
    def __init__(self, idealPos, width, data=None):
        self.idealPos = idealPos
        self.currentPos = idealPos
        self.width = width
        self.data = data
        self.layerIndex = 0
        self.parent = None
        self.overlap = None
        self.overlapCount = 0
        self.child = None
        # for rendering
        self.x = None
        self.dx = None
        self.y = None
        self.dy = None
        # other
        self.w = 0
        self.h = 0

    def __repr__(self):
        s = ('Node(idealPos=%r, currentPos=%r, width=%r, '
                'layerIndex=%r, data=%r)' % (self.idealPos, self.currentPos, 
                    self.width, self.layerIndex, self.data))
        return s
    def __str__(self):
        return repr(self)

    def distanceFrom(self, node):
        halfWidth = self.width/2
        nodeHalfWidth = node.width/2
        maxval = max(self.currentPos - halfWidth, node.currentPos - 
                nodeHalfWidth)
        minval = min(self.currentPos + halfWidth, node.currentPos + 
                nodeHalfWidth)
        return maxval - minval

    def moveToIdealPosition(self):
        self.currentPos = self.idealPos

    def displacement(self):
        return self.idealPos - self.currentPos

    def overlapWithNode(self, node, buf=None):
        _buffer = buf if buf else 0
        return self.distanceFrom(node) - _buffer < 0

    def overlapWithPoint(self, pos):
        halfWidth = self.width/2
        return ((pos >= self.currentPos - halfWidth) and (pos <=
            self.currentPos + halfWidth))

    def positionBefore(self, node, buf=None):
        _buffer = buf if buf else 0
        return node.currentLeft() - self.width/2 - _buffer

    def positionAfter(self, node, buf=None):
        _buffer = buf if buf else 0
        return node.currentRight() + self.width/2 + _buffer

    def currentRight(self):
        return self.currentPos + self.width/2

    def currentLeft(self):
        return self.currentPos - self.width/2

    def idealRight(self):
        return self.idealPos + self.width/2

    def idealLeft(self):
        return self.idealPos - self.width/2

    def removeStub(self):
        if self.parent:
            self.parent.child = None
            self.parent = None
        return self

    def createStub(self, width=None):
        stub = Node(self.idealPos, width, self.data)
        stub.currentPos = self.currentPos
        stub.child = self
        self.parent = stub
        return stub

    def isStub(self):
        return not(not(self.child))

    def getPathToRoot(self):
        path = []
        current = self
        while current:
            path.append(current)
            current = current.parent
        return path

    def getPathFromRoot(self):
        return list(reversed(self.getPathToRoot()))

    def getPathToRootLength(self):
        length = 0
        current = self
        while current:
            targetPos = (current.parent.currentPos if current.parent else 
                    current.idealPos)
            length += abs(current.currentPos - targetPos)
            current = current.parent
        return length

    def getRoot(self):
        previous = self
        current = self
        while current:
            previous = current
            current = current.parent
        return previous

    def getLayerIndex(self):
        return self.layerIndex

    def clone(self):
        node = Node(self.idealPos, self.width, self.data)
        node.currentPos = self.currentPos
        node.layerIndex = self.layerIndex
        return node

