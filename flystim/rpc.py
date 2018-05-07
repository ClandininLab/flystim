import sys
import json
from threading import Thread
from queue import Queue, Empty

# function to feed lines from a stream to a queue
def stream_to_queue(s, q):
    for line in s:
        q.put(line)

class RpcServer:
    def __init__(self, s=None):
        # set defaults
        if s is None:
            s = sys.stdin

        # create thread to handle I/O
        self.s = s
        self.q = Queue()
        self.t = Thread(target=stream_to_queue, args=(self.s, self.q))
        self.t.daemon = True
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
            kwargs = request.get('kwargs', {})

            # run command
            self.handle(method=method, args=args, kwargs=kwargs)

    def handle(self, method, args, kwargs):
        pass

class RpcClient:
    def __init__(self, s):
        self.s = s

    def handle(self, method, args, kwargs):
        # generate request string
        request = json.dumps({'method': method, 'args': args, 'kwargs': kwargs})

        # write request
        # TODO: is ASCII encoding the right one?
        # TODO: is flush necessary?
        self.s.write((request + '\n').encode('ascii'))
        self.s.flush()