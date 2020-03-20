#version 330

#if defined VERTEX_SHADER

in vec2 in_position;
in int gid;
out int out_gid;

void main() {
    gl_Position = vec4(in_position, 0., 1.0);
    out_gid = gid;
}

    #elif defined GEOMETRY_SHADER

layout (points) in;
layout (triangle_strip, max_vertices = 4) out;

in int out_gid[1];

//uniform float size;

out vec2 uv;
flat out int gid;

void main() {
    gid = out_gid[0];

    vec2 in_position = gl_in[0].gl_Position.xy;
    vec2 pos = in_position;

    vec2 right = vec2(1.0, 0.0);// * size;
    vec2 up = vec2(0.0, 1.0);// * size;

    uv = vec2(1.0, 1.0);
    gl_Position = vec4(pos + (right + up), 0.0, 1.0);
    EmitVertex();

    uv = vec2(0.0, 1.0);
    gl_Position = vec4(pos + (-right + up), 0.0, 1.0);
    EmitVertex();

    uv = vec2(1.0, 0.0);
    gl_Position = vec4(pos + (right - up), 0.0, 1.0);
    EmitVertex();

    uv = vec2(0.0, 0.0);
    gl_Position = vec4(pos + (-right - up), 0.0, 1.0);
    EmitVertex();

    EndPrimitive();
}

    #elif defined FRAGMENT_SHADER

out vec4 fragColor;
in vec2 uv;
flat in int gid;

uniform sampler2DArray texture0;

void main() {
    fragColor = texture(texture0, vec3(uv, gid));

}
    #endif