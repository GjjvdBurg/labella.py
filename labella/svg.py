"""
Create an SVG from the nodes.

"""

from xml.etree import ElementTree

CATEGORY_10 = [
        '#1f77b4',
        '#ff7f0e',
        '#2ca02c',
        '#d62728',
        '#9467bd',
        '#8c564b',
        '#e377c2',
        '#7f7f7f',
        '#bcbd22',
        '#17becf',
        ]

CATEGORY_20 = [
        '#1f77b4',
        '#aec7e8',
        '#ff7f0e',
        '#ffbb78',
        '#2ca02c',
        '#98df8a',
        '#d62728',
        '#ff9896',
        '#9467bd',
        '#c5b0d5',
        '#8c564b',
        '#c49c94',
        '#e377c2',
        '#f7b6d2',
        '#7f7f7f',
        '#c7c7c7',
        '#bcbd22',
        '#dbdb8d',
        '#17becf',
        '#9edae5',
        ]

DEFAULT_COLORSCALE = CATEGORY_10
COLORDOTS = False

def color(i):
    return DEFAULT_COLORSCALE[i%len(DEFAULT_COLORSCALE)]

def hex2dec(s):
    return int(s, 16)

def hex2rgb(code):
    if code[0:1] == '#':
        code = code[1:]
    rgb = (hex2dec(code[:2]), hex2dec(code[2:4]), hex2dec(code[4:6]))
    return rgb

def hex2rgbstr(code):
    rgb = hex2rgb(code)
    rgbstr = ', '.join([str(x) for x in rgb])
    return 'rgb(%s)' % rgbstr

def draw_svg(renderer, nodes, options, fname, direction, show_line=True, 
        colordots=False):
    # add x, y, dx, dy to nodes
    renderer.layout(nodes)
    for node in nodes:
        print(node.idealPos, node.currentPos)

    innerWidth = (options['initialWidth'] - options['margin']['left'] - 
            options['margin']['right'])
    innerHeight = (options['initialHeight'] - options['margin']['top'] - 
            options['margin']['bottom'])

    doc = ElementTree.Element('svg', width=str(options['initialWidth']),
            height=str(options['initialHeight']))
    if direction == 'up':
        trans = ElementTree.SubElement(doc, 'g', transform='translate(%i,%i)' 
                % (options['margin']['left'], options['margin']['top'] + 
                    innerHeight))
    elif direction == 'left':
        trans = ElementTree.SubElement(doc, 'g', transform='translate(%i,%i)' 
                % (options['margin']['left']+innerWidth, 
                    options['margin']['top']))
    else:
        trans = ElementTree.SubElement(doc, 'g', transform='translate(%i,%i)' 
                % (options['margin']['left'], options['margin']['top']))

    attrib_line = {'class': 'timeline'}
    if direction == 'up' or direction == 'down':
        attrib_line['x2'] = str(innerWidth)
    else:
        attrib_line['y2'] = str(innerHeight)
    if show_line:
        attrib_line['style'] = 'stroke-width: 2px; stroke: #222;'
    ElementTree.SubElement(trans, 'line', attrib=attrib_line)

    linkLayer = ElementTree.SubElement(trans, 'g')
    labelLayer = ElementTree.SubElement(trans, 'g')
    dotLayer = ElementTree.SubElement(trans, 'g')

    # Add dots
    attrib_dot = {'class': 'dot', 'r': '3'}
    for i, node in enumerate(nodes):
        rgbstr = hex2rgbstr(color(i)) if COLORDOTS else 'rgb(0, 0, 0)'
        attrib_dot['style'] = 'fill: %s;' % rgbstr
        if direction == 'up' or direction == 'down':
            attrib_dot['cx'] = str(node.getRoot().idealPos)
        else:
            attrib_dot['cy'] = str(node.getRoot().idealPos)
        ElementTree.SubElement(dotLayer, 'circle', attrib=attrib_dot)

    # Add label rectangles
    attrib_label = {'class': 'flag'}
    for i, node in enumerate(nodes):
        attrib_label['style'] = 'fill: %s;' % hex2rgbstr(color(i))
        attrib_label['width'] = str(node.dx)
        attrib_label['height'] = str(node.dy)
        if direction == 'up' or direction == 'down':
            attrib_label['x'] = str(node.x - node.dx/2)
            attrib_label['y'] = str(node.y)
        else:
            attrib_label['x'] = str(node.x)
            attrib_label['y'] = str(node.y - node.dy/2)
        ElementTree.SubElement(labelLayer, 'rect', attrib=attrib_label)

    # Add links from points on timeline to label rectangle
    for i, node in enumerate(nodes):
        thestyle = 'stroke: %s; ' % hex2rgbstr(color(i))
        thestyle += 'stroke-width: 2; '
        thestyle += 'opacity: 0.6; '
        thestyle += 'fill: none;'
        ElementTree.SubElement(linkLayer, 'path', attrib={
            'class': 'link',
            'd': renderer.generatePath(node),
            'style': thestyle
            })

    with open(fname, 'wb') as fid:
        fid.write(ElementTree.tostring(doc))

