
"""
This class is not included in the original Labella.js.

The idea is to make a simple timeline of objects which have text or no text.
Items must be added as either:

    dicts: {'time': value, 'width': int, 'name': str} where the 'name' field
    and the 'width' field are optional and the value field can be either a
    date(time) instance or a float. The type must be the same for all values.

or as date(time) objects:

    numbers: [date(time), date(time), date(time)]

or as

    numbers: [float, float, float]

"""

import datetime

from xml.etree import ElementTree

from labella.force import Force
from labella.node import Node
from labella.renderer import Renderer
from labella.utils import hex2rgbstr

DEFAULT_WIDTH = 50

DEFAULT_OPTIONS = {
        'margin': {'left': 20, 'right': 20, 'top': 20, 'bottom': 20},
        'initialWidth': 400,
        'initialHeight': 400,
        'scale': None,
        'domain': None,
        'direction': 'right',
        'dotRadius': 3,
        'layerGap': 60,
        'labella': {},
        'keyFn': None,
        'timeFn': None,
        'textFn': None,
        'dotColor': '#222222',
        'labelBgColor': '#222222',
        'labelTextColor': '#ffffff',
        'linkColor': '#222222',
        'labelPadding': {'left': 4, 'right': 4, 'top': 3, 'bottom': 2},
        'textYOffset': '0.85em',
        }

class Item(object):
    def __init__(self, time, width=DEFAULT_WIDTH, name=None,
            numeric_value=None, data=None):
        self.time = time
        self.name = name
        self.numeric_value = numeric_value
        self.width = width
        if self.width is None and self.name:
            self.width = self.magic_width_function(self.name)
        self.height = self.magic_height_function(self.name)
        self.data = data

    def to_node(self, output_mode):
        return Node(self.numeric_value, self.width, data=self)

    def magic_width_function(self, text):
        return len(text) * 8.0

    def magic_height_function(self, text):
        return 12.0

    def __str__(self):
        s = ("Item(time=%r, name=%r, numeric_value=%r, width=%r,"
                " height=%r, data=%r)" % (self.time, self.name, 
                    self.numeric_value, self.width, self.height, self.data))
        return s
    def __repr__(self):
        return str(self)

class Timeline(object):
    def __init__(self, items, options=None):
        # update timeline options
        self.options = {k:v for k,v in DEFAULT_OPTIONS.items()}
        if options:
            self.options.update(options)
        self.direction = self.options['direction']
        self.options['labella']['direction'] = self.direction
        # parse items
        self.items = self.parse_items(items)

    def parse_items(self, items):
        if isinstance(items[0], dict):
            assert(all([isinstance(x, dict) for x in items]))
            return self.parse_dicts(items)
        elif isinstance(items[0], datetime.datetime):
            assert(all([isinstance(x, datetime.datetime) for x in items]))
            return self.parse_datetimes(items)
        elif isinstance(items[0], datetime.date):
            assert(all([isinstance(x, datetime.date) for x in items]))
            return self.parse_dates(items)
        else:
            return self.parse_numbers(items)

    def parse_dicts(self, dicts):
        items = []
        for d in dicts:
            time = d['time']
            name = d.get('name', None)
            if name:
                width = d.get('width', None)
            else:
                width = d.get('width', DEFAULT_WIDTH)
            it = self.parse_time(time, width=width, name=name, data=d)
            items.append(it)
        #self.scale_items(items)
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

    def parse_time(self, time, width=None, name=None, data=None):
        if isinstance(time, datetime.datetime):
            it = Item(time, numeric_value=time.timestamp(), name=name,
                    width=width, data=data)
        elif isinstance(time, datetime.date):
            it = Item(time, numeric_value=time.toordinal(), name=name,
                    width=width, data=data)
        else:
            it = Item(time, numeric_value=time, name=name, width=width,
                    data=data)
        return it

    def parse_datetimes(self, datetimes):
        innerWidth, innerHeight = self.getInnerDims()
        items = [self.parse_time(dt) for dt in datetimes]
        return items

    def parse_dates(self, dates):
        innerWidth, innerHeight = self.getInnerDims()
        items = [self.parse_time(d) for d in dates]
        return items

    def parse_numbers(self, numbers):
        items = [self.parse_time(n) for n in numbers]
        return items

    def getInnerDims(self):
        innerWidth = (self.options['initialWidth'] -
                self.options['margin']['left'] -
                self.options['margin']['right'])
        innerHeight = (self.options['initialHeight'] -
                self.options['margin']['top'] -
                self.options['margin']['bottom'])
        return innerWidth, innerHeight

    def get_nodes(self, output_mode):
        nodes = [it.to_node(output_mode) for it in self.items]
        for node in nodes:
            node.w = (node.data.width + self.options['labelPadding']['left'] +
                    self.options['labelPadding']['right'])
            node.h = (node.data.height + self.options['labelPadding']['top'] +
                    self.options['labelPadding']['bottom'])
            if self.options['direction'] in ['left', 'right']:
                node.h, node.w = node.w, node.h
        return nodes

    def compute(self, output_mode):
        nodes = self.get_nodes(output_mode)
        renderer = Renderer(self.options['labella'])
        renderer.layout(nodes)
        force = Force(self.options['labella'])
        force.nodes(nodes)
        force.compute()
        newnodes = force.nodes()
        renderer.layout(newnodes)
        from pprint import pprint
        pprint(force.options)
        pprint(renderer.options)
        pprint(newnodes)
        return newnodes, renderer

