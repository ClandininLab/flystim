# ref: http://csc.lsu.edu/~kooima/articles/genperspective/

import numpy as np
import moderngl
from flystim import normalize, rotx, roty, rotz, rel_path
import os

class CaveSystem:
    def __init__(self, num_tri=200):
        # save settings
        self.num_tri = num_tri
        self.use_texture = False

        # initialize
        self.subscreens = []

    def add_subscreen(self, viewport, perspective):
        self.subscreens.append((viewport, perspective))

    def initialize(self, display):
        self.ctx = display.ctx
        self.prog = self.create_prog()

        # basic, no-texture vbo and vao
        self.vbo = self.ctx.buffer(reserve=self.num_tri*3*7*4) # 3 points, 7 values, 4 bytes per value
        self.vao = self.ctx.simple_vertex_array(self.prog, self.vbo, 'in_vert', 'in_color')
        self.prog['use_texture'].value = self.use_texture

    def add_texture(self, texture_img):
        self.use_texture = True
        # 3 points, 9 values (3 for vert, 4 for color, 2 for tex_coordscoord), 4 bytes per value
        self.vbo = self.ctx.buffer(reserve=self.num_tri*3*9*4)
        self.vao = self.ctx.simple_vertex_array(self.prog, self.vbo, 'in_vert', 'in_color', 'in_tex_coord')

        self.texture = self.ctx.texture(texture_img.shape, 1, texture_img.tobytes(), alignment=4)
        self.texture.use()
        self.prog['use_texture'].value = self.use_texture

    def create_prog(self):
        return self.ctx.program(
            vertex_shader='''
                #version 330

                in vec3 in_vert;
                in vec4 in_color;
                in vec2 in_tex_coord;

                out vec4 v_color;
                out vec2 v_tex_coord;

                uniform mat4 Mvp;

                void main() {
                    v_color = in_color;
                    v_tex_coord = in_tex_coord;
                    gl_Position = Mvp * vec4(in_vert, 1.0);
                }
            ''',
            fragment_shader='''
                #version 330

                in vec4 v_color;
                in vec2 v_tex_coord;

                uniform bool use_texture;
                uniform sampler2D texture_matrix;

                out vec4 f_color;

                void main() {
                    if (use_texture) {
                        vec4 texFrag = texture(texture_matrix, v_tex_coord);
                        f_color.rgb = texFrag.r * v_color.rgb;
                        f_color.a = 1;
                    } else {
                        f_color.rgb = v_color.rgb;
                        f_color.a = 1;
                    }
                }
            '''
        )

    def render(self, obj, texture_img=None):
        if texture_img is not None:
            self.add_texture(texture_img)
        # write data to VBO
        data = obj.data
        self.vbo.write(data.astype('f4'))

        # compute the number of vertices
        if self.use_texture:
            vertices = len(data) // 9
        else:
            vertices = len(data) // 7

        # render each viewport separately
        for viewport, perspective in self.subscreens:
            # set the viewport
            self.ctx.viewport = viewport
            # set the perspective matrix
            self.prog['Mvp'].write(perspective.matrix.astype('f4').tobytes(order='F'))
            # render the objects
            self.vao.render(mode=moderngl.TRIANGLES, vertices=vertices)

class GenPerspective:
    def __init__(self, pa, pb, pc, pe=(0, 0, 0), near=0.1, far=100):
        # save settings
        self.pa = pa
        self.pb = pb
        self.pc = pc
        self.pe = pe
        self.near = near
        self.far = far

    @property
    def matrix(self):
        # format vectors as numpy arrays
        pa = np.array(self.pa, dtype=float)
        pb = np.array(self.pb, dtype=float)
        pc = np.array(self.pc, dtype=float)
        pe = np.array(self.pe, dtype=float)

        # make aliases for "near" and "far" so that the code is easier to read
        n = self.near
        f = self.far

        # compute vector normals
        vr = normalize(pb - pa)
        vu = normalize(pc - pa)
        vn = normalize(np.cross(vr, vu))

        # compute relative position of screen
        va = pa - pe
        vb = pb - pe
        vc = pc - pe

        # compute distance parameters
        d = -np.dot(vn, va)
        l = np.dot(vr, va) * n / d
        r = np.dot(vr, vb) * n / d
        b = np.dot(vu, va) * n / d
        t = np.dot(vu, vc) * n / d

        # create projection matrices
        P =  np.array([[2*n/(r-l),         0,  (r+l)/(r-l),            0],
                       [        0, 2*n/(t-b),  (t+b)/(t-b),            0],
                       [        0,         0, -(f+n)/(f-n), -2*f*n/(f-n)],
                       [        0,         0,           -1,            0]], dtype=float)
        M = np.array([[vr[0], vu[0], vn[0], 0],
                      [vr[1], vu[1], vn[1], 0],
                      [vr[2], vu[2], vn[2], 0],
                      [    0,     0,     0, 1]], dtype=float)
        T = np.array([[1, 0, 0, -pe[0]],
                      [0, 1, 0, -pe[1]],
                      [0, 0, 1, -pe[2]],
                      [0, 0, 0,      1]], dtype=float)

        # return overall projection matrix
        return P.dot((M.T).dot(T))

    # rotating the screen on three axes is mostly for testing purposes

    def rotx(self, th):
        return GenPerspective(pa=rotx(self.pa, th), pb=rotx(self.pb, th), pc=rotx(self.pc, th),
                              pe=rotx(self.pe, th), near=self.near, far=self.far)

    def roty(self, th):
        return GenPerspective(pa=roty(self.pa, th), pb=roty(self.pb, th), pc=roty(self.pc, th),
                              pe=roty(self.pe, th), near=self.near, far=self.far)

    def rotz(self, th):
        return GenPerspective(pa=rotz(self.pa, th), pb=rotz(self.pb, th), pc=rotz(self.pc, th),
                              pe=rotz(self.pe, th), near=self.near, far=self.far)
