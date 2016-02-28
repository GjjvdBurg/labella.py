"""
    First example on:
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
        'margin': {'left': 40.5, 'right': 20, 'top': 20, 'bottom': 20},
        'initialWidth': 400,
        'initialHeight': 250,
        'direction': 'right',
        'dotColor': '#000000',
        'labelBgColor': '#000000',
        'linkColor': '#000000',
        'textFn': lambda x: str(x['time'].year) + ' - ' + x['text'],
        'labelPadding': {'left': 2, 'right': 0, 'top': 0, 'bottom': 0},
        'labella': {
            'nodeHeight': 12,
            },
        'latex': {
            'fontsize': '12pt'
            }
        }

    tl = TimelineSVG(items, options=options)
    tl.export('timeline_kit_1.svg')

    tl = TimelineTex(items, options=options)
    tl.export('timeline_kit_1.tex')

if __name__ == '__main__':
    main()
