#version 330

////////////////
// input
////////////////

in vec2 vert_pos;
in vec3 vert_col;

////////////////
// output
////////////////

out vec3 pixel_pos;

void main() {
    // pass along (interpolated) vertex color to the fragment shader as the 3D pixel coordinates
    pixel_pos = vert_col;

    // assign gl_Position
    gl_Position = vec4(vert_pos, 0.0, 1.0);
}