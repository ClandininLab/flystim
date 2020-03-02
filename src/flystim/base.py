import moderngl


class BaseProgram:
    def __init__(self, screen, num_tri=500):
        """
        :param screen: Object containing screen size information
        """
        # set screen
        self.screen = screen
        self.num_tri = num_tri
        self.texture_image = None
        self.use_texture = False
        self.cylindrical_height_correction = False
        self.texture_interpolation = 'LINEAR' # LINEAR, NEAREST
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

    def configure(self, *args, **kwargs):
        pass

    def paint_at(self, t, perspective, fly_position=[0, 0, 0]):
        """
        :param t: current time in seconds
        """
        self.eval_at(t, fly_position=fly_position)

        data = self.stim_object.data
        self.update_vertex_objects()

        if self.cylindrical_height_correction:
            self.prog['height'].value = self.cylinder_height
            self.prog['radius'].value = self.cylinder_radius

        if self.use_texture:
            self.prog['use_texture'].value = True

            self.add_texture(self.texture_image)
            vertices = len(data) // 9
        else:
            self.prog['use_texture'].value = False

            vertices = len(data) // 7

        # write data to VBO
        self.vbo.write(data.astype('f4'))

        # set the perspective matrix
        self.prog['Mvp'].write(perspective.matrix.astype('f4').tobytes(order='F'))
        # render the objects

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

    def add_texture(self, texture_image):
        self.texture = self.ctx.texture(size=(texture_image.shape[1], texture_image.shape[0]),
                                        components=1,
                                        data=texture_image.tobytes())  # size = (width, height)
        if self.texture_interpolation == 'NEAREST':
            self.texture.filter = (moderngl.NEAREST, moderngl.NEAREST)
        elif self.texture_interpolation == 'LINEAR':
            self.texture.filter = (moderngl.LINEAR, moderngl.LINEAR)
        else:
            self.texture.filter = (moderngl.LINEAR, moderngl.LINEAR)

        self.texture.use()

    def eval_at(self, t, fly_position=[0, 0, 0]):
        """
        :param t: current time in seconds
        """

        pass

    def create_prog(self):
        # TODO: cylinder height correction seems to be off by a factor of 2 or something?

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
        if self.cylindrical_height_correction:
            fragment_shader = '''
                #version 330

                in vec4 v_color;
                in vec2 v_tex_coord;

                uniform float height;
                uniform float radius;
                uniform bool use_texture;
                uniform sampler2D texture_matrix;

                out vec4 f_color;

                void main() {
                    if (use_texture) {
                        float n = 100;
                        float z = height*(v_tex_coord[1] - 0.5);
                        float k = floor( (n/2) * ( 1- ( z / sqrt(pow(radius, 2)  + pow(z, 2)) )) );
                        float v = k / (n-1);

                        vec4 texFrag = texture(texture_matrix, vec2(v_tex_coord[0], v));
                        f_color.rgb = texFrag.r * v_color.rgb;
                        f_color.a = v_color.a;
                    } else {
                        f_color.rgb = v_color.rgb;
                        f_color.a = v_color.a;
                    }
                }
            '''
        else:  # standard texture mapping
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