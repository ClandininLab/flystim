#version 330

// vertex inputs
in vec2 pos;

// instance inputs
in float color;
in float min_phi;
in float max_phi;
in float min_theta;
in float max_theta;

// uniforms
uniform vec2 screen_vector;
uniform vec3 screen_offset;

// outputs
out vec2 vert_pos;
out float vert_color;
out float min_cos_phi;
out float max_cos_phi;

void main() {
    // compute x coordinate of vertex
    float theta = mix(min_theta, max_theta, pos.x);
    float tan_theta = tan(theta);
    float x_coord = (+tan_theta*screen_offset.x-screen_offset.y) / (-tan_theta*screen_vector.x+screen_vector.y);

    // assign gl_Position
    vert_pos = vec2(x_coord, pos.y);
    gl_Position = vec4(vert_pos, 0.0, 1.0);

    // pass on color to fragment shader
    vert_color = color;

    // compute range of cos(phi) values
    // note that cos(phi) is decreasing on [0, pi]
    min_cos_phi = cos(max_phi);
    max_cos_phi = cos(min_phi);
}