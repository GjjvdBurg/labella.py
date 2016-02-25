
"""
NOTE: To make writing the tests easier and in accordance with the original d3
tests they are copied from, the local function converts months from 0 based
indexing to Python's 1 based indexing.

"""

import unittest

from datetime import datetime

from labella.scale import TimeScale
from labella.d3_time import d3_time

def local(year, month, day, hours=0, minutes=0, seconds=0, milliseconds=0):
    # helper function copied from d3/test/time/time.js
    date = datetime(year, month+1, day, hours, minutes, seconds, milliseconds
            * 1000)
    return date

class TimeScaleTestCase(unittest.TestCase):

    def test_nice_1c(self):
        # rounds using the specified time interval
        x = TimeScale().domain([local(2009, 0, 1, 0, 12), local(2009, 0, 1,
            23, 48)])
        self.assertEqual(x.nice(d3_time['day']).domain(), [local(2009, 0, 1),
            local(2009, 0, 2)])
        self.assertEqual(x.nice(d3_time['week']).domain(), [local(2008, 11,
            28), local(2009, 0, 4)])
        self.assertEqual(x.nice(d3_time['month']).domain(), [local(2008, 11,
            1), local(2009, 1, 1)])
        self.assertEqual(x.nice(d3_time['year']).domain(), [local(2008, 0, 1),
            local(2010, 0, 1)])

    def test_nice_2a(self):
        # rounds using the specified time interval and skip
        x = TimeScale().domain([local(2009, 0, 1, 0, 12), local(2009, 0, 1,
            23, 48)])
        self.assertEqual(x.nice(d3_time['day'], 3).domain(), [local(2009, 0,
            1), local(2009, 0, 4)])
        self.assertEqual(x.nice(d3_time['week'], 2).domain(), [local(2008, 11,
            21), local(2009, 0, 4)])
        self.assertEqual(x.nice(d3_time['month'], 3).domain(), [local(2008, 9,
            1), local(2009, 3, 1)])
        self.assertEqual(x.nice(d3_time['year'], 10).domain(), [local(2000, 0,
            1), local(2010, 0, 1)])

    def test_nice_3(self):
        # rounds using the specified count
        x = TimeScale().domain([local(2009, 0, 1, 0, 17), local(2009, 0, 1,
            23, 42)])
        self.assertEqual(x.nice(100).domain(), [local(2009, 0, 1, 0, 15),
            local(2009, 0, 1, 23, 45)])
        self.assertEqual(x.nice(10).domain(), [local(2009, 0, 1), local(2009,
            0, 2)])

    def test_nice_4(self):
        # rounds with a default count of ten if no arguments
        x = TimeScale().domain([local(2009, 0, 1, 0, 17), local(2009, 0, 1,
            23, 42)])
        self.assertEqual(x.nice().domain(), [local(2009, 0, 1), local(2009, 0,
            2)])

    def test_nice_5(self):
        # works on degenerate domains
        x = TimeScale().domain([local(2009, 0, 1, 0, 12), local(2009, 0, 1, 0,
            12)])
        self.assertEqual(x.nice(d3_time['day']).domain(), [local(2009, 0, 1),
            local(2009, 0, 2)])

    def test_nice_6(self):
        # nice succeeds on sub-second intervals
        domain = [local(2013, 0, 1, 12, 0, 0), local(2013, 0, 1, 12, 0, 8)]
        x = TimeScale().domain(domain)
        self.assertEqual(x.nice().domain(), domain)

    def test_copy_1(self):
        # changes to the domain are isolated
        x = TimeScale().domain([local(2009, 0, 1), local(2010, 0, 1)])
        y = x.copy()
        x.domain([local(2010, 0, 1), local(2011, 0, 1)])
        self.assertEqual(y.domain(), [local(2009, 0, 1), local(2010, 0, 1)])
        self.assertEqual(x(local(2010, 0, 1)), 0)
        self.assertEqual(y(local(2010, 0, 1)), 1)
        y.domain([local(2011, 0, 1), local(2012, 0, 1)])
        self.assertEqual(x(local(2011, 0, 1)), 1)
        self.assertEqual(y(local(2011, 0, 1)), 0)
        self.assertEqual(x.domain(), [local(2010, 0, 1), local(2011, 0, 1)])
        self.assertEqual(y.domain(), [local(2011, 0, 1), local(2012, 0, 1)])

    def test_copy_2(self):
        # changes to the range are isolated
        x = TimeScale().domain([local(2009, 0, 1), local(2010, 0, 1)])
        y = x.copy()
        x.range([1, 2])
        self.assertEqual(x.invert(1), local(2009, 0, 1))
        self.assertEqual(y.invert(1), local(2010, 0, 1))
        self.assertEqual(y.range(), [0, 1])
        y.range([2, 3])
        self.assertEqual(x.invert(2), local(2010, 0, 1))
        self.assertEqual(y.invert(2), local(2009, 0, 1))
        self.assertEqual(x.range(), [1, 2])
        self.assertEqual(y.range(), [2, 3])

    def test_copy_3(self):
        # changes to clamping are isolated
        x = TimeScale().domain([local(2009, 0, 1), local(2010, 0,
            1)]).clamp(True)
        y = x.copy()
        x.clamp(False)
        self.assertEqual(x(local(2011, 0, 1)), 2)
        self.assertEqual(y(local(2011, 0, 1)), 1)
        self.assertTrue(y.clamp())
        y.clamp(False)
        self.assertEqual(x(local(2011, 0, 1)), 2)
        self.assertEqual(y(local(2011, 0, 1)), 2)
        self.assertFalse(x.clamp())

    def test_ticks_subsecond(self):
        # generates sub-second ticks
        x = TimeScale().domain([local(2011, 0, 1, 12, 0, 0),
            local(2011, 0, 1, 12, 0, 1)])
        self.assertEqual(x.ticks(4), [
            local(2011, 0, 1, 12, 0, 0,   0),
            local(2011, 0, 1, 12, 0, 0, 200),
            local(2011, 0, 1, 12, 0, 0, 400),
            local(2011, 0, 1, 12, 0, 0, 600),
            local(2011, 0, 1, 12, 0, 0, 800),
            local(2011, 0, 1, 12, 0, 1,   0)
            ])

    def test_ticks_second_one(self):
        # generates 1-second ticks
        x = TimeScale().domain([local(2011, 0, 1, 12, 0, 0),
            local(2011, 0, 1, 12, 0, 4)])
        self.assertEqual(x.ticks(4), [
            local(2011, 0, 1, 12, 0, 0),
            local(2011, 0, 1, 12, 0, 1),
            local(2011, 0, 1, 12, 0, 2),
            local(2011, 0, 1, 12, 0, 3),
            local(2011, 0, 1, 12, 0, 4)
            ])
    def test_ticks_second_five(self):
        # generates 5-second ticks
        x = TimeScale().domain([local(2011, 0, 1, 12, 0, 0),
            local(2011, 0, 1, 12, 0, 20)])
        self.assertEqual(x.ticks(4), [
            local(2011, 0, 1, 12, 0, 0),
            local(2011, 0, 1, 12, 0, 5),
            local(2011, 0, 1, 12, 0, 10),
            local(2011, 0, 1, 12, 0, 15),
            local(2011, 0, 1, 12, 0, 20)
            ])
    def test_ticks_second_fifteen(self):
        # generates 15-second ticks
        x = TimeScale().domain([local(2011, 0, 1, 12, 0, 0),
            local(2011, 0, 1, 12, 0, 50)])
        self.assertEqual(x.ticks(4), [
            local(2011, 0, 1, 12, 0, 0),
            local(2011, 0, 1, 12, 0, 15),
            local(2011, 0, 1, 12, 0, 30),
            local(2011, 0, 1, 12, 0, 45)
            ])
    def test_ticks_second_thirty(self):
        # generates 30-second ticks
        x = TimeScale().domain([local(2011, 0, 1, 12, 0, 0),
            local(2011, 0, 1, 12, 1, 50)])
        self.assertEqual(x.ticks(4), [
            local(2011, 0, 1, 12, 0, 0),
            local(2011, 0, 1, 12, 0, 30),
            local(2011, 0, 1, 12, 1, 0),
            local(2011, 0, 1, 12, 1, 30)
            ])
    def test_ticks_minute_one(self):
        # generates 1-minute ticks
        x = TimeScale().domain([local(2011, 0, 1, 12, 0, 27),
            local(2011, 0, 1, 12, 4, 12)])
        self.assertEqual(x.ticks(4), [
            local(2011, 0, 1, 12, 1),
            local(2011, 0, 1, 12, 2),
            local(2011, 0, 1, 12, 3),
            local(2011, 0, 1, 12, 4)
            ])
    def test_ticks_minute_five(self):
        # generates 5-minute ticks
        x = TimeScale().domain([local(2011, 0, 1, 12, 3, 27),
            local(2011, 0, 1, 12, 21, 12)])
        self.assertEqual(x.ticks(4), [
            local(2011, 0, 1, 12, 5),
            local(2011, 0, 1, 12, 10),
            local(2011, 0, 1, 12, 15),
            local(2011, 0, 1, 12, 20)
            ])
    def test_ticks_minute_fifteen(self):
        # generates 15-minute ticks
        x = TimeScale().domain([local(2011, 0, 1, 12, 8, 27),
            local(2011, 0, 1, 13, 4, 12)])
        self.assertEqual(x.ticks(4), [
            local(2011, 0, 1, 12, 15),
            local(2011, 0, 1, 12, 30),
            local(2011, 0, 1, 12, 45),
            local(2011, 0, 1, 13, 0)
            ])
    def test_ticks_minute_thirty(self):
        # generates 30-minute ticks
        x = TimeScale().domain([local(2011, 0, 1, 12, 28, 27),
            local(2011, 0, 1, 14, 4, 12)])
        self.assertEqual(x.ticks(4), [
            local(2011, 0, 1, 12, 30),
            local(2011, 0, 1, 13, 0),
            local(2011, 0, 1, 13, 30),
            local(2011, 0, 1, 14, 0)
            ])
    def test_ticks_hour_one(self):
        # generates 1-hour ticks
        x = TimeScale().domain([local(2011, 0, 1, 12, 28, 27),
            local(2011, 0, 1, 16, 34, 12)])
        self.assertEqual(x.ticks(4), [
            local(2011, 0, 1, 13, 0),
            local(2011, 0, 1, 14, 0),
            local(2011, 0, 1, 15, 0),
            local(2011, 0, 1, 16, 0)
            ])
    def test_ticks_hour_three(self):
        # generates 3-hour ticks
        x = TimeScale().domain([local(2011, 0, 1, 14, 28, 27),
            local(2011, 0, 2, 1, 34, 12)])
        self.assertEqual(x.ticks(4), [
            local(2011, 0, 1, 15, 0),
            local(2011, 0, 1, 18, 0),
            local(2011, 0, 1, 21, 0),
            local(2011, 0, 2, 0, 0)
            ])
    def test_ticks_hour_six(self):
        # generates 6-hour ticks
        x = TimeScale().domain([local(2011, 0, 1, 16, 28, 27),
            local(2011, 0, 2, 14, 34, 12)])
        self.assertEqual(x.ticks(4), [
            local(2011, 0, 1, 18, 0),
            local(2011, 0, 2, 0, 0),
            local(2011, 0, 2, 6, 0),
            local(2011, 0, 2, 12, 0)
            ])
    def test_ticks_hour_twelve(self):
        # generates 12-hour ticks
        x = TimeScale().domain([local(2011, 0, 1, 16, 28, 27),
            local(2011, 0, 3, 21, 34, 12)])
        self.assertEqual(x.ticks(4), [
            local(2011, 0, 2, 0, 0),
            local(2011, 0, 2, 12, 0),
            local(2011, 0, 3, 0, 0),
            local(2011, 0, 3, 12, 0)
            ])
    def test_ticks_day_one(self):
        # generates 1-day ticks
        x = TimeScale().domain([local(2011, 0, 1, 16, 28, 27),
            local(2011, 0, 5, 21, 34, 12)])
        self.assertEqual(x.ticks(4), [
            local(2011, 0, 2, 0, 0),
            local(2011, 0, 3, 0, 0),
            local(2011, 0, 4, 0, 0),
            local(2011, 0, 5, 0, 0)
            ])
    def test_ticks_day_two(self):
        # generates 2-day ticks
        x = TimeScale().domain([local(2011, 0, 2, 16, 28, 27),
            local(2011, 0, 9, 21, 34, 12)])
        self.assertEqual(x.ticks(4), [
            local(2011, 0, 3, 0, 0),
            local(2011, 0, 5, 0, 0),
            local(2011, 0, 7, 0, 0),
            local(2011, 0, 9, 0, 0)
            ])
    def test_ticks_week_one(self):
        # generates 1-week ticks
        x = TimeScale().domain([local(2011, 0, 1, 16, 28, 27),
            local(2011, 0, 23, 21, 34, 12)])
        self.assertEqual(x.ticks(4), [
            local(2011, 0, 2, 0, 0),
            local(2011, 0, 9, 0, 0),
            local(2011, 0, 16, 0, 0),
            local(2011, 0, 23, 0, 0)
            ])
    def test_ticks_month_one(self):
        # generates 1-month ticks
        x = TimeScale().domain([local(2011, 0, 18), local(2011, 4, 2)])
        self.assertEqual(x.ticks(4), [
            local(2011, 1, 1, 0, 0),
            local(2011, 2, 1, 0, 0),
            local(2011, 3, 1, 0, 0),
            local(2011, 4, 1, 0, 0)
            ])
    def test_ticks_month_three(self):
        # generates 3-month ticks
        x = TimeScale().domain([local(2010, 11, 18), local(2011, 10, 2)])
        self.assertEqual(x.ticks(4), [
            local(2011, 0, 1, 0, 0),
            local(2011, 3, 1, 0, 0),
            local(2011, 6, 1, 0, 0),
            local(2011, 9, 1, 0, 0)
            ])
    def test_ticks_year_one(self):
        # generates 1-year ticks
        x = TimeScale().domain([local(2010, 11, 18), local(2014, 2, 2)])
        self.assertEqual(x.ticks(4), [
            local(2011, 0, 1, 0, 0),
            local(2012, 0, 1, 0, 0),
            local(2013, 0, 1, 0, 0),
            local(2014, 0, 1, 0, 0)
            ])
    def test_ticks_year_multi(self):
        # generates multi-year ticks
        # year adjusted to 1 for Python.
        x = TimeScale().domain([local(1, 11, 18), local(2014, 2, 2)])
        self.assertEqual(x.ticks(6), [
            local( 500, 0, 1, 0, 0),
            local(1000, 0, 1, 0, 0),
            local(1500, 0, 1, 0, 0),
            local(2000, 0, 1, 0, 0)
            ])
    def test_ticks_empty_domain(self):
        # returns one tick for degenerate empty domain
        x = TimeScale().domain([local(2014, 2, 2), local(2014, 2, 2)])
        self.assertEqual(x.ticks(6), [local(2014, 2, 2)])

    def test_tickFormat_year(self):
        #formats year on New Year's"
        fmt = TimeScale().tickFormat()
        self.assertEqual(fmt(local(2011, 0, 1)), "2011");
        self.assertEqual(fmt(local(2012, 0, 1)), "2012");
        self.assertEqual(fmt(local(2013, 0, 1)), "2013");

    def test_tickFormat_month(self):
        #formats month on the 1st of each month"
        fmt = TimeScale().tickFormat()
        self.assertEqual(fmt(local(2011, 1, 1)), "February");
        self.assertEqual(fmt(local(2011, 2, 1)), "March");
        self.assertEqual(fmt(local(2011, 3, 1)), "April");

    def test_tickFormat_month_year(self):
        #formats week on Sunday midnight"
        fmt = TimeScale().tickFormat()
        self.assertEqual(fmt(local(2011, 1, 6)), "Feb 06");
        self.assertEqual(fmt(local(2011, 1, 13)), "Feb 13");
        self.assertEqual(fmt(local(2011, 1, 20)), "Feb 20");

    def test_tickFormat_day_year(self):
        #formats date on midnight"
        fmt = TimeScale().tickFormat()
        self.assertEqual(fmt(local(2011, 1, 2)), "Wed 02");
        self.assertEqual(fmt(local(2011, 1, 3)), "Thu 03");
        self.assertEqual(fmt(local(2011, 1, 4)), "Fri 04");

    def test_tickFormat_time_ampm(self):
        #formats hour on minute zero"
        fmt = TimeScale().tickFormat()
        self.assertEqual(fmt(local(2011, 1, 2, 11)), "11 AM");
        self.assertEqual(fmt(local(2011, 1, 2, 12)), "12 PM");
        self.assertEqual(fmt(local(2011, 1, 2, 13)), "01 PM");

    def test_tickFormat_time(self):
        #formats minute on second zero"
        fmt = TimeScale().tickFormat()
        self.assertEqual(fmt(local(2011, 1, 2, 11, 59)), "11:59");
        self.assertEqual(fmt(local(2011, 1, 2, 12,  1)), "12:01");
        self.assertEqual(fmt(local(2011, 1, 2, 12,  2)), "12:02");

    def test_tickFormat_minutes(self):
        #otherwise, formats second"
        fmt = TimeScale().tickFormat()
        self.assertEqual(fmt(local(2011, 1, 2, 12,  1,  9)), ":09");
        self.assertEqual(fmt(local(2011, 1, 2, 12,  1, 10)), ":10");
        self.assertEqual(fmt(local(2011, 1, 2, 12,  1, 11)), ":11");


if __name__ == '__main__':
    unittest.main()
