#version 330

in vec2 vert_pos;

// uniforms
uniform vec2 screen_vector;
uniform vec3 screen_offset;
uniform float screen_height;

uniform float a_coeff;
uniform float b_coeff;
uniform float c_coeff;
uniform float d_coeff;

// output
out vec4 frag_color;

void main() {
    // compute 3D position on screen
    vec3 pos = screen_offset + vert_pos.xxy*vec3(screen_vector, screen_height);

    float r = length(pos);
    float phi = acos(pos.z / r);
    float theta = atan(pos.y, pos.x);

    float color = a_coeff * sin(b_coeff * (theta - c_coeff)) + d_coeff;
    frag_color = vec4(color, color, color, 1.0);
}
