# Introduction

**flystim** is a software package for generating visual stimuli for fruit fly experiments.  The stimuli are perspective-corrected and can be displayed across multiple screens with varying size and placement.

The software package using a server-client model: a server displays the stimuli in response to commands from the client.  This allows the client to control the logical flow of the experiment, without having to implement low-level graphics code.  As a result, experimental control code can be relatively concise, as in this example:

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

While the server is 

# Installation

First open a terminal and navigate to a convenient directory.  Then download and install the latest copy of the code:

```shell
> git clone https://github.com/sgherbst/flystim.git
> cd flystim
> pip3 install -e .
```

This should install the dependencies (pyglet, numpy, and scipy) if you don't already have them.

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
