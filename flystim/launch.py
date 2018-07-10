import subprocess
import os.path
import sys

from time import time

from flystim.rpc import Client, request

class IdCounter:
    """
    Class to keep track of how many screens of each ID have been added.  This is largely for debugging purposes,
    because usually only one window will be open on each screen.
    """

    def __init__(self):
        self.counts = {}

    def add(self, id):
        """
        :param id: ID number to be added.
        :return: Count of this ID registered so far (including the one just added)
        """

        # increment count of this ID
        self.counts[id] = self.counts.get(id, 0) + 1

        # return count
        return self.counts[id]

def create_stim_process(screen, profile=False, counter=None):
    """
    This function launches a subprocess to display stimuli on a given screen.  In general, this function should
    be called once for each screen.
    :param screen: Screen object (from flystim.screen) that contains screen ID, dimensions, etc.
    :return: Subprocess object corresponding to the stimuli display program.
    """

    # get full path to this file
    # ref: https://stackoverflow.com/questions/37863476/why-use-both-os-path-abspath-and-os-path-realpath/40311142
    file_path_full = os.path.realpath(os.path.expanduser(__file__))

    # get the full path of this directory
    dir_path_full = os.path.dirname(file_path_full)

    # get the full path of the server script
    server_full_path = os.path.join(dir_path_full, 'framework.py')

    # get the path of the python executable
    python_full_path = os.path.realpath(os.path.expanduser(sys.executable))

    # set argument for display program
    args = []
    args += [python_full_path]
    if profile:
        args += ['-m', 'cProfile']
        args += ['-o', 'id_{}_no_{}.prof'.format(screen.id, counter.add(screen.id))]
    args += [server_full_path]
    args += ['--id', str(screen.id)]
    args += ['--width', str(screen.width)]
    args += ['--height', str(screen.height)]
    args += ['--rotation', str(screen.rotation)]
    args += ['--offset'] + list(str(v) for v in screen.offset)
    args += ['--square_loc', str(screen.square_loc)]
    args += ['--square_side', str(screen.square_side)]
    if screen.fullscreen:
        args += ['--fullscreen']
    if screen.vsync:
        args += ['--vsync']

    # launch display program
    p = subprocess.Popen(args, stdin=subprocess.PIPE)

    # return the process
    return p

class StimManager:
    def __init__(self, screens, profile=False):
        """
        Launches separate processes to display synchronized stimuli on all of the given screens.  After that, a
        remote procedure call (RPC) server is launched, which allows the user to send commands to all screens at once.
        :param screens: List of screens on which the stimuli should be displayed.  Each should be a Screen object defining
        the screen coordinates, id #, etc.
        """

        # Launch a separate display process for each screen
        counter = IdCounter()
        self.processes = [create_stim_process(screen=screen, profile=profile, counter=counter) for screen in screens]

        # Create RPC handlers for each process
        self.clients = [Client(process.stdin) for process in self.processes]

    def batch(self, *requests):
        # preprocess requests as necessary
        for request in requests:
            if request.method == 'start_stim':
                assert not request.params, 'start_stim should not be called with arguments'
                request.params = [time()]

        # run the batch on each client
        for client in self.clients:
            client.batch(*requests)

    def __getattr__(self, method):
        """
        Generic handling for RPC methods.
        """

        def f(*args, **kwargs):
            self.batch(request(method, *args, **kwargs))

        return f

class MultiCall:
    def __init__(self, manager: StimManager):
        self.manager = manager
        self.requests = []

    def __getattr__(self, method):
        def f(*args, **kwargs):
            self.requests.append(request(method, *args, **kwargs))

        return f

    def __call__(self):
        self.manager.batch(*self.requests)