from PyQt5 import QtOpenGL, QtWidgets, QtCore

import sys
import signal
import moderngl
import numpy as np
import os.path
from argparse import ArgumentParser

class DarkDisplay(QtOpenGL.QGLWidget):
    """
    Class that controls the stimulus display on one screen.  It contains the pyglet window object for that screen,
    and also controls rendering of the stimulus, toggling corner square, and/or debug information.
    """

    def __init__(self, app):
        # call super constructor
        super().__init__(self.make_qt_format())
        self.app = app

    def initializeGL(self):
        # get OpenGL context
        self.ctx = moderngl.create_context()

    def paintGL(self):
        # set the viewport to fill the window
        # ref: https://github.com/pyqtgraph/pyqtgraph/issues/422
        self.ctx.viewport = (0, 0, self.width()*self.devicePixelRatio(), self.height()*self.devicePixelRatio())

        # clear the display
        self.ctx.clear(0, 0, 0, 1)
        self.ctx.enable(moderngl.BLEND)

        # update the window
        self.update()

    @classmethod
    def make_qt_format(cls, vsync=True):
        """
        Initializes the Qt OpenGL format.
        :param vsync: If True, use VSYNC, otherwise update as fast as possible
        """

        # create format with default settings
        format = QtOpenGL.QGLFormat()

        # use OpenGL 3.3
        format.setVersion(3, 3)
        format.setProfile(QtOpenGL.QGLFormat.CoreProfile)

        # use VSYNC
        if vsync:
            format.setSwapInterval(1)
        else:
            format.setSwapInterval(0)

        # TODO: determine what these lines do and whether they are necessary
        format.setSampleBuffers(True)
        format.setDepthBufferSize(24)

        # needed to enable transparency
        format.setAlpha(True)

        return format


def main():
    parser = ArgumentParser()
    parser.add_argument('--windowed', action='store_true')
    args = parser.parse_args()

    # launch application
    app = QtWidgets.QApplication([])

    stim_display = DarkDisplay(app=app)

    # display the stimulus
    if not args.windowed:
        stim_display.showFullScreen()
    else:
        stim_display.show()

    ####################################
    # Run QApplication
    ####################################

    # Use Ctrl+C to exit.
    # ref: https://stackoverflow.com/questions/2300401/qapplication-how-to-shutdown-gracefully-on-ctrl-c
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
