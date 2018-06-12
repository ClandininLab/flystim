#version 330

in float vert_color;

out vec4 frag_color;

void main() {
    frag_color = vec4(vert_color, vert_color, vert_color, 1.0);
}