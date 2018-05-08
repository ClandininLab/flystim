import sys
import json
from threading import Thread
from queue import Queue, Empty

# simple stream-based remote procedure calls
# inspired by this post:
# https://stackoverflow.com/questions/375427/non-blocking-read-on-a-subprocess-pipe-in-python

# function that copies a stream to
# a queue, line by line
def stream_to_queue(s, q):
    while True:
        q.put(s.readline())

class RpcServer:
    def __init__(self, s=None):
        # set defaults
        if s is None:
            s = sys.stdin

        # create thread to handle I/O
        self.s = s
        self.q = Queue()
        self.t = Thread(target=stream_to_queue, args=(self.s, self.q))

        # the I/O thread is set as a daemon to allow the program to exit cleanly
        # in general, this flag means "exit program when only daemon threads are left"
        self.t.daemon = True

        # start I/O thread
        self.t.start()

    def update(self):
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
            self.handle(method=method, args=args)

    def handle(self, method, args):
        pass

class RpcClient:
    def __init__(self, s):
        self.s = s

    def handle(self, method, args):
        # generate request string
        request = json.dumps({'method': method, 'args': args})

        # write request
        self.s.write((request + '\n').encode('utf-8'))
        self.s.flush()