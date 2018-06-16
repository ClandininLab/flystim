#version 330

#define M_PI 3.14159265359

in vec2 vert_pos;

// uniforms
uniform vec2 screen_vector;
uniform vec3 screen_offset;
uniform float screen_height;

uniform float screen_phi_min;
uniform float screen_phi_width;
uniform float screen_theta_min;
uniform float screen_theta_width;

uniform sampler2D Texture;

// output
out vec4 frag_color;

void main() {
    // compute 3D position on screen
    vec3 pos = screen_offset + vert_pos.xxy*vec3(screen_vector, 0.5*screen_height);

    // compute spherical coordinates of this position
    float r = length(pos);
    float phi = acos(pos.z / r);
    float theta = atan(pos.y, pos.x);

    // adjust theta component if necessary
    if (theta < screen_theta_min) {
        theta += 2.0 * M_PI;
    }

    // compute the texture coordinate
    vec2 text_coord = vec2((theta - screen_theta_min)/screen_theta_width,
                           (phi - screen_phi_min)/(screen_phi_width));

    // set the color
    frag_color = vec4(texture(Texture, text_coord).rrr, 1.0);
}
