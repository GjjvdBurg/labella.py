
from labella.force import Force
from labella.node import Node
from labella.renderer import Renderer
from labella.svg import draw_svg

def main():
    nodes = [
            Node(1,50),
	    Node(2,50),
	    Node(3,50),
	    Node(3,50),
	    Node(3,50),
	    Node(304,50),
	    Node(454,50),
	    Node(454,50),
	    Node(454,50),
	    Node(804,50),
	    Node(804,70),
	    Node(804,50),
	    Node(804,50),
	    Node(854,50),
	    Node(854,50)]
    options = {
            'margin': {'left': 20, 'right': 20, 'top': 20, 'bottom': 20},
            'initialWidth': 112,
            'initialHeight': 1000
            }
    direction = 'right'
    output_file = 'basic_right.svg'

    renderer = Renderer({'layerGap': 60, 'nodeHeight': 12, 'direction':
        direction})
    renderer.layout(nodes)

    force = Force({'minPos': 0, 'maxPos': 960})
    force.nodes(nodes)
    force.compute()

    draw_svg(renderer, force.nodes(), options, output_file, direction)


if __name__ == '__main__':
    main()
