import subprocess
import os.path
import sys

from time import time
from xmlrpc.server import SimpleXMLRPCServer

from flystim.rpc import RpcClient
from flystim.screen import Screen

def create_stim_process(screen):
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
    def __init__(self, process):
        super().__init__(s=process.stdin)

    def load_stim(self, *args, **kwargs):
        self.handle(method='load_stim', args=args, kwargs=kwargs)

    def start_stim(self, *args, **kwargs):
        self.handle(method='start_stim', args=args, kwargs=kwargs)

    def stop_stim(self, *args, **kwargs):
        self.handle(method='stop_stim', args=args, kwargs=kwargs)

def launch(screens, port=0):
    # Launch a separate display process for each screen
    processes = [create_stim_process(screen) for screen in screens]

    # Create RPC handlers for each process
    stim_clients = [StimClient(process) for process in processes]

    # Define RPC methods used to interact with the ensemble of screens

    def load_stim(name, kwargs):
        for stim_client in stim_clients:
            stim_client.load_stim(name, **kwargs)

        return 0

    def start_stim():
        t = time()
        for stim_client in stim_clients:
            stim_client.start_stim(t)

        return 0

    def stop_stim():
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
    server.serve_forever()

def main():
    screens = [Screen(fullscreen=False)]
    launch(screens)

if __name__ == '__main__':
    main()