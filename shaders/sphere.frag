#version 330

#define M_PI 3.14159265359

// inputs
in vec2 vert_pos;
in float vert_color;

// screen uniforms
uniform vec2 screen_vector;
uniform vec3 screen_offset;
uniform float screen_height;

// stimulus uniforms
uniform sampler2D Texture;

// output
out vec4 frag_color;

void main() {
    // compute screen position in cartesian coordinates
    vec3 pos_cart = screen_offset + vert_pos.xxy*vec3(screen_vector, 0.5*screen_height);

    // compute screen position in spherical coordinates
    float r = length(pos_cart);
    float phi = acos(pos_cart.z / r);
    float theta = atan(pos_cart.y, pos_cart.x);

    // compute monochromatic fragment color
    float color = texture(Texture, vec2(theta/(2.0*M_PI), phi/(M_PI))).r;

    // assign output color
    frag_color = vec4(color, color, color, 1.0);
}
