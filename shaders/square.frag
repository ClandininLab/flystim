#version 330

////////////////
// input
////////////////

uniform float color;

////////////////
// output
////////////////

out vec4 out_color;

void main() {
    out_color = vec4(color, color, color, 1.0);
}