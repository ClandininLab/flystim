# ref: http://csc.lsu.edu/~kooima/articles/genperspective/

import numpy as np
import moderngl
from flystim import normalize, rotx, roty, rotz

class CaveSystem:
    def __init__(self, num_tri=200):
        # save settings
        self.num_tri = num_tri

        # initialize
        self.subscreens = []

    def add_subscreen(self, viewport, perspective):
        self.subscreens.append((viewport, perspective))

    def initialize(self, display):
        self.ctx = display.ctx
        self.prog = self.create_prog()
        self.update_vertex_objects()

    def update_vertex_objects(self, use_texture=False):
        if use_texture:
            # 3 points, 9 values (3 for vert, 4 for color, 2 for tex_coords), 4 bytes per value
            self.vbo = self.ctx.buffer(reserve=self.num_tri*3*9*4)
            self.vao = self.ctx.simple_vertex_array(self.prog, self.vbo, 'in_vert', 'in_color', 'in_tex_coord')
        else:
            # basic, no-texture vbo and vao:
            self.vbo = self.ctx.buffer(reserve=self.num_tri*3*7*4) # 3 points, 7 values, 4 bytes per value
            self.vao = self.ctx.simple_vertex_array(self.prog, self.vbo, 'in_vert', 'in_color')

    def add_texture(self, texture_img):
        self.texture = self.ctx.texture(size=(texture_img.shape[1], texture_img.shape[0]),
                                        components=1,
                                        data=texture_img.tobytes()) # size = (width, height)
        self.texture.use()

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
        data = obj.data

        if texture_img is not None:
            self.update_vertex_objects(use_texture=True)
            self.prog['use_texture'].value = True
            self.add_texture(texture_img)
            vertices = len(data) // 9
        else:
            self.update_vertex_objects(use_texture=False)
            self.prog['use_texture'].value = False
            vertices = len(data) // 7

        # write data to VBO
        self.vbo.write(data.astype('f4'))

        # render each viewport separately
        for viewport, perspective in self.subscreens:
            # set the viewport
            self.ctx.viewport = viewport
            # set the perspective matrix
            self.prog['Mvp'].write(perspective.matrix.astype('f4').tobytes(order='F'))
            # render the objects
            self.vao.render(mode=moderngl.TRIANGLES, vertices=vertices)
