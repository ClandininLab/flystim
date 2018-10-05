#!/usr/bin/env python3

import matplotlib.pyplot as plt

from flystim.options import OptionParser
from flystim.options import get_screens

def main():
    parser = OptionParser('Draw screen setup.')
    parser.add_argument('--title', type=str, default=None, help='Optional title for the plot.')
    parser.add_argument('--output', type=str, default=None, help='Optional output file name for the plot.')

    screens = get_screens(parser.args.setup_name)

    legend = []
    for screen in screens:
        screen.draw()
        legend.append(screen.name)

    plt.plot([0], [0], marker='*')
    legend += ['fly']

    plt.legend(legend)
    plt.axis('equal')
    plt.xlabel('x (meters)')
    plt.ylabel('y (meters)')

    if parser.args.title is not None:
        plt.title(parser.args.title)

    if parser.args.output is None:
        plt.show()
    else:
        plt.savefig(parser.args.output, bbox_inches='tight')

if __name__=='__main__':
    main()