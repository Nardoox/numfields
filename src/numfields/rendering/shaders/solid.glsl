#version 330 core

#ifdef VERTEX_SHADER
in vec3 in_position;
in vec3 in_normal;

uniform mat4 u_model;
uniform mat4 u_view;
uniform mat4 u_proj;

out vec3 v_normal;
out vec3 v_world_pos;

void main() {
    vec4 world = u_model * vec4(in_position, 1.0);
    v_world_pos = world.xyz;
    v_normal = mat3(u_model) * in_normal;
    gl_Position = u_proj * u_view * world;
}
#endif

#ifdef FRAGMENT_SHADER
in vec3 v_normal;
in vec3 v_world_pos;

uniform vec3 u_tint;
uniform float u_alpha;
uniform int u_selected;
uniform int u_translating;
uniform vec3 u_light_dir;
uniform int u_body_id;

layout(location = 0) out vec4 f_color;
layout(location = 1) out int f_picking;

void main() {
    vec3 n = normalize(v_normal);
    vec3 l = normalize(u_light_dir);
    vec3 v = normalize(-v_world_pos);
    float diff = max(dot(n, l), 0.0);
    float spec = pow(max(dot(reflect(-l, n), v), 0.0), 32.0);
    vec3 base = u_tint * (0.25 + 0.65 * diff) + vec3(0.15) * spec;
    if (u_selected != 0) {
        base += u_tint * 0.35;
    }
    if (u_translating != 0) {
        base += vec3(0.18);
    }
    f_color = vec4(base, u_alpha);
    f_picking = u_body_id;
}
#endif
