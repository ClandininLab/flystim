#!/usr/bin/env python3

import matplotlib.pyplot as plt

from argparse import ArgumentParser
from flystim.rigs import get_screens

def main():
    parser = ArgumentParser('Draw screen setup.')
    parser.add_argument('--setup_name', type=str, default='bigrig', help='Name of the stimulus configuration.')
    parser.add_argument('--title', type=str, default=None, help='Optional title for the plot.')
    parser.add_argument('--output', type=str, default=None, help='Optional output file name for the plot.')

    args = parser.parse_args()

    screens = get_screens(args.setup_name)

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

    if args.title is not None:
        plt.title(args.title)

    if args.output is None:
        plt.show()
    else:
        plt.savefig(args.output, bbox_inches='tight')

if __name__=='__main__':
    main()