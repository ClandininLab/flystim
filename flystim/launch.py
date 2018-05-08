import subprocess
import os.path
import sys

from time import time
from xmlrpc.server import SimpleXMLRPCServer

from flystim.rpc import RpcClient
from flystim.screen import Screen

def create_stim_process(screen):
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

    # launch the display program
    args = [python_full_path, server_full_path]
    args += ['--id', str(screen.id)]
    args += ['--pa'] + list(str(v) for v in screen.pa)
    args += ['--pb'] + list(str(v) for v in screen.pb)
    args += ['--pc'] + list(str(v) for v in screen.pc)
    if screen.fullscreen:
        args += ['--fullscreen']
    p = subprocess.Popen(args, stdin=subprocess.PIPE)

    # return the process
    return p

class StimClient(RpcClient):
    """
    Class used to send commands to a single screen display program using a PIPE.
    """

    def __init__(self, process):
        super().__init__(s=process.stdin)

    def load_stim(self, name, params):
        """
        Loads the stimulus with the given name, using the given params.  After the stimulus is loaded, the
        background color is changed to the one specified in the stimulus, and the stimulus is evaluated at time 0.
        :param name: Name of the stimulus (should be a class name)
        :param params: Parameters used to instantiate the class (e.g., period, bar width, etc.)
        """

        self.handle(method='load_stim', args=[name, params])

    def start_stim(self, t):
        """
        Starts the stimulus animation, using the given time as t=0
        :param t: Time corresponding to t=0 of the animation
        """

        self.handle(method='start_stim', args=[t])

    def stop_stim(self):
        """
        Stops the stimulus animation and removes it from the display.  The background color reverts to idle_background
        """

        self.handle(method='stop_stim', args=[])

def launch(screens, port=0):
    """
    Launches separate processes to display synchronized stimuli on all of the given screens.  After that, a
    remote procedure call (RPC) server is launched, which allows the user to send commands to all screens at once.
    :param screens: List of screens on which the stimuli should be displayed.  Each should be a Screen object defining
    the screen coordinates, id #, etc.
    :param port: Socket port number to be used for sending stimulus commands.  The default value (0) means that a port
    will be assigned automatically, and the chosen port will be printed out.
    """

    # Launch a separate display process for each screen
    processes = [create_stim_process(screen) for screen in screens]

    # Create RPC handlers for each process
    stim_clients = [StimClient(process) for process in processes]

    # Define RPC methods used to interact with the ensemble of screens

    def load_stim(name, params):
        """
        Loads the stimulus with the given name, using the given params.  After the stimulus is loaded, the
        background color is changed to the one specified in the stimulus, and the stimulus is evaluated at time 0.
        :param name: Name of the stimulus (should be a class name)
        :param params: Parameters used to instantiate the class (e.g., period, bar width, etc.)
        """

        for stim_client in stim_clients:
            stim_client.load_stim(name, params)

        return 0

    def start_stim():
        """
        Starts the stimulus animation, using exactly the same start time for all screens.
        """

        t = time()
        for stim_client in stim_clients:
            stim_client.start_stim(t)

        return 0

    def stop_stim():
        """
        Stops the stimulus animation and removes it from the displays.  The background color reverts to idle_background.
        """

        for stim_client in stim_clients:
            stim_client.stop_stim()

        return 0

    # Set up the RPC server
    server = SimpleXMLRPCServer(addr=('127.0.0.1', port), logRequests=False)

    # Print the port name (mainly relevant when port=0, meaning that the
    # port number is automatically selected
    port = server.socket.getsockname()[1]
    print('Stimulus Display Port: {}'.format(port))

    # Register stimulus control functions
    server.register_function(load_stim, 'load_stim')
    server.register_function(start_stim, 'start_stim')
    server.register_function(stop_stim, 'stop_stim')

    # Run server
    # Use Ctrl+C to exit.
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass

def main():
    screens = [Screen(fullscreen=False)]
    launch(screens)

if __name__ == '__main__':
    main()