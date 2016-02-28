"""
    Fifth example on:
    https://kristw.github.io/d3kit-timeline/
"""

from datetime import date

from labella.scale import LinearScale
from labella.timeline import TimelineSVG, TimelineTex

def color5(d):
    if d['team'] == 'GER':
        return '#1F77B4'
    else:
        return '#FF7F0E'

def main():
    data = [
            {'time': 1,  'name': 'Müller',  'team': 'GER'},
            {'time': 23, 'name': 'Klose',   'team': 'GER'},
            {'time': 24, 'name': 'Kroos',   'team': 'GER'},
            {'time': 26, 'name': 'Kroos',   'team': 'GER'},
            {'time': 29, 'name': 'Khedira', 'team': 'GER'},
            {'time': 69, 'name': 'Schürrle', 'team': 'GER'},
            {'time': 79, 'name': 'Schürrle', 'team': 'GER'},
            {'time': 90, 'name': 'Oscar', 'team': 'BRA'},
            ]

    options = {
        'direction': 'up',
        'initialWidth': 804,
        'initialHeight': 120,
        'scale': LinearScale(),
        'domain': [0, 90],
        'margin': {'left': 20, 'right': 20, 'top': 30, 'bottom': 20},
        'textFn': lambda d : d['name'],
        'layerGap': 40,
        'dotColor': color5,
        'labelBgColor': color5,
        'linkColor': color5,
        'labella': {
            'maxPos': 764,
            'algorithm': 'simple',
            },
        'labelPadding': {'left': 0, 'right': 2, 'top': 0, 'bottom': 0},
        }

    tl = TimelineSVG(data, options=options)
    tl.export('timeline_kit_5.svg')

    tl = TimelineTex(data, options=options)
    tl.export('timeline_kit_5.tex')

if __name__ == '__main__':
    main()
