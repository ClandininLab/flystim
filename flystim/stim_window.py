# modified from https://github.com/cprogrammer1994/ModernGL/blob/master/examples/example_window.py

import moderngl
from PyQt5 import QtOpenGL, QtWidgets

class StimWindow(QtOpenGL.QGLWidget):
    def __init__(self, stim_gl, width, height, title):

        ######################
        # set up format
        ######################

        # create format with default settings
        format = QtOpenGL.QGLFormat()

        # use OpenGL 3.3
        format.setVersion(3, 3)
        format.setProfile(QtOpenGL.QGLFormat.CoreProfile)

        # use VSYNC
        format.setSwapInterval(1)

        # TODO: determine what these lines do and whether they are necessary
        format.setSampleBuffers(True)
        format.setDepthBufferSize(24)

        # call super constructor with this format
        super().__init__(format)

        ######################
        # set up window
        ######################

        # set the window size
        self.setFixedSize(width, height)

        # set the window title
        self.setWindowTitle(title)

        ######################
        # set up stimulus
        ######################

        # save the stimulus
        self.stim_gl = stim_gl

    def initializeGL(self):
        self.stim_gl.initialize(moderngl.create_context())

    def paintGL(self):
        self.stim_gl.paint()
        self.update()

def run_stim(stim_gl, width, height, title):
    app = QtWidgets.QApplication([title])

    widget = StimWindow(stim_gl=stim_gl, width=width, height=height, title=title)
    widget.show()

    app.exec_()

