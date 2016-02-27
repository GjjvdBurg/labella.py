
"""
This class is not included in the original Labella.js, but is partially
modelled on https://kristw.github.io/d3kit-timeline/

The idea is to make a simple timeline of objects which have text or no text.
Items must be added as either:

    dicts: {'time': value, 'width': int, 'text': str} where the 'text' field
    and the 'width' field are optional and the value field can be either a
    date(time) instance or a float. The type must be the same for all values.

or as date(time) objects:

    numbers: [date(time), date(time), date(time)]

or as

    numbers: [float, float, float]

"""

import datetime
import math
import os

from xml.etree import ElementTree

from labella.force import Force
from labella.node import Node
from labella.renderer import Renderer
from labella.scale import TimeScale, d3_extent
from labella.tex import text_dimensions, build_latex_doc
from labella.utils import COLOR_10, COLOR_20, int2name, hex2rgbf, hex2rgbstr

DEFAULT_WIDTH = 50

DEFAULT_OPTIONS = {
        'margin': {'left': 20, 'right': 20, 'top': 20, 'bottom': 20},
        'initialWidth': 400,
        'initialHeight': 400,
        'scale': TimeScale(),
        'domain': None,
        'direction': 'right',
        'dotRadius': 3,
        'layerGap': 60,
        'labella': {},
        'keyFn': None,
        'timeFn': lambda d: d['time'],
        'textFn': lambda d: d['text'] if 'text' in d else None,
        'dotColor': '#222',
        'labelBgColor': '#222',
        'labelTextColor': '#fff',
        'linkColor': '#222',
        'labelPadding': {'left': 2, 'right': 2, 'top': 3, 'bottom': 2},
        'textXOffset': '0.15em',
        'textYOffset': '0.85em',
        'showTicks': True,
        }

def d3_functor(v):
    if callable(v):
        return v
    return lambda x : v

class Item(object):
    def __init__(self, time, width=DEFAULT_WIDTH, text=None,
            numeric_value=None, data=None, output_mode='svg'):
        self.time = time
        self.text = text
        self.numeric_value = numeric_value
        self.width = width
        self.data = data
        self.output_mode = output_mode
        if self.width is None and self.text:
            self.width, self.height = self.get_text_dimensions(output_mode)
        else:
            self.height = 13.0

    def to_node(self):
        return Node(self.numeric_value, self.width, data=self)

    def get_text_dimensions(self, fontsize='11pt'):
        if self.output_mode == 'svg':
            width, height = text_dimensions(self.text, fontsize='12pt')
            width = math.ceil(width)
            height = 14.0
        else:
            width, height = text_dimensions(self.text, fontsize=fontsize)
        return width, height

    def __str__(self):
        s = ("Item(time=%r, text=%r, numeric_value=%r, width=%r,"
                " height=%r, data=%r)" % (self.time, self.text,
                    self.numeric_value, self.width, self.height, self.data))
        return s
    def __repr__(self):
        return str(self)

