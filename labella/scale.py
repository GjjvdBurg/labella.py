"""
"""

import math

from datetime import datetime

from labella.d3_time import d3_time

d3_identity = lambda x : x
dt2milli = lambda x : x.timestamp() * 1000.0
milli2dt = lambda x : datetime.fromtimestamp(x / 1000.0)

def drange(start, stop, step=1):
    r = start
    while r < stop:
        yield r
        r += step

def d3_scale_bilinear(domain, _range, uninterpolate, interpolate):
    u = uninterpolate(domain[0], domain[1])
    i = interpolate(_range[0], _range[1])
    return lambda x: i(u(x))

def d3_uninterpolateNumber(a, b):
    return lambda x : (x - a) / (b - a)

def d3_uninterpolateClamp(a, b):
    return lambda x : max(0, min(1, (x - a) / (b - a)))

def d3_interpolate(a, b):
    return d3_interpolateNumber(a, b)

def d3_interpolateNumber(a, b):
    return lambda t : a * (1 - t) + b * t

def d3_extent(data, fn):
    minval = min([fn(x) for x in data])
    maxval = max([fn(x) for x in data])
    return [minval, maxval]

def d3_scaleExtent(domain):
    start = domain[0]
    stop = domain[len(domain) - 1]
    if start < stop:
        return [start, stop]
    return [stop, start]

def d3_scale_nice(domain, nice):
    i0 = 0
    i1 = len(domain) - 1
    x0 = domain[i0]
    x1 = domain[i1]
    dx = None
    if (x1 < x0):
        dx = i0
        i0 = i1
        i1 = dx
        dx = x0
        x0 = x1
        x1 = dx
    if isinstance(nice, dict):
        domain[i0] = nice['floor'](x0)
        domain[i1] = nice['ceil'](x1)
    else:
        domain[i0] = nice.floor(x0)
        domain[i1] = nice.ceil(x1)
    return domain

def d3_scale_niceStep(step):
    if step:
        return {'floor': lambda x: math.floor(x / step) * step,
                'ceil': lambda x: math.ceil(x / step) * step}
    else:
        return {'floor': lambda x : x,
                'ceil': lambda x : x}

def d3_scale_linearTickRange(domain, m=None):
    if m is None:
        m = 10

    extent = d3_scaleExtent(domain)
    span = extent[1] - extent[0]
    if span == 0:
        extent.append(0)
        return extent
    step = pow(10, math.floor(math.log(span / m) / math.log(10)))
    err = m / span * step

    if err <= 0.15:
        step *= 10
    elif err <= 0.35:
        step *= 5
    elif err <= 0.75:
        step *= 2

    extent[0] = math.ceil(extent[0] / step) * step
    extent[1] = math.floor(extent[1] / step) * step + step * 0.5
    if len(extent) == 2:
        extent.append(step)
    else:
        extent[2] = step
    return extent

def d3_scale_linearTicks(domain, m):
    return drange(*d3_scale_linearTickRange(domain, m))

def d3_scale_linearTickFormat(domain, m, fmt=None):
    therange = d3_scale_linearTickRange(domain, m)
    # format not None is not implemented
    decimals = max(0, d3_scale_linearPrecision(therange[2]))
    fmt = "." + str(decimals) + "f"
    fmtstr = '{:%s}' % fmt
    return lambda x : fmtstr.format(x)

def d3_scale_linearPrecision(value):
    return -math.floor(math.log(value) / math.log(10) + 0.01)

def d3_scale_linearNice(domain, m=None):
    d3_scale_nice(domain, d3_scale_niceStep(d3_scale_linearTickRange(domain, 
        m)[2]))
    d3_scale_nice(domain, d3_scale_niceStep(d3_scale_linearTickRange(domain, 
        m)[2]))
    return domain

### Date ###

def zero_fill_right_shift(data, bits):
    return (data & 0xffffffff) >> bits

def d3_ascending(a, b):
    if a < b:
        return -1
    if a > b:
        return 1
    if a >= b:
        return 0
    return None

def d3_bisect(a, x, lo=0, hi=None):
    # implements d3_bisect.right, ascending
    if hi is None:
        hi = len(a)
    while lo < hi:
        mid = zero_fill_right_shift(lo + hi, 1)
        if a[mid] > x:
            hi = mid
        else:
            lo = mid + 1
    return lo

