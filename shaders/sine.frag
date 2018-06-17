#version 330

// inputs
in vec2 vert_pos;
in float vert_color;

// stimulus uniforms
uniform float a_coeff;
uniform float b_coeff;
uniform float c_coeff;
uniform float d_coeff;

// screen uniforms
uniform vec2 screen_vector;
uniform vec3 screen_offset;
uniform float screen_height;

// outputs
out vec4 frag_color;

void main() {
    // compute screen position in cartesian coordinates
    vec3 pos_cart = screen_offset + vert_pos.xxy*vec3(screen_vector, 0.5*screen_height);

    // compute screen position in spherical coordinates
    float r = length(pos_cart);
    float phi = acos(pos_cart.z / r);
    float theta = atan(pos_cart.y, pos_cart.x);

    // compute monochromatic fragment color
    float color = a_coeff * sin(b_coeff * (theta - c_coeff)) + d_coeff;

    // assign output color
    frag_color = vec4(color, color, color, 1.0);
}