import subprocess
import os
import os.path
import sys
import socket
import logging
from jsonrpc.jsonrpc2 import JSONRPC20BatchRequest, JSONRPC20Request
import platform

from time import time

from flystim.rpc import Client, request

def create_stim_process(screen, profile=False):
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
        args += ['-o', screen.name + '.prof']
    args += [server_full_path]
    args += ['--id', str(screen.id)]
    args += ['--name', str(screen.name)]
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
    env = os.environ.copy()
    if platform.system() == 'Linux':
        env['DISPLAY'] = ':0.' + str(screen.id)
    p = subprocess.Popen(args, stdin=subprocess.PIPE, env=env)

    # return the process
    return p

# ref: https://stackoverflow.com/questions/6946629/can-i-get-a-socket-makefile-to-have-the-same-read-semantics-as-a-regular-file

class StimClient:
    def __init__(self, addr=None):
        # set defaults
        if addr is None:
            addr = ('127.0.0.1', 60629)

        connection = socket.create_connection(addr)
        self.file = connection.makefile('w')

    def batch(self, *requests):
        self.file.write(JSONRPC20BatchRequest(*requests).json + '\n')
        self.file.flush()

    def __getattr__(self, method):
        def f(*args, **kwargs):
            self.batch(request(method, *args, **kwargs))

        return f

# ref: https://stackoverflow.com/questions/11815852/how-do-i-make-my-tcp-server-run-forever

def stim_server (manager, addr=None):
    # set defaults
    if addr is None:
        addr = ('127.0.0.1', 60629)

    # configure logging
    logging.basicConfig(level=logging.DEBUG)

    # configure the socket
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(addr)
    s.listen(1)

    while True:
        connection, addr = s.accept()
        logging.info('StimServer accepted connection.')

        f = connection.makefile('r')
        for line in f:
            # trim whitespace and skip if the line is now empty
            request_str = line.strip()
            if request_str == '':
                continue

            # parse request string
            request = JSONRPC20Request.from_json(request_str)

            # process request(s)
            if isinstance(request, JSONRPC20BatchRequest):
                manager.batch(*request.requests)
            else:
                manager.batch(request)

        logging.info('StimServer dropped connection.')

class StimManager:
    def __init__(self, screens, profile=False):
        """
        Launches separate processes to display synchronized stimuli on all of the given screens.  After that, a
        remote procedure call (RPC) server is launched, which allows the user to send commands to all screens at once.
        :param screens: List of screens on which the stimuli should be displayed.  Each should be a Screen object
        defining the screen coordinates, id #, etc.
        """

        # Launch a separate display process for each screen
        self.processes = [create_stim_process(screen=screen, profile=profile) for screen in screens]

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
    def __init__(self, manager):
        self.manager = manager
        self.requests = []

    def __getattr__(self, method):
        def f(*args, **kwargs):
            self.requests.append(request(method, *args, **kwargs))

        return f

    def __call__(self):
        self.manager.batch(*self.requests)
