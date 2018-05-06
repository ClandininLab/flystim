import subprocess
import os.path
import sys
import json

from time import sleep, time

def launch():
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
    p = subprocess.Popen(args, stdin=subprocess.PIPE)

    # return the process
    return p

def main():
    p = launch()

    request = ['load_stim', {'name': 'RotatingBars'}]
    p.stdin.write((json.dumps(request)+'\n').encode('ascii'))
    p.stdin.flush()

    sleep(3)

    request = ['start_stim', {'t': time()}]
    p.stdin.write((json.dumps(request)+'\n').encode('ascii'))
    p.stdin.flush()

    sleep(3)

    request = ['stop_stim', {}]
    p.stdin.write((json.dumps(request)+'\n').encode('ascii'))
    p.stdin.flush()

    sleep(3)

    p.wait()

if __name__ == '__main__':
    main()