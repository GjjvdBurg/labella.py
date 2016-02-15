from . import distributor
from . import removeOverlap
from . import metrics

DEFAULT_OPTIONS = {
        'nodeSpacing': 3,
        'minPos': 0,
        'maxPos': None,
        'algorithm': 'overlap',
        'density': 0.85,
        'stubWidth': 1
        }

class Force(object):
    def __init__(self, options=None):
        self.force = {}
        self.options = {k:v for k,v in DEFAULT_OPTIONS.items()}
        self.distributor = distributor.Distributor()
        self._nodes = []
        self.layers = None
        self.set_options(options)

    def set_options(self, x=None):
        if x is None:
            x = {}
        self.options.update(x)

        disOptions = {k:v for k,v in self.options.items() if k in 
                distributor.DEFAULT_OPTIONS}
        if (('minPos' in self.options) and (not self.options['minPos'] is 
            None) and ('maxPos' in self.options) and (not 
                self.options['maxPos'] is None)):
            disOptions['layerWidth'] = (self.options['maxPos'] - 
                    self.options['minPos'])
        else:
            disOptions['layerWidth'] = None
        self.distributor.options.update(disOptions)

    def nodes(self, x=None):
        if not x:
            return self._nodes
        self._nodes = x
        self.layers = None

    def getLayers(self):
        return self.layers

    def compute(self):
        simOptions = {k:v for k, v in self.options.items() if k in
                removeOverlap.DEFAULT_OPTIONS}

        for node in self._nodes:
            node.removeStub()

        layers = self.distributor.distribute(self._nodes)
        for layerIndex, nodes in enumerate(layers):
            for node in nodes:
                node.layerIndex = layerIndex
            removeOverlap.removeOverlap(nodes, simOptions)

    def metrics(self):
        methods = [m for m in dir(metrics) if not m.startswith('_')]
        out = [{'name': name, 'value': self.metric(name)} for name in methods]
        return out

    def metric(self, name):
        if name == 'overflow':
            return getattr(metrics, name)(self.layers, self.options['minPos'], 
                    self.options['maxPos'])
        elif name == 'overDensity':
            return getattr(metrics, name)(self.layers, 
                    self.options['density'], self.options['layerWidth'], 
                    self.options['nodeSpacing']-1)
        elif name == 'overlapCount':
            return getattr(metrics, name)(self.layers, 
                    self.options['nodeSpacing'] - 1)
        else:
            if getattr(metrics, name):
                return getattr(metrics, name)(self.layers)
            else:
                return None
