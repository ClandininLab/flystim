#!/usr/bin/env python3

# Launches a single-screen server for StimManager

from flystim.launch import StimManager, stim_server
from flystim.screen import Screen

def main():
    screens = [Screen()]

    manager = StimManager(screens)
    stim_server(manager)

if __name__ == '__main__':
    main()