class Timeline(object):
    def __init__(self, dicts, options=None):
        # update timeline options
        self.options = {k:v for k,v in DEFAULT_OPTIONS.items()}
        if options:
            self.options.update(options)
        self.direction = self.options['direction']
        self.options['labella']['direction'] = self.direction
        # parse items
        self.items = self.parse_items(dicts)
        self.rotate_items()
        self.init_axis(dicts)

    def rotate_items(self):
        if self.direction in ['left', 'right']:
            for item in self.items:
                if item.text:
                    item.height, item.width = item.width, item.height

    def parse_items(self, dicts):
        items = []
        for d in dicts:
            time = d['time']
            if isinstance(time, datetime.date):
                time = datetime.datetime.combine(time,
                        datetime.datetime.min.time())
                d['time'] = time
            text = self.textFn(d)
            if text:
                width = d.get('width', None)
            else:
                width = d.get('width', DEFAULT_WIDTH)
            it = self.parse_time(time, width=width, text=text, data=d)
            items.append(it)
        return items

    def scale_items(self, items):
        innerWidth, innerHeight = self.getInnerDims()
        minval = min((i.numeric_value for i in items))
        maxval = max((i.numeric_value for i in items))
        diff = maxval - minval
        for it in items:
            num_val = (it.numeric_value - minval)/diff
            if self.direction in ['up', 'down']:
                it.numeric_value = num_val * innerWidth
            else:
                it.numeric_value = num_val * innerHeight

    def init_axis(self, data):
        if self.options['domain']:
            self.options['scale'].domain(self.options['domain'])
        else:
            self.options['scale'].domain(
                    d3_extent(data, self.options['timeFn']))
            self.options['scale'].nice()
        innerWidth, innerHeight = self.getInnerDims()
        if self.options['direction'] in ['left', 'right']:
            self.options['scale'].range([0, innerHeight])
        else:
            self.options['scale'].range([0, innerWidth])

    def parse_time(self, time, width=None, text=None, data=None):
        if isinstance(time, datetime.datetime):
            it = Item(time, numeric_value=time.timestamp(), text=text,
                    width=width, data=data)
        elif isinstance(time, datetime.date):
            it = Item(time, numeric_value=time.toordinal(), text=text,
                    width=width, data=data)
        else:
            it = Item(time, numeric_value=time, text=text, width=width,
                    data=data)
        return it

    def getInnerDims(self):
        innerWidth = (self.options['initialWidth'] -
                self.options['margin']['left'] -
                self.options['margin']['right'])
        innerHeight = (self.options['initialHeight'] -
                self.options['margin']['top'] -
                self.options['margin']['bottom'])
        return innerWidth, innerHeight

    def get_nodes(self):
        nodes = []
        for it in self.items:
            n = Node(self.timePos(it.data), it.width, data=it)
            nodes.append(n)
        for node in nodes:
            node.w = (node.data.width + self.options['labelPadding']['left'] +
                    self.options['labelPadding']['right'])
            node.h = (node.data.height + self.options['labelPadding']['top'] +
                    self.options['labelPadding']['bottom'])
            if self.options['direction'] in ['left', 'right']:
                node.h, node.w = node.w, node.h
        return nodes

    def compute(self):
        nodes = self.get_nodes()
        if self.direction in ['left', 'right']:
            nodeHeight = max((n.w for n in nodes))
        else:
            nodeHeight = max((n.h for n in nodes))
        renderer = Renderer({
            'nodeHeight': nodeHeight,
            'layerGap': self.options['layerGap'],
            'direction': self.options['direction']
            })
        renderer.layout(nodes)
        force = Force(self.options['labella'])
        force.nodes(nodes)
        force.compute()
        newnodes = force.nodes()
        renderer.layout(newnodes)
        return newnodes, renderer

    def dotColor(self, thedict, i=0):
        if self.options['dotColor'] in [COLOR_10, COLOR_20]:
            return self.options['dotColor'][i%len(self.options['dotColor'])]
        dotColor = d3_functor(self.options['dotColor'])
        return dotColor(thedict)

    def linkColor(self, thedict, i=0):
        if self.options['linkColor'] in [COLOR_10, COLOR_20]:
            return self.options['linkColor'][i%len(self.options['linkColor'])]
        linkColor = d3_functor(self.options['linkColor'])
        return linkColor(thedict)

    def labelBgColor(self, thedict, i=0):
        if self.options['labelBgColor'] in [COLOR_10, COLOR_20]:
            return self.options['labelBgColor'][i %
                    len(self.options['labelBgColor'])]
        labelBgColor = d3_functor(self.options['labelBgColor'])
        return labelBgColor(thedict)

    def labelTextColor(self, thedict, i=0):
        if self.options['labelTextColor'] in [COLOR_10, COLOR_20]:
            return self.options['labelTextColor'][i %
                    len(self.options['labelTextColor'])]
        labelTextColor = d3_functor(self.options['labelTextColor'])
        return labelTextColor(thedict)

    def textFn(self, thedict):
        if self.options['textFn'] is None:
            if not 'text' in thedict:
                return None
            return thedict.get('text', None)
        return self.options['textFn'](thedict)

    def nodePos(self, d, nodeHeight):
        if self.direction == 'right':
            return (d.x, d.y - d.dy/2)
        elif self.direction == 'left':
            return (d.x - d.w + d.dx, d.y - d.dy/2)
        elif self.direction == 'up':
            return (d.x - d.dx/2, d.y)
        elif self.direction == 'down':
            return (d.x - d.dx/2, d.y)

    def timePos(self, thedict):
        if self.options['scale'] is None:
            return self.options['timeFn'](thedict)
        return self.options['scale'](self.options['timeFn'](thedict))

