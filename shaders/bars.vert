#version 330

// vertex inputs
in vec3 pos;

// instance inputs
in float bar_color;
in float bar_phi_min;
in float bar_phi_max;
in float bar_theta_min;
in float bar_theta_max;

// uniforms
uniform float screen_phi_min;
uniform float screen_phi_width;
uniform float screen_theta_min;
uniform float screen_theta_width;

// outputs
out float vert_color;

void main() {
    // compute angular coordinates of vertex (in radians)
    vec2 pos_angular = vec2(mix(bar_theta_min, bar_theta_max, pos.x) + pos.z,
                            mix(bar_phi_min, bar_phi_max, pos.y));

    // compute 2D position in NDC space
    vec2 pos_ndc = vec2(2.0*(pos_angular.x - screen_theta_min)/screen_theta_width - 1.0,
                        2.0*(pos_angular.y - screen_phi_min)/screen_phi_width - 1.0);

    // assign gl_Position
    gl_Position = vec4(pos_ndc, 0.0, 1.0);

    // assign output color
    vert_color = bar_color;
}