def time_nice_floor(date, skipped, interval):
    newdate = interval.floor(date)
    while skipped(newdate):
        newdate = milli2dt(dt2milli(newdate) - 1)
        newdate = interval.floor(newdate)
    return newdate

def time_nice_ceil(date, skipped, interval):
    newdate = interval.ceil(date)
    while skipped(newdate):
        newdate = milli2dt(dt2milli(newdate) + 1)
        newdate = interval.ceil(newdate)
    return newdate

class d3TimeScaleMilliseconds(object):
    def __init__(self):
        pass

    def range(self, start, stop, step):
        return list(map(milli2dt, range(math.ceil(int(start.timestamp() * 
            1000) / step) * step, int(stop.timestamp() * 1000), step)))
    def floor(self, x):
        return x
    def ceil(self, x):
        return x

d3_time_scaleMilliseconds = d3TimeScaleMilliseconds()

d3_time_scaleSteps = [
        1e3,    # 1-second
        5e3,    # 5-second
        15e3,   # 15-second
        3e4,    # 30-second
        6e4,    # 1-minute
        3e5,    # 5-minute
        9e5,    # 15-minute
        18e5,   # 30-minute
        36e5,   # 1-hour
        108e5,  # 3-hour
        216e5,  # 6-hour
        432e5,  # 12-hour
        864e5,  # 1-day
        1728e5, # 2-day
        6048e5, # 1-week
        2592e6, # 1-month
        7776e6, # 3-month
        31536e6 # 1-year
        ]

d3_time_scaleLocalMethods = [
        [d3_time['second'], 1],
        [d3_time['second'], 5],
        [d3_time['second'], 15],
        [d3_time['second'], 30],
        [d3_time['minute'], 1],
        [d3_time['minute'], 5],
        [d3_time['minute'], 15],
        [d3_time['minute'], 30],
        [d3_time['hour'], 1],
        [d3_time['hour'], 3],
        [d3_time['hour'], 6],
        [d3_time['hour'], 12],
        [d3_time['day'], 1],
        [d3_time['day'], 2],
        [d3_time['week'], 1],
        [d3_time['month'], 1],
        [d3_time['month'], 3],
        [d3_time['year'], 1]
        ]

def d3_time_formatMulti(formats):
    def local_func(date):
        i = 0
        f = formats[i]
        while (not f[1](date)):
            i += 1
            f = formats[i]
        return f[0](date)
    return local_func

def mytimeformat(date):
    if date.day == 1 and date.month == 1:
        return date.strftime("%Y")
    elif date.day == 1:
        return date.strftime("%B")
    elif (date.isoweekday() == 7 and date.hour == 0 and date.minute == 0 and 
            date.second == 0):
        return date.strftime("%b %d")
    elif (date.hour == 0 and date.minute == 0 and date.second == 0):
        return date.strftime("%a %d")
    elif (date.minute == 0 and date.second == 0):
        return date.strftime("%I %p")
    elif (date.second == 0):
        return date.strftime("%H:%M")
    else:
        return date.strftime(":%S")

######################################################################

class LinearScale(object):

    def __init__(self, domain=None, _range=None, interpolate=None, 
            clamp=False):
        self._domain = [0, 1] if domain is None else domain
        self._range = [0, 1] if _range is None else _range
        self._interpolate = (d3_interpolate if interpolate is None else 
                interpolate)
        self._clamp = clamp

        self._output = None
        self._input = None
        self.rescale()

    def rescale(self):
        linear = d3_scale_bilinear
        if self._clamp:
            uninterpolate = d3_uninterpolateClamp
        else:
            uninterpolate = d3_uninterpolateNumber
        self._output = linear(self._domain, self._range, uninterpolate, 
                self._interpolate)
        self._input = linear(self._range, self._domain, uninterpolate, 
                d3_interpolate)
        return self

    def scale(self, x):
        return self._output(x)

    def invert(self, y):
        return self._input(y)

    def domain(self, x=None):
        if x is None:
            return self._domain
        self._domain = list(map(float, x))
        return self.rescale()

    def range(self, x=None):
        if x is None:
            return self._range
        self._range = x
        return self.rescale()

    def rangeRound(self, x):
        pass

    def clamp(self, x=None):
        if x is None:
            return self._clamp
        self._clamp = x
        return self.rescale()

    def interpolate(self, x=None):
        if x is None:
            return self._interpolate
        self._interpolate = x
        return self.rescale()

    def ticks(self, m=None):
        return d3_scale_linearTicks(self._domain, m)

    def tickFormat(self, m=None, fmt=None):
        return d3_scale_linearTickFormat(self._domain, m, fmt)

    def nice(self, m=None):
        d3_scale_linearNice(self._domain, m)
        return self.rescale()

    def copy(self):
        return LinearScale(self._domain, self._range, self._interpolate, 
                self._clamp)

    def __call__(self, x):
        return self._output(x)

