# Introduction

**flystim** is a software package for generating visual stimuli for fruit fly experiments.  The stimuli are perspective-corrected and can be displayed across multiple screens.

In this software package, a server displays stimuli in response to commands from a client.  This allows users to write relatively concise experimental control programs, such as the following example:

```python
client = ServerProxy('http://127.0.0.1:{}'.format(port))

dirs = [-1, 1]
rates = [10, 20, 40, 100, 200, 400, 1000]

for _ in range(num_trials):
    dir = choice(dirs)
    rate = dir*choice(rates)

    client.load_stim('RotatingBars', {'rate': rate})

    sleep(550e-3)
    client.start_stim()
    sleep(250e-3)
    client.stop_stim()
    sleep(500e-3)
```

The server is a Python program, while the client can be written in any language that supports [XML-RPC](https://en.wikipedia.org/wiki/XML-RPC).  Sample client code is included in the **examples** directory.

# Installation

First open a terminal and navigate to a convenient directory.  Then download and install the latest **flystim** codebase:

```shell
> git clone https://github.com/sgherbst/flystim.git
> cd flystim
> pip3 install -e .
```

This should install the Python package dependencies (pyglet, numpy, and scipy) if you don't already have them.

# Running the Example Code

In one terminal tab, launch the server:

```shell
> cd flystim/examples
> python3 server.py
```

Then, in a second terminal tab, launch the client:

```shell
> cd flystim/examples
> python3 client.py
```

The client program should run for about 20 seconds before completing.  However, the server will still be active and ready to accept further commands at that point.  When you are ready to exit the server, go back to the server's terminal tab and press Ctrl+C.
