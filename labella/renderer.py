def lineTo(point):
    return 'L ' + ' '.join([str(x) for x in point])

def moveTo(point):
    return 'M ' + ' '.join([str(x) for x in point])

def curveTo(c1, c2, point2):
    c1str = ' '.join([str(x) for x in c1])
    c2str = ' '.join([str(x) for x in c2])
    ptstr = ' '.join([str(x) for x in point2])
    return 'C ' + c1str + ' ' + c2str + ' ' + ptstr

def vCurveBetween(point1, point2):
    midY = (point1[1] + point2[1]) / 2
    return curveTo([point1[0], midY], [point2[0], midY], point2)

def hCurveBetween(point1, point2):
    midX = (point1[0] + point2[0]) / 2
    return curveTo([midX, point1[1]], [midX, point2[1]], point2)

DEFAULT_OPTIONS = {
        'layerGap': 60,
        'nodeHeight': 10,
        'direction': 'down'
        }

class Renderer(object):
    def __init__(self, options):
        if not options:
            options = {}
        self.options = {k:v for k,v in DEFAULT_OPTIONS.items()}
        self.options.update(options)

    def getWayPoints(self, node):
        options = self.options
        direction = options['direction']
        hops = node.getPathFromRoot()
        gap = options['nodeHeight'] + options['layerGap']

        if direction == 'left':
            out = [[[0, hops[0].idealPos]]]
            for level, hop in enumerate(hops):
                xPos = gap * (level+1) * -1
                out.append(
                        [
                            [xPos + options['nodeHeight'], hop.currentPos],
                            [xPos, hop.currentPos]
                        ]
                        )
        elif direction == 'right':
            out = [[[0, hops[0].idealPos]]]
            for level, hop in enumerate(hops):
                xPos = gap * (level+1)
                out.append(
                        [
                            [xPos - options['nodeHeight'], hop.currentPos],
                            [xPos, hop.currentPos]
                        ]
                        )
        elif direction == 'up':
            out = [[[hops[0].idealPos, 0]]]
            for level, hop in enumerate(hops):
                yPos = gap * (level + 1) * -1
                out.append(
                        [
                            [hop.currentPos, yPos + options['nodeHeight']],
                            [hop.currentPos, yPos]
                        ]
                        )
        else:
            out = [[[hops[0].idealPos, 0]]]
            for level, hop in enumerate(hops):
                yPos = gap * (level + 1)
                out.append(
                        [
                            [hop.currentPos, yPos - options['nodeHeight']],
                            [hop.currentPos, yPos]
                        ]
                        )
        return out

    def layout(self, nodes):
        options = self.options
        direction = options['direction']
        gap = options['layerGap'] + options['nodeHeight']

        if direction == 'left':
            for node in nodes:
                pos = node.getLayerIndex() * gap + options['layerGap']
                node.x = -pos - options['nodeHeight']
                node.y = node.currentPos
                node.dx = options['nodeHeight']
                node.dy = node.width
        elif direction == 'right':
            for node in nodes:
                pos = node.getLayerIndex() * gap + options['layerGap']
                node.x = pos
                node.y = node.currentPos
                node.dx = options['nodeHeight']
                node.dy = node.width
        elif direction == 'up':
            for node in nodes:
                pos = node.getLayerIndex() * gap + options['layerGap']
                node.x = node.currentPos
                node.y = -pos - options['nodeHeight']
                node.dx = node.width
                node.dy = options['nodeHeight']
        else:
            for node in nodes:
                pos = node.getLayerIndex() * gap + options['layerGap']
                node.x = node.currentPos
                node.y = pos
                node.dx = node.width
                node.dy = options['nodeHeight']

        return nodes

    def generatePath(self, node, tikz=False):
        options = self.options
        direction = options['direction']
        waypoints = self.getWayPoints(node)
        steps = [moveTo(waypoints[0][0])]

        if direction == 'left' or direction == 'right':
            enum = enumerate(waypoints)
            level, prev = next(enum)
            for level, current in enum:
                steps.append(hCurveBetween(prev[len(prev) - 1], current[0]))
                if level < len(waypoints) - 1:
                    steps.append(lineTo(current[1]))
                prev = current
        else:
            enum = enumerate(waypoints)
            level, prev = next(enum)
            for level, current in enum:
                steps.append(vCurveBetween(prev[len(prev) - 1], current[0]))
                if level < len(waypoints) - 1:
                    steps.append(lineTo(current[1]))
                prev = current
        if tikz:
            return steps
        return ' '.join(steps)
