"""
Base stimulus class.

Handles GL context, shader programs common to all flystim stim classes.

See flystim.stimuli for available child stimulus classes. Overwrite methods in child classes like:
    configure
    eval_at

"""

import moderngl


class BaseProgram:
    def __init__(self, screen, num_tri=500):
        """
        :param screen: Object containing screen size information
        """
        # set screen
        self.screen = screen
        self.num_tri = num_tri
        self.use_texture = False
        self.texture = None
        self.draw_mode = 'TRIANGLES' # TRIANGLES, POINTS
        self.point_size = 2 # pixels on screen, only for POINTS draw_mode

    def initialize(self, ctx):
        """
        :param ctx: ModernGL context
        """
        # save context
        self.ctx = ctx
        self.prog = self.create_prog()

        self.update_vertex_objects()

        if self.use_texture:
            self.prog['use_texture'].value = True
        else:
            self.prog['use_texture'].value = False

    def configure(self, *args, **kwargs):
        pass

    def paint_at(self, t, viewports, perspectives, fly_position=[0, 0, 0]):
        """
        :param t: current time in seconds
        :param viewports: list of viewport arrays for each subscreen - (xmin, ymin, width, height) in display device pixels
        :param perspectives: list of perspective matrices for each subscreen, generated using perspective.GenPerspective and subscreen corners
        :param fly_position: x, y, z position of fly (meters)
        """
        self.eval_at(t, fly_position=fly_position) # update any stim objects that depend on fly position

        data = self.stim_object.data # get stim object vertex data
        self.update_vertex_objects()

        if self.use_texture:
            vertices = len(data) // 9
        else:
            vertices = len(data) // 7

        # write data to VBO
        self.vbo.write(data.astype('f4'))

        # Render to each subscreen
        for v_ind, vp in enumerate(viewports):
            # set the perspective matrix
            self.prog['Mvp'].write(perspectives[v_ind])
            # set the viewport
            self.ctx.viewport = vp

            # render the object
            if self.draw_mode == 'POINTS':
                self.vao.render(mode=moderngl.POINTS, vertices=vertices)
                self.ctx.point_size=self.point_size
            elif self.draw_mode == 'TRIANGLES':
                self.vao.render(mode=moderngl.TRIANGLES, vertices=vertices)

    def update_vertex_objects(self):
        if self.use_texture:
            # 3 points, 9 values (3 for vert, 4 for color, 2 for tex_coords), 4 bytes per value
            self.vbo = self.ctx.buffer(reserve=self.num_tri*3*9*4)
            self.vao = self.ctx.simple_vertex_array(self.prog, self.vbo, 'in_vert', 'in_color', 'in_tex_coord')
        else:
            # basic, no-texture vbo and vao:
            self.vbo = self.ctx.buffer(reserve=self.num_tri*3*7*4)  # 3 points, 7 values, 4 bytes per value
            self.vao = self.ctx.simple_vertex_array(self.prog, self.vbo, 'in_vert', 'in_color')

    def add_texture_gl(self, texture_image, texture_interpolation='LINEAR'):
        self.texture = self.ctx.texture(size=(texture_image.shape[1], texture_image.shape[0]),
                                        components=1,
                                        data=texture_image.tobytes())  # size = (width, height)

        if texture_interpolation == 'NEAREST':
            self.texture.filter = (moderngl.NEAREST, moderngl.NEAREST)
        elif texture_interpolation == 'LINEAR':
            self.texture.filter = (moderngl.LINEAR, moderngl.LINEAR)
        else:
            self.texture.filter = (moderngl.LINEAR, moderngl.LINEAR)

        self.texture.use()

    def update_texture_gl(self, texture_image):
        self.texture.write(data=texture_image.tobytes())

    def eval_at(self, t, fly_position=[0, 0, 0]):
        """
        :param t: current time in seconds
        """

        pass

    def create_prog(self):

        return self.ctx.program(vertex_shader=self.get_vertex_shader(), fragment_shader=self.get_fragment_shader())

    def get_vertex_shader(self):
        vertex_shader = '''
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
        '''
        return vertex_shader

    def get_fragment_shader(self):
        fragment_shader = '''
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
                    f_color.a = v_color.a;
                } else {
                    f_color.rgb = v_color.rgb;
                    f_color.a = v_color.a;
                }
            }
        '''

        return fragment_shader
