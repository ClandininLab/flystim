#!/usr/bin/env python3

# Launches a single-screen server for StimManager

from flystim.options import OptionParser

def main():
    OptionParser('Run display server.').run_server()

if __name__ == '__main__':
    main()
