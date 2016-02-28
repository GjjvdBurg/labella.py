Labella.py Documentation
========================

The main interface through which you can use labella.py is through the 
`TimelineSVG` and `TimelineTex` objects in `labella.timeline`. These objects 
are inherit from the main `Timeline` object, which organizes the common code 
needed for both output formats. Both the `TimelineSVG` and `TimelineTex` 
objects support the options implemented in 
[d3kit-timeline](https://github.com/kristw/d3kit-timeline), see the 
documentation 
[here](https://github.com/kristw/d3kit-timeline/blob/master/docs/api.md). Note 
that the options that end in `Fn` require functions, which can be supplied by 
lambdas or user defined functions in Python.

Options that are new and not part of 
[d3kit-timeline](https://github.com/kristw/d3kit-timeline) are:

| option | default | description |
| ------ | ------- | ----------- |
| textXOffset | 0.15em | horizontal offset for text within a label, used for SVG output |
| showTicks | True | boolean for showing ticks on the axis 
| latex | `{'fontsize': '11pt'}` | options for LaTeX, only includes fontsize specification now |

Input Specification
-------------------

Labella.py allows input specification through a list of dicts, just like in 
labella.js. A dict must have a 'time' field, which can be either numeric 
(int/float), `datetime.date`, `datetime.time` or `datetime.datetime`. If a 
'width' field is not specified, the default width of 50 will be used. Labels 
with text can be created by supplying a 'text' field in the dict. If this is 
the case and no 'width' field is specified, the width is calculated 
automatically (see Width Calculation below). Other data can be incorporated in 
the dict, which can for instance be used by the `textFn` function, and those 
for determining colors.

Note that if a `datetime.date` or a `datetime.time` object is specified they 
will be converted internally to a full `datetime.datetime` object for use in 
the time scale.

Width Calculation
-----------------

In [d3kit-timeline](https://github.com/kristw/d3kit-timeline), the width of a 
label with text is calculated by getting the bounding box of a the HTML label. 
Since labella.py doesn't have access to this, the width is calculated by 
compiling a small LaTeX document which contains only the text, and the 
bounding box is calculated from that. This ensures that for PDF output the 
label has exactly the right width. For the SVG output the width is 
approximate, since a different font is used for SVG than used in LaTeX.

Color Specification
-------------------

As in labella.js, labella.py allows specification of colors through the 
following options to a TimelineSVG or TimelineTex object:

- dotColor
- labelBgColor
- labelTextColor
- linkColor

For these options the color can be given as a three letter hex code (e.g. 
`#222`), a six letter hex code (e.g. `#45f23a`), a user-defined function, a 
lambda expression, or by a default color scheme. The default color schemes 
that are implemented are available in `labella.utils` and are known as 
`COLOR_10` and `COLOR_20`, corresponding to the category 10 and category 20 
[categorical colors in 
d3](https://github.com/mbostock/d3/wiki/Ordinal-Scales).  When either of these 
are used, the colors are used in order from small time value to large time 
value, looping around when necessary.

Scales
------

Labella.py includes two scales, `LinearScale` and `TimeScale`, which are 
adapted from their d3 equivalents. For use in a Labella timeline their use is 
equivalent to their use in d3kit-timeline, but they have some limitations 
beyond that. For instance, only linear interpolation is implemented, and the 
rangeRound functions of the scales in d3 are not implemented. Additionally, no 
distinction is made between local times and UTC times (i.e. timezones are 
ignored).  This may be a limitation for some, and pull requests for this 
feature are welcome.

Tests
-----

Labella.py includes unit tests for the d3 scales, VPSC functions, and those 
implemented in labella.js.

Known limitations
-----------------

Labella.py has not been tested on any other platforms than Linux. Therefore, 
the functionality on these platforms may be a bit limited. Pull requests and 
bug reports are welcome.
