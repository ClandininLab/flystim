#version 330

in vec2 pos;
out vec2 vert_pos;

void main() {
    vert_pos = pos;
    gl_Position = vec4(pos, 0.0, 1.0);
}