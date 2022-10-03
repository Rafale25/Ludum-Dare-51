#version 330

uniform sampler2D u_texture;

void main(void){
   	// vec2 p = (gl_FragCoord.xy * 2.0 - resolution) / min(resolution.x, resolution.y);
	vec4 color = texture(u_texture, gl_FragCoord.xy);

	gl_FragColor = color;
}