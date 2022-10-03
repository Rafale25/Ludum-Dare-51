#version 330

void main(void){
   	// vec2 p = (gl_FragCoord.xy * 2.0 - resolution) / min(resolution.x, resolution.y);

	gl_FragColor = vec4(gl_FragCoord.xy * 0.001, 0.0, 1.0);
}