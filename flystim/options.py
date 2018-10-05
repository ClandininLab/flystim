from argparse import ArgumentParser
from math import pi, sqrt

from flystim.launch import StimManager, StimClient, stim_server
from flystim.screen import Screen

def get_bruker_screen(dir):
    # display geometry
    w = 14.2e-2
    h = 9e-2
    d = (w/2) * sqrt(2)

    # derived parameters
    s = (w/2) / sqrt(2)

    if dir=='left':
        id=2
        rotation = -pi/4
        offset = (-s, -d + s, -h / 2)
        square_loc = 'll'
    elif dir=='right':
        id=1
        rotation = +pi/4
        offset = (+s, -d + s, -h / 2)
        square_loc = 'lr'
    else:
        raise ValueError('Invalid direction.')

    return Screen(id=id, rotation=rotation, width=w, height=h, offset=offset, square_loc=square_loc,
           fullscreen=True, square_side=5e-2, name='Bruker '+dir)

def get_screens(setup_name):
    if setup_name.lower() in ['macbook']:
        return [Screen(fullscreen=False, name='MacBook')]
    elif setup_name.lower() in ['bruker_right']:
        return [get_bruker_screen('right')]
    elif setup_name.lower() in ['bruker_left']:
        return [get_bruker_screen('left')]
    elif setup_name.lower() in ['bruker']:
        return [get_bruker_screen('right'), get_bruker_screen('left')]
    elif setup_name.lower() in ['bigrig']:
        w = 43 * 2.54e-2
        h = 24 * 2.54e-2

        return [Screen(id=1, rotation=pi / 2, width=w, height=h, offset=(-w / 2, 0, h / 2), name='West'),
                Screen(id=2, rotation=0, width=w, height=h, offset=(0, w / 2, h / 2), name='North'),
                Screen(id=3, rotation=pi, width=w, height=h, offset=(0, -w / 2, h / 2), name='South'),
                Screen(id=4, rotation=-pi / 2, width=w, height=h, offset=(w / 2, 0, h / 2), name='East')]
    else:
        raise ValueError('Invalid setup name.')

class OptionParser(ArgumentParser):
    def __init__(self, description='Stimulus options.', default_setup_name='macbook', default_use_server=False):
        super().__init__(description=description)

        if not default_use_server:
            self.add_argument('--use_server', action='store_true', help='Connect to existing display server.')
        else:
            # Very bad, fix soon!
            self.add_argument('--use_server', action='store_false', help='Connect to existing display server.')
        self.add_argument('--setup_name', type=str, default=default_setup_name, help='Name of the setup configuration.')

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