class TimelineSVG(Timeline):
    def __init__(self, items, options=None):
        self.nodes = None
        self.renderer = None
        super().__init__(items, options=options)

    def export(self, filename):
        self.nodes, self.renderer = self.compute()
        initWidth, initHeight = (self.options['initialWidth'],
                self.options['initialHeight'])
        doc = ElementTree.Element('svg', width=str(initWidth),
                height=str(initHeight))
        transform = self.getTranslation()
        trans = ElementTree.SubElement(doc, 'g', transform=transform)
        ElementTree.SubElement(trans, 'g', attrib={'class': 'dummy-layer'})
        mainLayer = self.add_main(trans)
        self.add_timeline(mainLayer)
        if self.options['showTicks']:
            self.add_axis(mainLayer)
        self.add_links(mainLayer)
        self.add_labels(mainLayer)
        self.add_dots(mainLayer)
        with open(filename, 'wb') as fid:
            fid.write(ElementTree.tostring(doc))

    def getTranslation(self):
        x = self.options['margin']['left']
        y = self.options['margin']['top']
        transform = 'translate(%i, %i)' % (x, y)
        return transform

    def add_main(self, trans):
        innerWidth, innerHeight = self.getInnerDims()
        attrib = {'class': 'main-layer'}
        if self.direction == 'right':
            attrib['transform'] = 'translate(0, 0)'
        elif self.direction == 'left':
            attrib['transform'] = 'translate(%i, 0)' % innerWidth
        elif self.direction == 'up':
            attrib['transform'] = 'translate(0, %i)' % innerHeight
        elif self.direction == 'down':
            attrib['transform'] = 'translate(0, 0)'
        layer = ElementTree.SubElement(trans, 'g', attrib=attrib)
        return layer

    def add_axis(self, trans):
        layer = ElementTree.SubElement(trans, 'g', attrib={'class':
            'axis-layer'})
        scale = self.options['scale']
        tick_text = map(scale.tickFormat(), scale.ticks())
        tick_pos = map(scale, scale.ticks())
        line_attr = {'style': 'stroke-width: 1px; stroke: #222;'}
        for pos, text in zip(tick_pos, tick_text):
            if self.direction == 'down':
                text_attr = {'style': 'text-anchor: middle;',
                        'x': '0', 'y': '-9', 'dy': '0em'}
                line_attr.update({'x2': '0', 'y2': '-6'})
                transform = 'translate(%.16f, 0)' % pos
            elif self.direction == 'right':
                text_attr = {'style': 'text-anchor: end;',
                        'x': '-9', 'y': '0', 'dy': '.32em'}
                line_attr.update({'x2': '-6', 'y2': '0'})
                transform = 'translate(0, %.16f)' % pos
            elif self.direction == 'left':
                text_attr = {'style': 'text-anchor: start;',
                        'x': '9', 'y': '0', 'dy': '.32em'}
                line_attr.update({'x2': '6', 'y2': '0'})
                transform = 'translate(0, %.16f)' % pos
            else:
                text_attr = {'style': 'text-anchor: middle;',
                        'x': '0', 'y': '9', 'dy': '.71em'}
                line_attr.update({'x2': '0', 'y2': '6'})
                transform = 'translate(%.16f, 0)' % pos
            attrib = {
                    'class': 'tick',
                    'transform': transform,
                    'style': 'opacity: 1;'
                    }
            group = ElementTree.SubElement(layer, 'g', attrib=attrib)
            ElementTree.SubElement(group, 'line', attrib=line_attr)
            thetext = ElementTree.SubElement(group, 'text', attrib=text_attr)
            thetext.text = text

    def add_timeline(self, trans):
        layer = ElementTree.SubElement(trans, 'g')
        innerWidth, innerHeight = self.getInnerDims()
        attrib = {'class': 'timeline'}
        if self.direction in ['up', 'down']:
             attrib['x2'] = str(innerWidth)
        else:
            attrib['y2'] = str(innerHeight)
        attrib['style'] = 'stroke-width: 2px; stroke: #222;'
        ElementTree.SubElement(layer, 'line', attrib=attrib)

    def add_dots(self, trans):
        layer = ElementTree.SubElement(trans, 'g', attrib={'class':
            'dot-layer'})
        attrib = {'class': 'dot', 'r': str(self.options['dotRadius'])}
        field = 'cx' if self.direction in ['up', 'down'] else 'cy'
        for i, node in enumerate(self.nodes):
            rgbstr = hex2rgbstr(self.dotColor(node.data.data, i))
            attrib['style'] = 'fill: %s;' % rgbstr
            attrib[field] = str(node.getRoot().idealPos)
            ElementTree.SubElement(layer, 'circle', attrib=attrib)

    def add_links(self, trans):
        layer = ElementTree.SubElement(trans, 'g', attrib={'class':
            'link-layer'})
        attrib = {'class': 'link'}
        for i, node in enumerate(self.nodes):
            thestyle = 'stroke: %s; ' % hex2rgbstr(self.linkColor(
                node.data.data, i))
            thestyle += 'stroke-width: 2; '
            thestyle += 'fill: none;'
            attrib['style'] = thestyle
            attrib['d'] = self.renderer.generatePath(node)
            ElementTree.SubElement(layer, 'path', attrib=attrib)

    def add_labels(self, trans):
        layer = ElementTree.SubElement(trans, 'g', attrib={'class':
            'label-layer'})
        if self.direction in ['left', 'right']:
            nodeHeight = max((n.w for n in self.nodes))
        else:
            nodeHeight = max((n.h for n in self.nodes))
        for i, node in enumerate(self.nodes):
            theg = ElementTree.SubElement(layer, 'g', attrib={
                'class': 'label-g',
                'transform': 'translate(%i, %i)' % self.nodePos(node,
                    nodeHeight)
                })
            ElementTree.SubElement(theg, 'rect', attrib={
                'class': 'label-bg',
                'rx': '2',
                'ry': '2',
                'width': str(node.w),
                'height': str(node.h),
                'style': 'fill: %s;' % hex2rgbstr(self.labelBgColor(
                    node.data.data, i))})
            if node.data.text:
                thetext = ElementTree.SubElement(theg, 'text', attrib={
                    'class': 'label-text',
                    'dy': self.options['textYOffset'],
                    'dx': self.options['textXOffset'],
                    'x': str(self.options['labelPadding']['left']),
                    'y': str(self.options['labelPadding']['top']),
                    'style': 'fill: %s;' % hex2rgbstr(self.labelTextColor(
                        node.data.data, i))
                    })
                thetext.text = node.data.text

