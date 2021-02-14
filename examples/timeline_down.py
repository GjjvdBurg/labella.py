"""
Basic timeline without text in the labels, down direction.

"""

from labella.scale import LinearScale
from labella.timeline import TimelineSVG, TimelineTex
from labella.utils import COLOR_10


def main():
    items = [
        {"time": 1, "width": 50},
        {"time": 2, "width": 50},
        {"time": 3, "width": 50},
        {"time": 3, "width": 50},
        {"time": 3, "width": 50},
        {"time": 304, "width": 50},
        {"time": 454, "width": 50},
        {"time": 454, "width": 50},
        {"time": 454, "width": 50},
        {"time": 804, "width": 50},
        {"time": 804, "width": 70},
        {"time": 804, "width": 50},
        {"time": 804, "width": 50},
        {"time": 854, "width": 50},
        {"time": 854, "width": 50},
    ]

    options = {
        "initialWidth": 1000,
        "initialHeight": 112,
        "scale": LinearScale(),
        "direction": "down",
        "dotColor": "#000000",
        "labelBgColor": COLOR_10,
        "linkColor": COLOR_10,
        "labelPadding": {"left": 0, "right": 0, "top": 0, "bottom": 0},
        "labella": {"minPos": 0, "maxPos": 960},
        "showTicks": False,
        "latex": {
        "reproducible": True,
        }
    }

    tl = TimelineSVG(items, options=options)
    tl.export("timeline_down.svg")

    tl = TimelineTex(items, options=options)
    tl.export("timeline_down.tex")


if __name__ == "__main__":
    main()
