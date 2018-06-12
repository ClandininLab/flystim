#version 330

// inputs
in vec2 vert_pos;
in float vert_color;
in float min_cos_phi;
in float max_cos_phi;

// uniforms
uniform vec2 screen_vector;
uniform vec3 screen_offset;
uniform float screen_height;

// output
out vec4 frag_color;

void main() {
    // compute 3D position on screen
    vec3 pos = screen_offset + vert_pos.xxy*vec3(screen_vector, screen_height);

    // compute distance to screen
    float r = length(pos);

    // color the fragment if it is in the specified range of latitudes
    if ((r*min_cos_phi <= pos.z) && (pos.z <= r*max_cos_phi)){
        frag_color = vec4(vert_color, vert_color, vert_color, 1.0);
    } else {
        discard;
    }
}
