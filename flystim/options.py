from argparse import ArgumentParser
from math import pi

from flystim.launch import StimManager, StimClient, stim_server
from flystim.screen import Screen

def get_screens(setup_name):
    if setup_name.lower() in ['macbook']:
        return [Screen(fullscreen=False)]
    elif setup_name.lower() in ['bruker']:
        # meters of image at projection plane, screen only shows 9x9 of this
        w = 14.2e-2
        h = 9e-2

        zDistToScreen = 5.36e-2  # meters

        screen = Screen(id=1, width=w, height=h, offset=(0, zDistToScreen, 0), fullscreen=True, square_side=5e-2, square_loc='lr')

        # TODO set back to two screens
        return [screen]
    elif setup_name.lower() in ['bigrig']:
        w = 43 * 2.54e-2
        h = 24 * 2.54e-2

        return [Screen(id=1, rotation=pi / 2, width=w, height=h, offset=(-w / 2, 0, h / 2)),
                Screen(id=2, rotation=0, width=w, height=h, offset=(0, w / 2, h / 2)),
                Screen(id=3, rotation=pi, width=w, height=h, offset=(0, -w / 2, h / 2)),
                Screen(id=4, rotation=-pi / 2, width=w, height=h, offset=(w / 2, 0, h / 2))]
    else:
        raise ValueError('Invalid setup name.')

class OptionParser(ArgumentParser):
    def __init__(self, description='Stimulus options.'):
        super().__init__(description=description)

        self.add_argument('--use_server', action='store_true', help='Connect to existing display server.')
        self.add_argument('--setup_name', type=str, default='macbook', help='Name of the setup configuration.')

        self._args = None

    @property
    def args(self):
        if self._args is None:
            self._args = super().parse_args()
        return self._args

    def create_manager(self):
        if self.args.use_server:
            return StimClient()
        else:
            return StimManager(get_screens(self.args.setup_name))

    def run_server(self):
        manager = StimManager(get_screens(self.args.setup_name))
        stim_server(manager)
