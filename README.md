# Introduction

**flystim** is a software package for generating visual stimuli for fruit fly experiments.  The stimuli are perspective-corrected and can be displayed across multiple screens.

In this software package, a server displays stimuli in response to commands from a client.  This allows users to write relatively concise experimental control programs.

The server is a Python program, while the client can be written in any language that supports [XML-RPC](https://en.wikipedia.org/wiki/XML-RPC).  Sample client code is included in the **examples** directory.

# Installation

First open a terminal and navigate to a convenient directory.  Then download and install the latest **flystim** codebase:

```shell
> git clone https://github.com/ClandininLab/flystim.git
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
