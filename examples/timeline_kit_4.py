"""
    Fourth example on:
    https://kristw.github.io/d3kit-timeline/

    Labella.py doesn't implement the full colorscale from d3, just category 10 
    and category 20. Below we show an example of implementing specific colors 
    based on the input data.
"""

import math

from datetime import date

from labella.timeline import TimelineSVG, TimelineTex

def color_4(d):
    idx = math.ceil(d['episode']/3)
    if idx == 1:
        return '#bcbd22'
    elif idx == 2:
        return '#7f7f7f'
    elif idx == 3:
        return '#17becf'

def main():
    items = [
            {'time': date(1977, 4,25), 'episode': 4,
                'text': 'A New Hope'},
            {'time': date(1980, 4,17), 'episode': 5,
                'text': 'The Empire Strikes Back'},
            {'time': date(1984, 4,25), 'episode': 6,
                'text': 'Return of the Jedi'},
            {'time': date(1999, 4,19), 'episode': 1,
                'text': 'The Phantom Menace'},
            {'time': date(2002, 4,16), 'episode': 2,
                'text': 'Attack of the Clones'},
            {'time': date(2005, 4,19), 'episode': 3,
                'text': 'Revenge of the Sith'},
            {'time': date(2015,11,18), 'episode': 7,
                'text': 'The Force Awakens'},
            ]

    options = {
        'initialWidth': 804,
        'initialHeight': 160,
        'direction': 'up',
        'dotColor': color_4,
        'labelBgColor': color_4,
        'linkColor': color_4,
        'textFn': lambda d : d['text'],
        'margin': {'left': 20, 'right': 20, 'top': 20, 'bottom': 30},
        'layerGap': 40,
        'labella': {
            'maxPos': 800,
            'algorithm': 'simple'
            }
        }

    tl = TimelineSVG(items, options=options)
    tl.export('timeline_kit_4.svg')

    tl = TimelineTex(items, options=options)
    tl.export('timeline_kit_4.tex')

if __name__ == '__main__':
    main()
