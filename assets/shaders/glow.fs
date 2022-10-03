#version 330

uniform bool flip;
uniform bool blend;

uniform sampler2D tex;
uniform sampler2D tex2;
uniform float weight[5] = float[] (0.227027, 0.1945946, 0.1216216, 0.054054, 0.016216);

in vec2 uv;
out vec4 color;

void main() {
    vec2 size = textureSize(tex, 0);
    vec2 pix_size = 1 / size;
    vec2 shift;
    if (flip) {
        shift = vec2(0, pix_size.y);
    } else {
        shift = vec2(pix_size.x, 0);
    }
    vec4 col = texture(tex, uv) * weight[0];
    for (int i=1;i<5;i++) {
        col += texture(tex, uv+shift*i) * weight[i];
        col += texture(tex, uv-shift*i) * weight[i];
    }
    if (blend) {
        col += texture(tex2, uv);
    }    
    color = col;
}