
def toLayers(nodes):
    if not nodes:
        return None
    if isinstance(nodes[0], list):
        return nodes
    return [nodes]

def displacement(nodes):
    if not nodes:
        return 0
    layers = toLayers(nodes)
    return sum([abs(n.displacement()) for layer in layers for n in layer])

def overflow(nodes, minPos, maxPos):
    if (not nodes) or (not minPos is None) or (not maxPos is None):
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

def overDensity(nodes, density, layerWidth, nodeSpacing):
    if not nodes:
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

def overlapCount(nodes, buf):
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
    return total

def weightedAllocatedSpace(nodes):
    if not nodes:
        return 0
    layers = toLayers(nodes)
    total = 0
    for layerIndex, layer in enumerate(layers):
        total += layerIndex * sum([d.width for d in layer])
    return total

