#version 330

// input vertex: one of (-1, -1), (-1, 1), (1, 1), or (-1, 1)
in vec2 in_vert;

// output vertex: one of (0, 0), (0, 1), (1, 1), (0, 1)
// the fragment shader will receive an interpolated version
out vec2 screen_coord;

void main() {
    gl_Position = vec4(in_vert, 0.0, 1.0);
    screen_coord = 0.5*(in_vert + vec2(1.0, 1.0));
}