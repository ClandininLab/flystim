import os
import os.path
import platform

from time import time

import flystim.framework
from flystim.rigs import get_screens

from flyrpc.transceiver import MySocketServer
from flyrpc.launch import launch_server
from flyrpc.util import get_kwargs

def launch_screen(screen):
    """
    This function launches a subprocess to display stimuli on a given screen.  In general, this function should
    be called once for each screen.
    :param screen: Screen object (from flystim.screen) that contains screen ID, dimensions, etc.
    :return: Subprocess object corresponding to the stimuli display program.
    """

    # set the arguments as necessary
    env = os.environ.copy()
    if platform.system() == 'Linux':
        env['DISPLAY'] = ':0.' + str(screen['id'])

    # launch the server and return the resulting client
    return launch_server(flystim.framework, screen=screen.serialize(), env=env)


class StimServer(MySocketServer):
    def __init__(self, screens, host=None, port=None, auto_stop=None):
        # call super constructor
        super().__init__(host=host, port=port, threaded=False, auto_stop=auto_stop)

        # launch screens
        self.clients = [launch_screen(screen=screen) for screen in screens]

    def handle_request_list(self, request_list):
        # make sure that request list is actually a list...
        if not isinstance(request_list, list):
            return

        # pre-process the request list as necessary
        for request in request_list:
            if isinstance(request, dict) and ('name' in request) and (request['name'] == 'start_stim'):
                request['args'] = [time()]
                request['kwargs'] = {}

        # send modified request list to clients
        for client in self.clients:
            client.write_request_list(request_list)

def run_stim_server(host=None, port=None, auto_stop=None, setup_name=None):
    # set defaults
    if setup_name is None:
        setup_name = 'macbook'

    # get the associated screens
    screens = get_screens(setup_name)

    # instantiate the server
    server = StimServer(screens=screens, host=host, port=port, auto_stop=auto_stop)

    # launch the server
    server.loop()

def main():
    # get the startup arguments
    kwargs = get_kwargs()

    # run the server
    run_stim_server(host=kwargs['host'], port=kwargs['port'], auto_stop=kwargs['auto_stop'],
                    setup_name=kwargs['setup_name'])

if __name__ == '__main__':
    main()