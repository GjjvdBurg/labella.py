
import math

from copy import deepcopy
from datetime import datetime, timedelta

d3_time = {}

milli2dt = lambda x : datetime.fromtimestamp(x / 1000.0)
dt2milli = lambda x : x.timestamp() * 1000.0

# Timezones are ignored
getTimezoneOffset = lambda x : 0
daysThisMonth = lambda x : (x.replace(month=x.month%12+1, day=1) - 
        timedelta(days=1)).day

class d3_time_interval():

    def __init__(self, local, step, number):
        self._local = local
        self._step = step
        self._number = number

    def round(self, date):
        d0 = self._local(date)
        d1 = self.offset(d0, 1)
        if date - d0 < d1 - date:
            return d0
        return d1

    def floor(self, date):
        return self._local(date)

    def ceil(self, date):
        ndate = self._local(milli2dt(dt2milli(date) - 1))
        ndate = self._step(ndate, 1)
        return ndate

    def offset(self, date, k):
        ndate = self._step(date, k)
        return ndate

    def range(self, t0, t1, dt):
        time = self.ceil(t0)
        times = []
        if dt > 1:
            while time < t1:
                if not (self._number(time) % dt):
                    times.append(deepcopy(time))
                time = self._step(time, 1)
        else:
            while time < t1:
                times.append(deepcopy(time))
                time = self._step(time, 1)
        return times

    def __call__(self, date):
        return self._local(date)

############ second ################################

d3_time['second'] = d3_time_interval(
        lambda date : milli2dt(math.floor(dt2milli(date) / 1e3) * 1e3),
        lambda date, offset : milli2dt((dt2milli(date) + 
            math.floor(offset) * 1e3)),
        lambda date : date.second
        )

d3_time['seconds'] = d3_time['second'].range

####################################################

############ minute ################################

d3_time['minute'] = d3_time_interval(
        lambda date : milli2dt(math.floor(dt2milli(date) / 6e4) * 6e4),
        lambda date, offset : milli2dt(dt2milli(date) + 
            math.floor(offset) * 6e4),
        lambda date : date.minute
        )

d3_time['minutes'] = d3_time['minute'].range

####################################################

############ hour ##################################

def d3_time_hour_local(date):
    timezone = getTimezoneOffset(date) / 60
    ndate = milli2dt((math.floor(dt2milli(date) / 36e5 - timezone) + 
        timezone) * 36e5)
    return ndate

d3_time['hour'] = d3_time_interval(
        lambda date : d3_time_hour_local(date),
        lambda date, offset : milli2dt(dt2milli(date) + 
            math.floor(offset) * 36e5),
        lambda date : date.hour)

d3_time['hours'] = d3_time['hour'].range

####################################################

############# day ##################################

def d3_time_day_offset(date, offset):
    nday = date.day + offset
    ndaysthismonth = daysThisMonth(date)
    ndate = deepcopy(date)
    while nday > ndaysthismonth:
        ndate = d3_time_month_offset(date, 1)
        nday -= ndaysthismonth
        ndaysthismonth = daysThisMonth(ndate)
    ndate = ndate.replace(day=nday)
    return ndate

def day_of_year(date):
    year = d3_time['year'](date)
    tzoff = getTimezoneOffset(date) - getTimezoneOffset(year)
    diff = dt2milli(date) - dt2milli(year) - tzoff * 6e4
    return math.floor(diff / 864e5)

d3_time['day'] = d3_time_interval(
        lambda date : datetime(date.year, date.month, date.day),
        #lambda date, offset : date.replace(day=(date.day + offset)),
        lambda date, offset : d3_time_day_offset(date, offset),
        lambda date : date.day - 1
        )

d3_time['days'] = d3_time['day'].range

d3_time['dayOfYear'] = lambda date : day_of_year(date)

####################################################

########### week ###################################

def d3_time_week_local(date):
    # only sunday
    i = 7
    ndate = d3_time['day'](date)
    diff = ((date.isoweekday() % 7) + i) % 7
    ndate = datetime.fromtimestamp(ndate.timestamp() - diff * 24 * 3600)
    return ndate

def d3_time_week_number(date):
    # only sunday
    i = 7
    day = d3_time['year'](date).isoweekday() % 7
    return (math.floor((d3_time['dayOfYear'](date) + (day + i) % 7) / 7) - 
            (day != i))

d3_time['week'] = d3_time_interval(
        lambda date : d3_time_week_local(date),
        lambda date, offset : datetime.fromtimestamp(date.timestamp() + 
            math.floor(offset) * 7 * 24 * 3600),
        lambda date : d3_time_week_number(date)
        )

d3_time['weeks'] = d3_time['week'].range

####################################################

############ month #################################

def d3_time_month_local(date):
    ndate = d3_time['day'](date)
    return ndate.replace(day=1)

def d3_time_month_offset(date, offset):
    nmonth = date.month + offset
    ndate = deepcopy(date)
    while nmonth > 12:
        ndate = ndate.replace(year=ndate.year + 1)
        nmonth -= 12
    ndate = ndate.replace(month=nmonth)
    return ndate

d3_time['month'] = d3_time_interval(
        lambda date : d3_time_month_local(date),
        lambda date, offset : d3_time_month_offset(date, offset),
        lambda date : date.month - 1
        )

d3_time['months'] = d3_time['month'].range

####################################################

############## year ################################

def d3_time_year_local(date):
    ndate = d3_time['day'](date)
    return ndate.replace(month=1, day=1)

d3_time['year'] = d3_time_interval(
        lambda date : d3_time_year_local(date),
        lambda date, offset : date.replace(year=date.year + offset),
        lambda date : date.year
        )

d3_time['years'] = d3_time['year'].range

####################################################
