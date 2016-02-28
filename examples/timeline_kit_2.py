"""
    Second example on:
    https://kristw.github.io/d3kit-timeline/
"""

from datetime import date

from labella.timeline import TimelineSVG, TimelineTex

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
        'initialWidth': 400,
        'initialHeight': 250,
        'direction': 'left',
        'dotColor': '#000000',
        'labelBgColor': '#777',
        'linkColor': '#777',
        'textFn': lambda x: x['text'] + ' - ' + str(x['time'].year),
        'labelPadding': {'left': 0, 'right': 0, 'top': 0, 'bottom': 0},
        'margin': {'left': 20, 'right': 20, 'top': 20, 'bottom': 20},
        'labella': {
            'nodeHeight': 12,
            },
        'showTicks': False
        }

    tl = TimelineSVG(items, options=options)
    tl.export('timeline_kit_2.svg')

    tl = TimelineTex(items, options=options)
    tl.export('timeline_kit_2.tex')

if __name__ == '__main__':
    main()
