#version 120

attribute vec3 a_position;
attribute vec3 a_color;
varying vec3 fragColor;

void main() {
  gl_Position = gl_ProjectionMatrix*gl_ModelViewMatrix*vec4(a_position, 1.0);
  gl_PointSize = 10.0;
  fragColor = a_color;
}
