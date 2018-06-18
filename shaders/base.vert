#version 330

////////////////
// input
////////////////

in vec2 vert_pos;

////////////////
// output
////////////////

out vec2 frag_pos;

void main() {
    // assign output
    frag_pos = vert_pos;

    // assign gl_Position
    gl_Position = vec4(vert_pos, 0.0, 1.0);
}