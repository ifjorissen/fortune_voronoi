#version 120
// precision highp float;
// precision highp int;

attribute vec3 a_position;
attribute vec3 a_color;

// uniform vec3 u_velocity;
varying vec3 fragColor;

void main() {
  // gl_Position = vec4(a_position+u_velocity), 1.0);
  gl_Position = vec4(a_position, 1.0);
  // gl_PointSize = 10.0;
  fragColor = a_color;
}
