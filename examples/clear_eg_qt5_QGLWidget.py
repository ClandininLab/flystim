import sys, signal
import numpy as np
import moderngl

from PyQt5 import QtWidgets
from PyQt5.QtOpenGL import QGLWidget
from PyQt5.QtOpenGL import QGLFormat

def make_qt_format():
    fmt = QGLFormat()
    fmt.setVersion(3, 3)
    fmt.setProfile(QGLFormat.CoreProfile)
    return fmt

class StimDisplay(QGLWidget):
    def __init__(self, app):
        super().__init__(make_qt_format())


        self.app = app

        self.context = None
        self.vao = None

        self.subscreen_viewports = [(0, 0, 100, 100),
                                    (101, 0, 100, 100),
                                    (51, 101, 100, 100)]

        self.frame_cnt = 0

    def initializeGL(self):
        # Create ModernGL context
        self.context = moderngl.create_context()

        # Triangle vertices (x, y)
        vertices = np.array([
            -0.6, -0.6,
             0.6, -0.6,
             0.0,  0.6
        ], dtype='f4')

        # Vertex Buffer Object
        vbo = self.context.buffer(vertices)

        # Vertex Array Object
        self.vao = self.context.simple_vertex_array(
            self.context.program(
                vertex_shader="""
                #version 330
                in vec2 in_vert;
                void main() {
                    gl_Position = vec4(in_vert, 0.0, 1.0);
                }
                """,
                fragment_shader="""
                #version 330
                out vec4 fragColor;
                void main() {
                    fragColor = vec4(1.0, 0.0, 0.0, 1.0);  // Red color
                }
                """,
            ),
            vbo,
            'in_vert'
        )

    def paintGL(self):
        # Clear the buffer
        # self.context.clear(0.5, 0.5, 0.5, 1.0)

        print(f"Frame # {self.frame_cnt}")
        if self.frame_cnt % 2 == 0:
            print("Clearing context!")
        else:
            print("Not clearing context!")

        for vp in self.subscreen_viewports:
            self.context.viewport = vp

            if self.frame_cnt % 2 == 0:
                self.context.clear(0.5, 0.5, 0.5, 1.0, viewport=vp)

            # Render the triangle
            self.vao.render(moderngl.TRIANGLES)

        self.frame_cnt += 1

def main():

    # set default format with OpenGL context
    QGLFormat.setDefaultFormat(make_qt_format())

    # launch application
    app = QtWidgets.QApplication([])

    # create the StimDisplay object
    stim_display = StimDisplay(app=app)
    stim_display.setGeometry(100, 100, 200, 200)
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
