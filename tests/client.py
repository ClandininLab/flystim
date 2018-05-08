from xmlrpc.client import ServerProxy
from time import sleep

from random import choice

def main():
    client = ServerProxy('http://127.0.0.1:62632')

    dirs = [-1, 1]
    rates = [10, 20, 40, 100, 200, 400, 1000]

    while True:
        dir = choice(dirs)
        rate = dir*choice(rates)

        client.load_stim('RotatingBars', {'rate': rate})

        sleep(550e-3)
        client.start_stim()
        sleep(250e-3)
        client.stop_stim()
        sleep(500e-3)

if __name__ == '__main__':
    main()