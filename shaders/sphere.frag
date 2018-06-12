#version 330

in vec2 screen_coord;

uniform vec3 h_vec;
uniform vec3 v_vec;
uniform vec3 o_vec;

void assign_color(float r, float theta, float phi);

void main() {
    vec3 pos = h_vec*screen_coord.x + v_vec*screen_coord.y + o_vec;

    float r = length(pos);
    float theta = acos(pos.z / r);
    float phi = atan(pos.y, pos.x);

    assign_color(r, theta, phi);
}
