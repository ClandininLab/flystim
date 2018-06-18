#version 330

////////////////
// input
////////////////

in vec2 pos;

void main() {
    // assign gl_Position
    gl_Position = vec4(pos, 0.0, 1.0);
}