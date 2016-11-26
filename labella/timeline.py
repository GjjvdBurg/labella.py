
"""
This class is not included in the original Labella.js, but is modelled on
https://kristw.github.io/d3kit-timeline/

The idea is to make a simple timeline of objects which have text or no text.
Items must be added as dicts: {'time': value, 'width': int, 'text': str} where
the 'text' field and the 'width' field are optional and the value field can be
either a date(time) instance or a float. The type must be the same for all
values.

"""

import datetime
import math
import os

from xml.etree import ElementTree

from labella.force import Force
from labella.node import Node
from labella.renderer import Renderer
from labella.scale import TimeScale, d3_extent
from labella.tex import text_dimensions, build_latex_doc, uni2tex
from labella.utils import int2name, hex2rgbf, hex2rgbstr

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
        'borderColor': '#000',
        'showBorder': False,
        'latex': {
            'fontsize': '11pt',
            'borderThickness': 'very thick',
            'axisThickness': 'very thick',
            'tickThickness': 'thick',
            'linkThickness': 'very thick',
            'tickCross': False,
            'preamble': ''
            }
        }

def d3_functor(v):
    if callable(v):
        return v
    return lambda x : v

class Item(object):
    def __init__(self, time, width=DEFAULT_WIDTH, text=None, data=None,
            output_mode='svg', tex_fontsize='11pt', tex_preamble=None):
        self.time = time
        self.text = text
        self.width = width
        self.data = data
        self.output_mode = output_mode
        self.tex_fontsize = tex_fontsize
        self.tex_preamble = tex_preamble
        if self.width is None and self.text:
            self.width, self.height = self.get_text_dimensions()
        else:
            self.height = 13.0

    def get_text_dimensions(self):
        if self.output_mode == 'svg':
            width, height = text_dimensions(self.text, fontsize='12pt')
            width = math.ceil(width)
            height = 14.0
        else:
            width, height = text_dimensions(self.text,
                    fontsize=self.tex_fontsize, preamble=self.tex_preamble)
            width = math.ceil(width) + 4
            height += 4
        return width, height

    def __str__(self):
        s = ("Item(time=%r, text=%r, width=%r, height=%r, data=%r)" %
                (self.time, self.text, self.width, self.height, self.data))
        return s

    def __repr__(self):
        return str(self)

