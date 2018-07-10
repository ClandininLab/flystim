import sys
from threading import Thread
from queue import Queue, Empty

from jsonrpc import JSONRPCResponseManager
from jsonrpc.jsonrpc2 import JSONRPC20Request, JSONRPC20BatchRequest

# This file contains a simple stream-based remote procedure call system
# The work is inspired by this StackOverflow post:
# https://stackoverflow.com/questions/375427/non-blocking-read-on-a-subprocess-pipe-in-python

def stream_to_queue(s, q):
    """
    Function that copies a stream output into a queue, line by line.
    :param s: Stream
    :param q: Queue
    """

    while True:
        # read next line from stream (blocking call)
        line = s.readline()

        # put the line into the queue
        q.put(line)

def request(method, *args, **kwargs):
    """
    Returns a single JSON RPC 2.0 request.
    :param method: Name of the method.
    :param params: Positional or keyword arguments of the method
    """

    if args:
        if kwargs:
            raise ValueError('Cannot use both positional and keyword arguments.')
        else:
            params = args
    else:
        params = kwargs

    return JSONRPC20Request(method=method, params=params, is_notification=True)

class Server:
    """
    This class is intended to be scheduled to run inside an event loop.  It launches a thread to store each line of
    the stream into a queue.  The lines are then processed as remote procedure calls according to the JSON RPC
    specification.
    """

    def __init__(self, dispatcher):
        # save dispatcher
        self.dispatcher = dispatcher

        # create a queue to hold I/O
        self.q = Queue()

        # create thread to handle I/O
        self.t = Thread(target=stream_to_queue, args=(sys.stdin, self.q))

        # the I/O thread is set as a daemon to allow the program to exit cleanly
        # in general, this flag means "exit program when only daemon threads are left"
        self.t.daemon = True

        # start I/O thread
        self.t.start()

    def process(self):
        """
        This is the function that should be scheduled to run in the event loops.  It processes all of the lines in
        the queue as RPCs before returning.
        """

        while True:
            try:
                request_str = self.q.get_nowait()
            except Empty:
                break

            # strip whitespace from the request
            request_str = request_str.strip()

            # if line is now empty (i.e., it was all whitespace), skip to the next line
            if request_str == '':
                continue

            # handle the request(s)
            JSONRPCResponseManager.handle(request_str, self.dispatcher)

class Client:
    """
    This class sends commands to an Server via a PIPE.  The JSON 2.0 specification is used.
    """

    def __init__(self, s):
        """
        :param s: Stream to be used to transmitting RPCs
        """

        self.s = s

    def batch(self, *requests):
        """
        Sends a batch of requests to the server.
        """

        self.write(JSONRPC20BatchRequest(*requests))

    def write(self, request):
        self.s.write((request.json + '\n').encode('utf-8'))
        self.s.flush()
