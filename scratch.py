#!/usr/bin/env python3
import moderngl
import moderngl_window
import time
from time import sleep
from PyQt5 import QtOpenGL, QtWidgets
import sys
import signal
import numpy as np

class StimDisplay(QtOpenGL.QGLWidget):
    def __init__(self):
        super().__init__()
        pass

    def create_prog(self):
        return self.ctx.program(
            vertex_shader='''
                #version 330

                in vec2 pos;

                void main() {
                    // assign gl_Position
                    gl_Position = vec4(pos, 0.0, 1.0);
                }
            ''',
            fragment_shader='''
                #version 330

                uniform float color;

                out vec4 out_color;

                void main() {
                    // assign output color based on uniform input
                    out_color = vec4(color, color, color, 1.0);
                }
            '''
        )

    def initializeGL(self):
        # get OpenGL context
        self.ctx = moderngl.create_context()
        self.ctx.enable(moderngl.BLEND) # enable alpha blending
        self.ctx.enable(moderngl.DEPTH_TEST) # enable depth test

        self.prog = self.create_prog()

        x_min = -1
        x_max = 1
        y_min = -1
        y_max = 1
        data = np.array([x_min, y_min, x_max, y_min, x_min, y_max, x_max, y_max])

        self.vbo = self.ctx.buffer(data.astype('f4').tobytes())
        self.vao = self.ctx.simple_vertex_array(self.prog, self.vbo, 'pos')

        # self.ctx.viewport = [50, 50, 100, 100]
        self.viewports = ([50, 50, 100, 100],
                          [250, 150, 100, 100])
        # self.ctx.viewport = (0, 0, self.width()*self.devicePixelRatio(), self.height()*self.devicePixelRatio())
        self.ctx.disable(moderngl.DEPTH_TEST) # disable depth test so square is painted on top always

    def paintGL(self):
        for vp in self.viewports:
            self.ctx.viewport = vp

            # write color
            t = time.time()
            f = 2
            self.prog['color'].value = np.sin(2*np.pi*f*t)

            # render to screen
            self.vao.render(mode=moderngl.TRIANGLE_STRIP)



            self.ctx.finish()
            self.update()


def main():
    # launch application
    app = QtWidgets.QApplication([])

    # create the StimDisplay object
    stim_display = StimDisplay()

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
