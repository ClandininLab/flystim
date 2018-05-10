import sys
import json
from threading import Thread
from queue import Queue, Empty

# This file contains a simple stream-based remote procedure call system
# The work is inspired by this StackOverflow post:
# https://stackoverflow.com/questions/375427/non-blocking-read-on-a-subprocess-pipe-in-python

def stream_to_queue(s, q):
    """
    Function that copies a stream output into a queue, line by line
    :param s: Stream
    :param q: Queue
    """

    while True:
        # read next line from stream
        # this is a blocking call, so the line will stall until input is received
        line = s.readline()

        # strip whitespace from ends and make sure that this isn't an empty line
        # this is necessary because empty lines are transmitted when Ctrl+C is pressed,
        # which sometimes causes the JSON decoder to fail.
        line = line.strip()
        if line != '':
            q.put(line)

class RpcServer:
    """
    This class is intended to be scheduled to run inside an event loop such as pyglet.app.run()
    It launches a thread to store each line of the stream into a queue.  The lines are then processed as remote
    procedure calls.
    """

    def __init__(self, s=None):
        """
        :param s: Stream containing RPCs (defaults to sys.stdin)
        """

        # set defaults
        if s is None:
            s = sys.stdin

        # save settings
        self.s = s

        # initialize function mapping
        self.functions = {}

        # create a queue to hold I/O
        self.q = Queue()

        # create thread to handle I/O
        self.t = Thread(target=stream_to_queue, args=(self.s, self.q))

        # the I/O thread is set as a daemon to allow the program to exit cleanly
        # in general, this flag means "exit program when only daemon threads are left"
        self.t.daemon = True

        # start I/O thread
        self.t.start()

    def update(self):
        """
        This is the function that should be scheduled to run in the event loops.  It processes all of the lines in
        the queue as RPCs before returning.
        """

        while True:
            try:
                line = self.q.get_nowait()
            except Empty:
                break

            # parse request
            request = json.loads(line)

            # extract method name and arguments
            method = request['method']
            args = request.get('args', [])

            # run command
            self.functions[method](*args)

    def register_function(self, function, name):
        self.functions[name] = function

class RpcClient:
    """
    This class sends commands to an RpcServer via a PIPE.  JSON encoding is used for the RPCs.
    """

    def __init__(self, s):
        """
        :param s: Stream to be used to transmitting RPCs
        """
        self.s = s

    def request(self, method, args=None):
        """
        Sends a single command to the RPC server.
        :param method: Name of the method.
        :param args: Positional arguments of the method.
        """

        # build request
        request = {'method': method}

        if args is not None:
            request['args'] = args

        # convert request to JSON format
        request_json = json

        # write request
        self.s.write((json.dumps(request) + '\n').encode('utf-8'))
        self.s.flush()
