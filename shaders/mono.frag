#version 330

// inputs
in vec2 vert_pos;
in float vert_color;

// outputs
out vec4 frag_color;

void main() {
    frag_color = vec4(vert_color, vert_color, vert_color, 1.0);
}