#version 120
varying vec3 fragColor;

void main() {

  float d2 = distance(gl_PointCoord.xy, vec2(.5,.5));

  if (d2 >= .5){
    discard;
  }else{
    gl_FragColor = vec4(fragColor, 1.0);
  }
  gl_FragColor = vec4(fragColor, 1.0);
}