class TimelineSVG(Timeline):
    def __init__(self, items, options=None):
        self.nodes = None
        self.renderer = None
        super().__init__(items, options=options)

    def export(self, filename):
        self.nodes, self.renderer = self.compute('svg')
        initWidth, initHeight = (self.options['initialWidth'],
                self.options['initialHeight'])
        doc = ElementTree.Element('svg', width=str(initWidth),
                height=str(initHeight))
        transform = self.getTranslation()
        trans = ElementTree.SubElement(doc, 'g', transform=transform)
        ElementTree.SubElement(trans, 'g', attrib={'class': 'dummy-layer'})
        mainLayer = self.add_main(trans)
        self.add_timeline(mainLayer)
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

    def dotColor(self, idx):
        if isinstance(self.options['dotColor'], str):
            return self.options['dotColor']
        return self.options['dotColor'](idx)

    def add_dots(self, trans):
        layer = ElementTree.SubElement(trans, 'g', attrib={'class': 
            'dot-layer'})
        attrib = {'class': 'dot', 'r': str(self.options['dotRadius'])}
        field = 'cx' if self.direction in ['up', 'down'] else 'cy'
        for i, node in enumerate(self.nodes):
            rgbstr = hex2rgbstr(self.dotColor(i))
            attrib['style'] = 'fill: %s;' % rgbstr
            attrib[field] = str(node.getRoot().idealPos)
            ElementTree.SubElement(layer, 'circle', attrib=attrib)

    def linkColor(self, idx):
        if isinstance(self.options['linkColor'], str):
            return self.options['linkColor']
        return self.options['linkColor'](idx)

    def add_links(self, trans):
        layer = ElementTree.SubElement(trans, 'g', attrib={'class': 
            'link-layer'})
        attrib = {'class': 'link'}
        for i, node in enumerate(self.nodes):
            thestyle = 'stroke: %s; ' % hex2rgbstr(self.linkColor(i))
            thestyle += 'stroke-width: 2; '
            thestyle += 'opacity: 0.6; '
            thestyle += 'fill: none;'
            attrib['style'] = thestyle
            attrib['d'] = self.renderer.generatePath(node)
            ElementTree.SubElement(layer, 'path', attrib=attrib)

    def nodePos(self, d, nodeHeight):
        if self.direction == 'right':
            return 'translate(%i, %i)' % (d.x, d.y - d.dy/2)
        elif self.direction == 'left':
            return 'translate(%i, %i)' % (d.x + nodeHeight - d.w, d.y - 
                    d.dy/2)
        elif self.direction == 'up':
            return 'translate(%i, %i)' % (d.x - d.dx/2, d.y)
        elif self.direction == 'down':
            return 'translate(%i, %i)' % (d.x - d.dx/2, d.y)

    def labelBgColor(self, idx):
        if isinstance(self.options['labelBgColor'], str):
            return self.options['labelBgColor']
        return self.options['labelBgColor'](idx)

    def labelTextColor(self, idx):
        if isinstance(self.options['labelTextColor'], str):
            return self.options['labelTextColor']
        return self.options['labelTextColor'](idx)

    def textFn(self, item):
        if self.options['textFn'] is None:
            return item.name if item.name else ''
        return self.options['textFn'](item)

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
                'transform': self.nodePos(node, nodeHeight)
                })
            ElementTree.SubElement(theg, 'rect', attrib={
                'class': 'label-bg',
                'rx': '2',
                'ry': '2',
                'width': str(node.w),
                'height': str(node.h),
                'style': 'fill: %s;' % hex2rgbstr(self.labelBgColor(i))})
            thetext = ElementTree.SubElement(theg, 'text', attrib={
                'class': 'label-text',
                'dy': self.options['textYOffset'],
                'x': str(self.options['labelPadding']['left']),
                'y': str(self.options['labelPadding']['top']),
                'style': 'fill: %s;' % hex2rgbstr(self.labelTextColor(i))
                })
            thetext.text = self.textFn(node.data)

