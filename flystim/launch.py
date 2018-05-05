import subprocess
import os.path
import sys
import psutil

from xmlrpc.client import ServerProxy
from flystim.server import ServerArgParser

tag = 'flystim-server'

class Screen:
    def __init__(self, id, pa, pb, pc):
        self.id = id
        self.pa = pa
        self.pb = pb
        self.pc = pc

def get_server_processes():
    parser = ServerArgParser()

    server_processes = []
    for process in psutil.process_iter():
        # get process name and make sure that it's valid
        name = process.name()
        if name is None or not isinstance(name, str):
            continue

        # keep only python scripts
        if 'python' not in name.lower():
            continue

        # get command line arguments and make sure they're valid
        cmdline = process.cmdline()
        if cmdline is None or not all(isinstance(elem, str) for elem in cmdline):
            continue

        # keep only those with a matching tag
        args, unknown = parser.parse_known_args(cmdline)
        if args.tag == tag:
            server_processes.append(process)

    return server_processes

def get_clients():
    server_processes = get_server_processes()

    clients = []
    for server_process in server_processes:
        connections = server_process.connections()
        assert len(connections) == 1

        laddr = connections[0].laddr

        server_addr = 'http://'
        server_addr += laddr.ip
        server_addr += ':'
        server_addr += str(laddr.port)

        client = ServerProxy(server_addr)
        clients.append(client)

    return clients

def launch(screens):
    # get full path to this file
    # ref: https://stackoverflow.com/questions/37863476/why-use-both-os-path-abspath-and-os-path-realpath/40311142
    file_path_full = os.path.realpath(os.path.expanduser(__file__))

    # get the full path of this directory
    dir_path_full = os.path.dirname(file_path_full)

    # get the full path of the server script
    server_full_path = os.path.join(dir_path_full, 'server.py')

    # get the path of the python executable
    python_full_path = os.path.realpath(os.path.expanduser(sys.executable))

    # launch the display server
    processes = []
    for screen in screens:
        args = [python_full_path, server_full_path, '--tag', tag]
        args += ['--id', str(screen.id)]
        args += ['--pa'] + [str(v) for v in screen.pa]
        args += ['--pb'] + [str(v) for v in screen.pb]
        args += ['--pc'] + [str(v) for v in screen.pc]

        process = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        processes.append(process)

    # stall indefinitely
    for process in processes:
        process.wait()

def main():
    screen = Screen(id=0, pa=[-1, -1, -1], pb=[1, -1, -1], pc=[-1, 1, -1])
    launch([screen])

if __name__ == '__main__':
    main()