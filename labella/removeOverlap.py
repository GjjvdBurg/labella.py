
from . import vpsc

DEFAULT_OPTIONS = {
        'lineSpacing': 2,
        'nodeSpacing': 3,
        'minPos': 0,
        'maxPos': None
        }

def last(arr):
    return arr[-1]

def nodeToVariable(node):
    v = vpsc.Variable(node.targetPos)
    v.node = node
    return v

def removeOverlap(nodes, options):
    if len(nodes) == 0:
        return nodes

    if options is None:
        options = {}
    new_options = {k:v for k,v in DEFAULT_OPTIONS.items()}
    new_options.update(options)
    options = new_options

    for node in nodes:
        node.targetPos = (node.parent.currentPos if node.parent else
                node.idealPos)

    nodes.sort(key=lambda x : x.targetPos)

    variables = [nodeToVariable(n) for n in nodes]

    constraints = []
    for i in range(1, len(variables)):
        v1 = variables[i-1]
        v2 = variables[i]

        if v1.node.isStub() and v2.node.isStub():
            gap = (v1.node.width + v2.node.width)/2 + options['lineSpacing']
        else:
            gap = (v1.node.width + v2.node.width)/2 + options['nodeSpacing']

        constraints.append(vpsc.Constraint(v1, v2, gap))

    if ('minPos' in options) and (not options['minPos'] is None):
        leftWall = vpsc.Variable(options['minPos'], 1e10)
        v = variables[0]
        constraints.append(vpsc.Constraint(leftWall, v, v.node.width/2))
        variables = [leftWall] + variables

    if ('maxPos' in options) and (not options['maxPos'] is None):
        rightWall = vpsc.Variable(options['maxPos'], 1e10)
        lastv = last(variables)
        constraints.append(vpsc.Constraint(lastv, rightWall, 
            lastv.node.width/2))
        variables.append(rightWall)

    solver = vpsc.Solver(variables, constraints)
    solver.solve()

    variables = [v for v in variables if v.node]
    for v in variables:
        v.node.currentPos = round(v.position())

    return nodes
