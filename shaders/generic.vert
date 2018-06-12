#version 330

in vec2 pos;
in float color;

out float vert_color;

void main() {
    gl_Position = vec4(pos, 0.0, 1.0);
    vert_color = color;
}