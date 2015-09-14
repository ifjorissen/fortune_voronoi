#version 120

// precision highp float;
// precision highp int;

varying vec3 fragColor;
void main() {
  gl_FragColor = vec4(fragColor, 1.0);
}