class TimelineTex(Timeline):
    def __init__(self, items, options=None):
        self.nodes = None
        self.renderer = None
        super().__init__(items, options=options)

    def export(self, filename, build_pdf=True):
        self.nodes, self.renderer = self.compute()

        doc = []
        self.add_header(doc)
        self.add_timeline(doc)
        self.add_ticks(doc)
        self.add_labels(doc)
        self.add_dots(doc)
        self.add_links(doc)
        self.add_footer(doc)

        with open(filename, 'w') as fid:
            fid.write('\n'.join(doc))
        if build_pdf:
            fullname = os.path.realpath(filename)
            root = os.path.splitext(fullname)[0]
            output_name = root + ".pdf"
            build_latex_doc('\n'.join(doc), output_name=output_name)

    def add_header(self, doc):
        border = ("{left}bp {right}bp {bottom}bp {top}bp".format(
            **self.options['margin']))
        txt = ["\\documentclass[border={%s}]{standalone}" % border,
                "\\usepackage{tikz}",
                "\\usepackage{xcolor}",
                "\\usetikzlibrary{shapes.misc}",
                "\\usetikzlibrary{backgrounds}",
                ""]
        doc.extend(txt)
        self.add_header_colors(doc)
        self.add_header_ticks(doc)
        self.add_header_axis(doc)
        self.add_header_labels(doc)
        self.add_header_dots(doc)
        self.add_header_text(doc)
        doc.extend(["\\begin{document}", "\\begin{tikzpicture}[x=1bp,y=1bp]",
            ""])

    def add_header_colors(self, doc):
        # Define colors
        for i, node in enumerate(self.nodes):
            rgb = hex2rgbf(self.dotColor(node.data.data, i))
            doc.append("\\definecolor{dotColor%s}{rgb}{%f,%f,%f}" %
                    (int2name(i), rgb[0], rgb[1], rgb[2]))
        doc.append("")
        for i, node in enumerate(self.nodes):
            rgb = hex2rgbf(self.labelBgColor(node.data.data, i))
            doc.append("\\definecolor{labelBgColor%s}{rgb}{%f,%f,%f}" %
                    (int2name(i), rgb[0], rgb[1], rgb[2]))
        doc.append("")
        for i, node in enumerate(self.nodes):
            rgb = hex2rgbf(self.labelTextColor(node.data.data, i))
            doc.append("\\definecolor{labelTextColor%s}{rgb}{%f,%f,%f}" %
                    (int2name(i), rgb[0], rgb[1], rgb[2]))
        doc.append("")
        for i, node in enumerate(self.nodes):
            rgb = hex2rgbf(self.linkColor(node.data.data, i))
            doc.append("\\definecolor{linkColor%s}{rgb}{%f,%f,%f}" %
                    (int2name(i), rgb[0], rgb[1], rgb[2]))
        doc.append("")

    def add_header_ticks(self, doc):
        # Define ticks
        if not self.options['showTicks']:
            return
        scale = self.options['scale']
        tick_pos = map(scale, scale.ticks())
        for i, pos in enumerate(tick_pos):
            doc.append("\\def\\tick%s{%.8f}" % (int2name(i), pos))
        doc.append("")

    def add_header_axis(self, doc):
        # TODO Is this really necessary to define?
        # Define axis
        innerWidth, innerHeight = self.getInnerDims()
        doc.append("\\def\\axisL{0}")
        if self.direction in ['up', 'down']:
            doc.append("\\def\\axisR{%i}" % innerWidth)
        else:
            doc.append("\\def\\axisR{%i}" % innerHeight)
        doc.append("")

    def add_header_labels(self, doc):
        # Define labels
        if self.direction in ['left', 'right']:
            nodeHeight = max((n.w for n in self.nodes))
        else:
            nodeHeight = max((n.h for n in self.nodes))

        for i, node in enumerate(self.nodes):
            doc.append("\\def\\label%sx{%.8f}" % (int2name(i),
                self.nodePos(node, nodeHeight)[0]))
            doc.append("\\def\\label%sy{%.8f}" % (int2name(i),
                self.nodePos(node, nodeHeight)[1]))
        doc.append("")

    def add_header_dots(self, doc):
        # Define dots
        for i, node in enumerate(self.nodes):
            doc.append("\\def\\dot%sx{%.8f}" % (int2name(i),
                node.getRoot().idealPos))
        doc.append("")

    def add_header_text(self, doc):
        # Define text
        for i, node in enumerate(self.nodes):
            if node.data.text:
                doc.append("\\def\\text%s{%s}" % (int2name(i),
                    node.data.text))
        doc.append("")

    def add_timeline(self, doc):
        doc.append("% axis")
        if self.direction in ['up', 'down']:
            doc.append("\\draw[thick] (\\axisL, 0) -- (\\axisR, 0);")
        else:
            doc.append("\\draw[thick] (0, \\axisR) -- (0, \\axisL);")
        doc.append("")

    def add_ticks(self, doc):
        if not self.options['showTicks']:
            return
        doc.append("% ticks")
        scale = self.options['scale']
        tick_text = map(scale.tickFormat(), scale.ticks())
        for i, text in enumerate(tick_text):
            t = "\\tick%s" % int2name(i)
            doc.append("\\draw (%s, 5pt) -- (%s, -5pt)\n"
                    "node[anchor=north] {%s};" % (t, t, text))
        doc.append("")

    def add_labels(self, doc):
        doc.append("% labels")
        for i, node in enumerate(self.nodes):
            ID = int2name(i)
            lblx = "\\label%sx" % ID
            lbly = "\\label%sy" % ID
            txt = "\\text%s" % ID if node.data.text else ""
            doc.append("\\filldraw[fill=labelBgColor%s, draw=labelBgColor%s, "
                    "rounded corners=2pt]\n"
                    "(%s, %s) rectangle (%s+%f, %s+%f)\n"
                    "node[pos=0.5, text=labelTextColor%s] (lbl%s) {%s};" %
                    (ID, ID, lblx, lbly, lblx, node.w, lbly, node.h, ID, ID,
                        txt))
        doc.append("")

    def add_dots(self, doc):
        doc.append("% dots")
        for i, node in enumerate(self.nodes):
            ID = int2name(i)
            txt = ("\\draw node [circle, inner sep=0pt, minimum "
                    "size=%spt, \nfill=dotColor%s] (circ%s) at " % 
                    (str(self.options['dotRadius']), ID, ID))
            if self.direction in ['up', 'down']:
                txt += "(\\dot%sx, 0) {};" % ID
            else:
                txt += "(0, \\dot%sx) {};" % ID
            doc.append(txt)
        doc.append("")

    def add_links(self, doc):
        doc.append("% links")
        doc.append("\\begin{scope}[on background layer]")
        for i, node in enumerate(self.nodes):
            ID = int2name(i)
            txt = "\\path[shorten >= -1pt, shorten <= -1pt]\n"
            if self.direction == 'down':
                txt += "(lbl%s.south) edge[out=-90, in=90, " % ID
            elif self.direction == 'up':
                txt += "(lbl%s.north) edge[out=90, in=-90, " % ID
            elif self.direction == "left":
                txt += "(lbl%s.east) edge[out=0, in=180, " % ID
            else:
                txt += "(lbl%s.west) edge[out=180, in=0, " % ID
            txt += "color=linkColor%s, very thick] (circ%s);" % (ID, ID)
            doc.append(txt)
        doc.append("\\end{scope}")
        doc.append("")

    def add_footer(self, doc):
        doc.append("\\end{tikzpicture}")
        doc.append("\\end{document}")