class Timeline(object):
    def __init__(self, dicts, options=None, output_mode='svg'):
        # update latex options
        latex_opts = {k:v for k,v in DEFAULT_OPTIONS['latex'].items()}
        if 'latex' in options:
            latex_opts.update(options['latex'])
        options['latex'] = latex_opts
        # update timeline options
        self.options = {k:v for k,v in DEFAULT_OPTIONS.items()}
        if options:
            self.options.update(options)
        self.direction = self.options['direction']
        self.options['labella']['direction'] = self.direction
        # parse items
        self.items = self.parse_items(dicts, output_mode=output_mode)
        self.equal_heights()
        self.rotate_items()
        self.init_axis(dicts)

    def equal_heights(self):
        maxheight = max((x.height for x in self.items))
        for item in self.items:
            if item.text:
                item.height = maxheight

    def rotate_items(self):
        if self.direction in ['left', 'right']:
            for item in self.items:
                if item.text:
                    item.height, item.width = item.width, item.height

    def parse_items(self, dicts, output_mode='svg'):
        items = []
        for d in dicts:
            time = d['time']
            if isinstance(time, datetime.date):
                time = datetime.datetime.combine(time,
                        datetime.datetime.min.time())
                d['time'] = time
            elif isinstance(time, datetime.time):
                time = datetime.datetime.combine(datetime.date.today(), time)
                d['time'] = time
            text = self.textFn(d)
            if text:
                width = d.get('width', None)
            else:
                width = d.get('width', DEFAULT_WIDTH)
            it = Item(time, width=width, text=text, data=d,
                    output_mode=output_mode,
                    tex_fontsize=self.options['latex']['fontsize'], 
                    tex_preamble=self.options['latex']['preamble'])
            items.append(it)
        return items

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
                node.width = node.h
            else:
                node.width = node.w
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

    def colorFunc(self, colorName, thedict, i=0):
        if isinstance(self.options[colorName], list):
            return self.options[colorName][i%len(self.options[colorName])]
        theColor = d3_functor(self.options[colorName])
        return theColor(thedict)

    def dotColor(self, thedict, i=0):
        return self.colorFunc('dotColor', thedict, i=i)

    def linkColor(self, thedict, i=0):
        return self.colorFunc('linkColor', thedict, i=i)

    def labelBgColor(self, thedict, i=0):
        return self.colorFunc('labelBgColor', thedict, i=i)

    def labelTextColor(self, thedict, i=0):
        return self.colorFunc('labelTextColor', thedict, i=i)

    def borderColor(self, thedict, i=0):
        return self.colorFunc('borderColor', thedict, i=i)

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
        super().__init__(items, options=options, output_mode='svg')

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
        svglines = ElementTree.tostring(doc)
        with open(filename, 'wb') as fid:
            fid.write(svglines)
        return svglines

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
            thestyle = ('fill:%s;' % 
                    hex2rgbstr(self.labelBgColor(node.data.data, i)))
            if self.options['showBorder']:
                thestyle += ('stroke-width:1;stroke:%s' % 
                        hex2rgbstr(self.borderColor(node.data.data, i)))
            ElementTree.SubElement(theg, 'rect', attrib={
                'class': 'label-bg',
                'rx': '2',
                'ry': '2',
                'width': str(node.w),
                'height': str(node.h),
                'style': thestyle
                })
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
        super().__init__(items, options=options, output_mode='tex')

    def export(self, filename, build_pdf=True):
        self.nodes, self.renderer = self.compute()

        doc = []
        self.add_header(doc)
        self.add_margin(doc)
        self.add_main(doc)
        self.add_timeline(doc)
        if self.options['showTicks']:
            self.add_axis(doc)
        self.add_links(doc)
        self.add_labels(doc)
        self.add_dots(doc)
        self.close_scope(doc) # main
        self.close_scope(doc) # margin
        self.add_footer(doc)

        texlines = '\n'.join(doc)
        with open(filename, 'w') as fid:
            fid.write(texlines)
        if build_pdf:
            fullname = os.path.realpath(filename)
            root = os.path.splitext(fullname)[0]
            output_name = root + ".pdf"
            build_latex_doc(texlines, output_name=output_name)
        return texlines

    def add_header(self, doc):
        border = ("%fbp %fbp %fbp %fbp" % (self.options['margin']['left'], 
            self.options['margin']['bottom'], self.options['margin']['right'], 
            self.options['margin']['top']))
        fontsize = self.options['latex']['fontsize']
        txt = ["\\documentclass[border={%s}, %s]{standalone}" % (border,
            fontsize),
                self.options['latex']['preamble'],
                "\\usepackage{tikz}",
                "\\usepackage{xcolor}",
                "\\usetikzlibrary{shapes.misc}",
                "\\usetikzlibrary{backgrounds}",
                ""]
        doc.extend(txt)
        self.add_header_colors(doc)
        self.add_header_text(doc)
        doc.extend(["\\begin{document}", "\\begin{tikzpicture}[x=1bp,y=-1bp]",
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
        for i, node in enumerate(self.nodes):
            if not self.options['showBorder']:
                return
            rgb = hex2rgbf(self.borderColor(node.data.data, i))
            doc.append("\\definecolor{borderColor%s}{rgb}{%f,%f,%f}" % 
                    (int2name(i), rgb[0], rgb[1], rgb[2]))
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

    def add_header_text(self, doc):
        # Define text
        for i, node in enumerate(self.nodes):
            if node.data.text:
                doc.append("\\def\\text%s{%s}" % (int2name(i),
                    uni2tex(node.data.text)))
        doc.append("")

    def add_margin(self, doc):
        x = self.options['margin']['left']
        y = self.options['margin']['right']
        doc.append("% shift for the margin")
        doc.append("\\begin{scope}[shift={(%i, %i)}]" % (x, y))

    def close_scope(self, doc):
        doc.append("\\end{scope}")

    def add_main(self, doc):
        innerWidth, innerHeight = self.getInnerDims()
        doc.append("% main layer")
        if self.direction in ['right', 'down']:
            x, y = 0, 0
        elif self.direction == 'left':
            x, y = innerWidth, 0
        else:
            x, y = 0, innerHeight
        doc.append("\\begin{scope}[shift={(%i, %i)}]" % (x, y))

    def add_timeline(self, doc):
        innerWidth, innerHeight = self.getInnerDims()
        doc.append("% axis")
        doc.append("\\begin{scope}")
        if self.direction in ['up', 'down']:
            doc.append("\\draw[%s] (0, 0) -- (%i, 0);" %
                    (self.options['latex']['axisThickness'], innerWidth))
        else:
            doc.append("\\draw[%s] (0, 0) -- (0, %i);" %
                    (self.options['latex']['axisThickness'], innerHeight))
        doc.append("\\end{scope}")
        doc.append("")

    def add_axis(self, doc):
        doc.append("% axis layer")
        doc.append("\\begin{scope}")
        scale = self.options['scale']
        tick_pos = map(scale, scale.ticks())
        tick_text = map(scale.tickFormat(), scale.ticks())
        if self.options['latex']['tickCross']:
            tickstart = '6pt'
        else:
            tickstart = '0'
        for i, tup in enumerate(zip(tick_pos, tick_text)):
            pos, text = tup
            if self.direction == 'up':
                txt = "\\begin{scope}[shift={(%i, %i)}]\n" % (pos, 0)
                txt += ("\\draw[%s] (0, %s) -- (0, -6pt)\n" %
                        (self.options['latex']['tickThickness'], tickstart))
                txt += "node[anchor=north] {%s};" % (text)
            elif self.direction == 'down':
                txt = "\\begin{scope}[shift={(%i, %i)}]\n" % (pos, 0)
                txt += ("\\draw[%s] (0, -%s) -- (0, 6pt)\n" %
                        (self.options['latex']['tickThickness'], tickstart))
                txt += "node[anchor=south] {%s};" % (text)
            elif self.direction == 'left':
                txt = "\\begin{scope}[shift={(%i, %i)}]\n" % (0, pos)
                txt += ("\\draw[%s] (-%s, 0) -- (6pt, 0)\n" %
                        (self.options['latex']['tickThickness'], tickstart))
                txt += "node[anchor=west] {%s};" % (text)
            else:
                txt = "\\begin{scope}[shift={(%i, %i)}]\n" % (0, pos)
                txt += ("\\draw[%s] (%s, 0) -- (-6pt, 0)\n" %
                        (self.options['latex']['tickThickness'], tickstart))
                txt += "node[anchor=east] {%s};" % (text)
            doc.append(txt)
            doc.append("\\end{scope}")
        doc.append("\\end{scope}")
        doc.append("")

    def add_links(self, doc):
        doc.append("% link layer")
        doc.append("\\begin{scope}")
        for i, node in enumerate(self.nodes):
            ID = int2name(i)
            lineSteps = self.renderer.generatePath(node, tikz=True)
            txt = ""
            currentPos = ('0', '0')
            lineopts = "color=linkColor%s, %s" % (ID,
                    self.options['latex']['linkThickness'])
            for step in lineSteps:
                if step.startswith('M'):
                    currentPos = step.split(' ')[1:]
                elif step.startswith('C'):
                    points = step.split(' ')[1:]
                    if txt:
                        txt += "\n"
                    txt += "\\draw[%s] (%s, %s) .. " % (lineopts,
                            currentPos[0], currentPos[1])
                    txt += "controls\n(%s, %s) " % (points[0], points[1])
                    txt += "and (%s, %s) " % (points[2], points[3])
                    txt += ".. (%s, %s);" % (points[4], points[5])
                    currentPos = (points[4], points[5])
                elif step.startswith('L'):
                    points = step.split(' ')[1:]
                    if txt:
                        txt += "\n"
                    txt += "\\draw[%s] (%s, %s) -- (%s, %s);" % (lineopts,
                            currentPos[0], currentPos[1], points[0],
                            points[1])
                    currentPos = (points[0], points[1])
            doc.append(txt)
        doc.append("\\end{scope}")
        doc.append("")

    def add_labels(self, doc):
        doc.append("% label layer")
        doc.append("\\begin{scope}")

        if self.direction in ['left', 'right']:
            nodeHeight = max((n.w for n in self.nodes))
        else:
            nodeHeight = max((n.h for n in self.nodes))

        for i, node in enumerate(self.nodes):
            ID = int2name(i)
            txt = "\\text%s" % ID if node.data.text else ""
            doc.append("\\begin{scope}[shift={(%i, %i)}]" %
                    (self.nodePos(node, nodeHeight)))
            if self.options['showBorder']:
                doc.append("\\draw[%s, borderColor%s, fill=labelBgColor%s, "
                        "rounded corners=2pt]\n"
                        "(0, 0) rectangle (%s, %s) node[midway, yshift=-.75bp,"
                        " anchor=center, text=labelTextColor%s] {\\strut %s};" 
                        % (self.options['latex']['borderThickness'], ID, ID, 
                            str(node.w), str(node.h), ID, txt))
            else:
                doc.append("\\fill[color=labelBgColor%s, rounded corners=2pt]\n"
                        "(0, 0) rectangle (%s, %s) node[midway, yshift=-.75bp, "
                        "anchor=center, text=labelTextColor%s] {\\strut %s};" % 
                        (ID, str(node.w), str(node.h), ID, txt))
            doc.append("\\end{scope}")
        doc.append("\\end{scope}")
        doc.append("")

    def add_dots(self, doc):
        doc.append("% dots")
        doc.append("\\begin{scope}")
        for i, node in enumerate(self.nodes):
            ID = int2name(i)
            # factor 2 added for visual similarity between pdf and svg
            txt = ("\\draw node [circle, inner sep=0pt, minimum "
                    "size=%sbp, \nfill=dotColor%s] at " %
                    (str(2*self.options['dotRadius']), ID))
            if self.direction in ['up', 'down']:
                txt += "(%f, 0) {};" % (node.getRoot().idealPos)
            else:
                txt += "(0, %f) {};" % (node.getRoot().idealPos)
            doc.append(txt)
        doc.append("\\end{scope}")
        doc.append("")

    def add_footer(self, doc):
        doc.append("\\end{tikzpicture}")
        doc.append("\\end{document}")
