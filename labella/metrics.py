
def toLayers(nodes):
    if not nodes:
        return None
    if isinstance(nodes[0], list):
        return nodes
    return [nodes]

def denominator(layers):
    return sum((len(l) for l in layers))

def denominatorWithoutStubs(layers):
    return sum((len([x for x in l if not x.isStub()]) for l in layers))

def displacement(nodes):
    if not nodes:
        return 0
    layers = toLayers(nodes)
    thesum = 0
    for layer in layers:
        for node in layer:
            thesum += 0 if node.isStub() else abs(node.displacement())
    return thesum / denominatorWithoutStubs(layers)

def pathLength(nodes):
    if len(nodes) == 0:
        return 0
    layers = toLayers(nodes)
    thesum = 0
    for layer in layers:
        for node in layer:
            thesum += 0 if node.isStub() else abs(node.getPathToRootLength())
    return thesum / denominatorWithoutStubs(layers)

def overflowSpace(nodes, minPos=None, maxPos=None):
    if (not nodes) or ((minPos is None) and (maxPos is None)):
        return 0
    layers = toLayers(nodes)

    total = 0
    for layer in layers:
        for node in layer:
            l = node.currentLeft()
            r = node.currentRight()

            if not minPos is None:
                if r <= minPos:
                    total += node.width
                elif l < minPos:
                    total += minPos - l
            if not maxPos is None:
                if l >= maxPos:
                    total += node.width
                elif r > maxPos:
                    total += r - maxPos
    return total

def overDensitySpace(nodes, density=None, layerWidth=None, nodeSpacing=0):
    if (not nodes) or (density is None) or (layerWidth is None):
        return 0
    limit = density * layerWidth
    layers = toLayers(nodes)

    total = 0
    for layer in layers:
        width = 0
        for node in layer:
            width += node.width + nodeSpacing
        width -= nodeSpacing
        total += 0 if width <= limit else width - limit
    return total

def overlapCount(nodes, buf=0):
    if not nodes:
        return 0
    layers = toLayers(nodes)
    total = 0
    for layer in layers:
        count = 0
        for i in range(len(layer)):
            for j in range(i+1, len(layer)):
                if layer[i].overlapWithNode(layer[j], buf):
                    count += 1
        total += count
    return total

def overlapSpace(nodes):
    if not nodes:
        return 0
    layers = toLayers(nodes)
    total = 0
    for layer in layers:
        count = 0
        for i in range(len(layer)):
            for j in range(i+1, len(layer)):
                distance = layer[i].distanceFrom(layer[j])
                count += abs(distance) if distance < 0 else 0
        total += count
    return total / denominator(layers)

def weightedAllocation(nodes):
    if not nodes:
        return 0
    layers = toLayers(nodes)

    total = 0
    for layerIndex, layer in enumerate(layers):
        total += layerIndex * len([x for x in layer if not x.isStub()])
    return total

def weightedAllocatedSpace(nodes):
    if not nodes:
        return 0
    layers = toLayers(nodes)
    total = 0
    for layerIndex, layer in enumerate(layers):
        total += layerIndex * sum([d.width for d in layer])
    return total

