import subprocess
import os.path
import sys

from time import time
from xmlrpc.server import SimpleXMLRPCServer

from flystim.rpc import RpcClient
from flystim.screen import Screen

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

def launch(screens, port=0, profile=False):
    """
    Launches separate processes to display synchronized stimuli on all of the given screens.  After that, a
    remote procedure call (RPC) server is launched, which allows the user to send commands to all screens at once.
    :param screens: List of screens on which the stimuli should be displayed.  Each should be a Screen object defining
    the screen coordinates, id #, etc.
    :param port: Socket port number to be used for sending stimulus commands.  The default value (0) means that a port
    will be assigned automatically, and the chosen port will be printed out.
    """

    ####################################
    # launch the display processes
    ####################################

    # Launch a separate display process for each screen
    counter = IdCounter()
    processes = [create_stim_process(screen=screen, profile=profile, counter=counter) for screen in screens]

    # Create RPC handlers for each process
    stim_clients = [RpcClient(process.stdin) for process in processes]

    ####################################
    # define the control functions
    ####################################

    def load_stim(name, params):
        """
        Loads the stimulus with the given name, using the given params.  After the stimulus is loaded, the
        background color is changed to the one specified in the stimulus, and the stimulus is evaluated at time 0.
        :param name: Name of the stimulus (should be a class name)
        :param params: Parameters used to instantiate the class (e.g., period, bar width, etc.)
        """

        for stim_client in stim_clients:
            stim_client.request('load_stim', [name, params])

        return 0

    def start_stim():
        """
        Starts the stimulus animation, using exactly the same start time for all screens.
        """

        t = time()
        for stim_client in stim_clients:
            stim_client.request('start_stim', [t])

        return 0

    def stop_stim():
        """
        Stops the stimulus animation and removes it from the displays.  The background color reverts to idle_background.
        """

        for stim_client in stim_clients:
            stim_client.request('stop_stim')

        return 0

    def start_corner_square():
        """
        Start toggling the corner square.
        """

        for stim_client in stim_clients:
            stim_client.request('start_corner_square')

        return 0

    def stop_corner_square():
        """
        Stop toggling the corner square.
        """

        for stim_client in stim_clients:
            stim_client.request('stop_corner_square')

        return 0

    def white_corner_square():
        """
        Make the corner square white.
        """

        for stim_client in stim_clients:
            stim_client.request('white_corner_square')

        return 0

    def black_corner_square():
        """
        Make the corner square black.
        """

        for stim_client in stim_clients:
            stim_client.request('black_corner_square')

        return 0

    def show_corner_square():
        """
        Show the corner square.
        """

        for stim_client in stim_clients:
            stim_client.request('show_corner_square')

        return 0

    def hide_corner_square():
        """
        Hide the corner square.  Note that it will continue to toggle if self.should_toggle_square is True,
        even though nothing will be displayed.
        """

        for stim_client in stim_clients:
            stim_client.request('hide_corner_square')

        return 0

    def set_idle_background(color):
        """
        Sets the RGB color of the background when there is no stimulus being displayed (sometimes called the
        interleave period).
        """

        for stim_client in stim_clients:
            stim_client.request('set_idle_background', [color])

        return 0

    ####################################
    # set up the server
    ####################################

    # Set up the RPC server
    server = SimpleXMLRPCServer(addr=('127.0.0.1', port), logRequests=False)

    # Register stimulus control functions
    server.register_function(load_stim, 'load_stim')
    server.register_function(start_stim, 'start_stim')
    server.register_function(stop_stim, 'stop_stim')

    # corner square control functions
    server.register_function(start_corner_square, 'start_corner_square')
    server.register_function(stop_corner_square, 'stop_corner_square')
    server.register_function(white_corner_square, 'white_corner_square')
    server.register_function(black_corner_square, 'black_corner_square')
    server.register_function(show_corner_square, 'show_corner_square')
    server.register_function(hide_corner_square, 'hide_corner_square')

    # background control functions
    server.register_function(set_idle_background, 'set_idle_background')

    ####################################
    # run the application
    ####################################

    # Print the port name (mainly relevant when port=0, meaning that the
    # port number is automatically selected
    port = server.socket.getsockname()[1]
    print('Display server port: {}'.format(port))

    # Run server
    print('Press Ctrl+C to exit.')
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
