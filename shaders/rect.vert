#version 330

// vertex inputs
in vec2 pos;

// instance inputs
in float color;
in float x_min;
in float x_max;
in float y_min;
in float y_max;

// outputs
out vec2 vert_pos;
out float vert_color;

void main() {
    // assign vertex position in NDC space
    vert_pos = vec2(mix(x_min, x_max, pos.x),
                    mix(y_min, y_max, pos.y));

    // assign vertex color (mono)
    vert_color = color;

    // assign gl_Position
    gl_Position = vec4(vert_pos, 0.0, 1.0);
}