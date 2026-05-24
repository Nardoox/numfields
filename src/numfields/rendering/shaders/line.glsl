#version 330 core

#ifdef VERTEX_SHADER
in vec3 in_position;

uniform mat4 u_model;
uniform mat4 u_view;
uniform mat4 u_proj;

void main() {
    gl_Position = u_proj * u_view * u_model * vec4(in_position, 1.0);
}
#endif

#ifdef FRAGMENT_SHADER
uniform vec3 u_tint;
uniform int u_selected;

layout(location = 0) out vec4 f_color;
layout(location = 1) out int f_picking;

void main() {
    vec3 c = u_tint;
    if (u_selected != 0) {
        c += u_tint * 0.4;
    }
    f_color = vec4(c, 1.0);
    f_picking = 0;
}
#endif