class TimeScale(object):

    def __init__(self, linear=None, methods=None, fmt=None):
        self._linear = LinearScale() if linear is None else linear
        self._methods = (d3_time_scaleLocalMethods if methods is None else 
                methods)
        #self._format = d3_time_scaleLocalFormat if fmt is None else fmt
        self._format = mytimeformat if fmt is None else fmt

    def invert(self, x):
        return milli2dt(self._linear.invert(x))

    def domain(self, x=None):
        if x is None:
            return list(map(milli2dt, self._linear.domain()))
        num_domain = list(map(dt2milli, x))
        self._linear.domain(num_domain)
        return self

    def tickMethod(self, extent, count):
        span = extent[1] - extent[0]
        target = span / count
        i = d3_bisect(d3_time_scaleSteps, target)
        if i == len(d3_time_scaleSteps):
            return [self._methods[-1][0],
                    d3_scale_linearTickRange(list(map(lambda d : d / 31536e6, 
                        extent)), count)[2]]
        if not i:
            return [d3_time_scaleMilliseconds,
                    d3_scale_linearTickRange(extent, count)[2]]
        if (target / d3_time_scaleSteps[i - 1] < d3_time_scaleSteps[i] / 
                target):
            return self._methods[i - 1]
        return self._methods[i]

    def nice(self, interval=None, skip=0):
        domain = self.domain()
        extent = d3_scaleExtent(domain)
        extent = list(map(dt2milli, extent))
        if interval is None:
            method = self.tickMethod(extent, 10)
        elif str(interval).isnumeric():
            method = self.tickMethod(extent, interval)
        else:
            method = None
        if method:
            interval = method[0]
            skip = method[1]

        def skipped(date):
            return (not date is None) and (not len(interval.range(date, 
                milli2dt(dt2milli(date)+1), skip)))

        if skip > 1:
            return self.domain(d3_scale_nice(domain,
                        {'floor': lambda x : time_nice_floor(x, skipped, 
                            interval),
                        'ceil': lambda x : time_nice_ceil(x, skipped, 
                            interval)}))
        else:
            return self.domain(d3_scale_nice(domain, interval))

    def ticks(self, interval=None, skip=None):
        extent = d3_scaleExtent(self.domain())
        extent = list(map(lambda x : x.timestamp() * 1000, extent))
        method = (self.tickMethod(extent, 10) if interval is None else 
                self.tickMethod(extent, interval))
        if method:
            interval = method[0]
            skip = method[1]

        if skip < 1:
            return interval.range(milli2dt(extent[0]), 
                    milli2dt(extent[1] + 1), 1)
        else:
            return interval.range(milli2dt(extent[0]), 
                    milli2dt(extent[1] + 1), skip)

    def tickFormat(self):
        return self._format

    def range(self, x=None):
        if x is None:
            return self._linear.range()
        self._linear.range(x)
        return self

    def rangeRound(self, x):
        pass

    def clamp(self, x=None):
        if x is None:
            return self._linear.clamp()
        self._linear.clamp(x)
        return self

    def interpolate(self, x=None):
        if x is None:
            return self._linear.interpolate()
        self._linear.interpolate(x)
        return self

    def copy(self):
        return TimeScale(self._linear.copy(), self._methods, self._format)

    def __call__(self, x):
        return self._linear(dt2milli(x))
