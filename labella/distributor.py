
from math import ceil
from intervaltree import IntervalTree

DEFAULT_OPTIONS = {
        'algorithm': 'overlap',
        'layerWidth': 1000,
        'density': 0.75,
        'nodeSpacing': 3,
        'stubWidth': 1
        }

class Distributor(object):
    def __init__(self, options=None):
        if options is None:
            options = {}
        self.options = {k:v for k,v in DEFAULT_OPTIONS.items()}
        self.options.update(options)

    def computeRequiredWidth(self, nodes):
        total = 0
        for node in nodes:
            total += node.width + self.options['nodeSpacing']
        total -= self.options['nodeSpacing']
        return total

    def maxWidthPerLayer(self):
        return self.options['density'] * self.options['layerWidth']

    def needToSplit(self, nodes):
        return self.estimateRequiredLayers(nodes) > 1

    def estimateRequiredLayers(self, nodes):
        if self.options['layerWidth']:
            return ceil(self.computeRequiredWidth(nodes) /
                    self.maxWidthPerLayer())
        else:
            return 1

    def distribute(self, nodes):
        if (not nodes or len(nodes) == 0):
            return []
        if ((self.options['algorithm'] == 'none') or (not 'algorithm' in
            self.options)):
            return [nodes]

        nodes = sorted(nodes, key=lambda x: x.idealPos)

        if not self.needToSplit(nodes):
            return [nodes]

        if self.options['algorithm'] == 'simple':
            return self.algorithm_simple(nodes)
        elif self.options['algorithm'] == 'roundRobin':
            return self.algorithm_roundRobin(nodes)
        elif self.options['algorithm'] == 'overlap':
            return self.algorithm_overlap(nodes)
        else:
            raise ValueError(self.options['algorithm'])

    def algorithm_simple(self, nodes):
        numLayers = self.estimateRequiredLayers(nodes)
        layers = []
        for i in range(numLayers):
            layers.append([])

        for i, node in enumerate(nodes):
            mod = i % numLayers
            layers[mod].append(node)

            stub = node
            for j in range(mod-1, -1, -1):
                stub = stub.createStub(self.options['stubWidth'])
                layers[j].append(stub)

        return layers

    def algorithm_roundRobin(self, nodes):
        layers = []
        return layers

    def algorithm_overlap(self, nodes):
        layers = []
        maxWidth = self.maxWidthPerLayer()

        puntedNodes = nodes[:]
        puntedWidth = self.computeRequiredWidth(puntedNodes)

        while puntedWidth > maxWidth:
            self.countIdealOverlaps(puntedNodes)

            nodesInCurrentLayer = puntedNodes[:]
            currentLayerWidth = puntedWidth
            puntedNodes = []

            while (len(nodesInCurrentLayer) > 2 and currentLayerWidth >
                    maxWidth):
                # Sort by overlaps
                nodesInCurrentLayer.sort(key=lambda x : x.overlapCount,
                        reverse=True)

                # Remove the node with the most overlap
                first = nodesInCurrentLayer.pop(0)

                # Update width
                currentLayerWidth -= first.width
                currentLayerWidth += self.options['stubWidth']

                # Update overlap count for the remaining nodes
                for node in first.overlaps:
                    node.overlapCount -= 1

                puntedNodes.append(first)

            layers.append(nodesInCurrentLayer)

            puntedWidth = self.computeRequiredWidth(puntedNodes)

        if len(puntedNodes) > 0:
            layers.append(puntedNodes)

        # Create stubs
        # From last layer
        for i in range(len(layers)-1, 0, -1):
            layer = layers[i]
            # For each node in the layer
            for k in range(len(layer)):
                node = layer[k]
                # If it is not a stub
                if node.isStub():
                    continue
                # Create one stub for each layer above it
                stub = node
                for j in range(i-1, -1, -1):
                    stub = stub.createStub(self.options['stubWidth'])
                    layers[j].append(stub)

        return layers

    def countIdealOverlaps(self, nodes):
        iTree = IntervalTree()
        for node in nodes:
            iTree.addi(node.idealLeft(), node.idealRight(), data=node)

        for node in nodes:
            overlaps = iTree.search(node.idealLeft(), node.idealRight())
            node.overlaps = [x.data for x in overlaps]
            node.overlapCount = len(overlaps)
