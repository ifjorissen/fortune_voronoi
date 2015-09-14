#
# view.py
#
# Author: Jim Fix
# MATH 385, Reed College, Spring 2015
#
# This is the starting point for Homework 5 where you
# are asked to implememt C. Loop's subdivision scheme.
# It relies on the separate file 'we.py' which implements
# object, face, edge, and vertex classes.  These 
# constitute a triangular mesh that describe an object.
#
# In the code below, that object/mesh is constructed from
# an Alias/Wavefront .OBJ file and displayed in an OpenGL
# window.  It can then be 'refined' by pressing the '/'
# key.  The effect should be to build a new mesh, one 
# where each triangular face of the 'input mesh' is 
# split into four triangles, and where the placement of
# their vertices is a weighted average of vertices on
# and around the split face.  The resulting 'output
# mesh' object replaces pre-refined input mesh, and 
# becomes what's displayed by the code below.
#
# The refinement happens in the 'slash key handler'
# code under the procedure 'keypress'.
#
# Your assignment is to modify the 'refine' method code 
# at the bottom of 'we.py', under the definition of 
# the 'object' class, so that it performs Loop's
# splitting and averaging and returns that new, refined
# mesh.
#
# To run the code:
#    python3 object-view.py objs/stell.obj
#
# There are several interesting low-resolution meshes found
# in the 'objs' folder.
#

import sys
from geometry import point, vector, EPSILON, ORIGIN
from quat import quat
# from we import vertex, edge, face, object
from random import random
from math import sin, cos, acos, asin, pi, sqrt
from ctypes import *
import random

from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLUT.freeglut import *
from voronoi import Voronoi
import numpy as np

colors = [
  vector(0.3451, 1.0, 0.5450),
  vector(1.0, 0.4313, 0.3411),
  vector(1.0, 0.8862, 0.3725),
  vector(1.0, 1.0, 0.0),
  vector(0.0, 1.0, 1.0),
  vector(1.0, 0.0, 1.0),
  vector(0.3804, 0.7647, 1.0)
]
site_buffer = None  # The VBOs
site_color_buffer = None   #
scanline_buffer = None
scanline_color_buffer = None
beachfront_buffer = None
beachfront_color_buffer = None

line_shaders = None
pt_shaders = None
# ctl_pts = []
# ctl_pts_color = []
# scan = False

xStart = 0
yStart = 0
width = 512
height = 512
scale = 1.0/min(width,height)
V = None
# ticks = 0

def init_shaders(vs_name,fs_name):
  """Compile the vertex and fragment shaders from source."""

  vertex_shader = glCreateShader(GL_VERTEX_SHADER)
  glShaderSource(vertex_shader,open(vs_name,'r').read())
  glCompileShader(vertex_shader)
  result = glGetShaderiv(vertex_shader, GL_COMPILE_STATUS)
  if result:
    print('Vertex shader compilation successful.')
  else:
    print('Vertex shader compilation FAILED:')
    print(glGetShaderInfoLog(vertex_shader))
    sys.exit(-1)

  fragment_shader = glCreateShader(GL_FRAGMENT_SHADER)
  glShaderSource(fragment_shader, open(fs_name,'r').read())
  glCompileShader(fragment_shader)
  result = glGetShaderiv(fragment_shader, GL_COMPILE_STATUS)
  if result:
    print('Fragment shader compilation successful.')
  else:
    print('Fragment shader compilation FAILED:')
    print(glGetShaderInfoLog(fragment_shader))
    sys.exit(-1)

  shs = glCreateProgram()
  glAttachShader(shs,vertex_shader)
  glAttachShader(shs,fragment_shader)
  glLinkProgram(shs)

  return shs


def draw():
  """ Issue GL calls to draw the scene. """
  global site_buffer, site_color_buffer, \
       scanline_buffer, scanline_color_buffer, \
       beachfront_buffer, beachfront_color_buffer, \
       pt_shaders, line_shaders

  # Clear the rendering information.
  glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

  # Clear the transformation stack.
  glMatrixMode(GL_MODELVIEW)
  glLoadIdentity()
  glPushMatrix()

  # * * * * * * * * * * * * * * * *
  # Draw all the voronoi ctl sites.
  if V.sites:
    # print(V.sites)
    shs = pt_shaders
    glUseProgram(shs)
    colorAL = glGetAttribLocation(shs,'a_color')
    posAL = glGetAttribLocation(shs,'a_position')

    # all the vertex positions
    glEnable(GL_POINT_SPRITE)
    glEnable(GL_VERTEX_PROGRAM_POINT_SIZE)
    glEnableVertexAttribArray(posAL)
    glBindBuffer(GL_ARRAY_BUFFER, site_buffer)
    glVertexAttribPointer(posAL, 3, GL_FLOAT, GL_FALSE, 0, None)

    # all the vertex colors
    glEnableVertexAttribArray(colorAL)
    glBindBuffer(GL_ARRAY_BUFFER, site_color_buffer)
    glVertexAttribPointer(colorAL, 3, GL_FLOAT, GL_FALSE, 0, None)

    glDrawArrays(GL_POINTS, 0, len(V.sites))
    glDisable(GL_POINT_SPRITE);
    glDisable(GL_VERTEX_PROGRAM_POINT_SIZE)
    glDisableVertexAttribArray(posAL)
    glDisableVertexAttribArray(colorAL)

  # * * * * * * * * * * * * * * * *
  # Draw the scanline
  shs = line_shaders
  glUseProgram(shs)
  if V.scanning:
    glLineWidth(5)
    colorAL = glGetAttribLocation(shs,'a_color')
    posAL = glGetAttribLocation(shs,'a_position')

    # # all the vertex positions
    glBindBuffer(GL_ARRAY_BUFFER, scanline_buffer)
    glVertexAttribPointer(posAL, 3, GL_FLOAT, GL_FALSE, 0, None)
    glEnableVertexAttribArray(posAL)

    # # all the vertex colors
    glBindBuffer(GL_ARRAY_BUFFER, scanline_color_buffer)
    glVertexAttribPointer(colorAL, 3, GL_FLOAT, GL_FALSE, 0, None)
    glEnableVertexAttribArray(colorAL)
      
    glDrawArrays(GL_LINES, 0, 2)
    glDisableVertexAttribArray(posAL)
    glDisableVertexAttribArray(colorAL)

  # * * * * * * * * * * * * * * * *
  # Draw the beachfront
  shs = line_shaders
  glUseProgram(shs)
  if V.beachfrontSegments():
    glLineWidth(5)
    colorAL = glGetAttribLocation(shs,'a_color')
    posAL = glGetAttribLocation(shs,'a_position')

    # # all the vertex positions
    glBindBuffer(GL_ARRAY_BUFFER, beachfront_buffer)
    glVertexAttribPointer(posAL, 3, GL_FLOAT, GL_FALSE, 0, None)
    glEnableVertexAttribArray(posAL)

    # # all the vertex colors
    glBindBuffer(GL_ARRAY_BUFFER, beachfront_color_buffer)
    glVertexAttribPointer(colorAL, 3, GL_FLOAT, GL_FALSE, 0, None)
    glEnableVertexAttribArray(colorAL)
    glDrawArrays(GL_LINE_STRIP, 0, V.beachfrontSegments())
    glDisableVertexAttribArray(posAL)
    glDisableVertexAttribArray(colorAL)

  glPopMatrix()

  # Render the scene.
  glFlush()
  glutSwapBuffers()

def keypress(key, x, y):
  """ Handle a "normal" keypress. """
  global V, control

  # Handle ESC key.
  if key == b'\033':  
  # "\033" is the Escape key
    sys.exit(1)

  # Handle SPACE key.
  if key == b' ': 
    V.scanning = not V.scanning
    tick(0)

  # Handle slash key.
  if key == b'm': 
    control = not control
    glutPostRedisplay()

def mouse(button, state, x, y):
  global ctl_pts, ctl_pts_color, site_array, color_array, V
  ctwpt = screenToWorldCoords(x, y)
  if button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:
    color = random.choice(colors)
    V.addSite(ctwpt, color)
  update_site_buffers()
  glutPostRedisplay()



#this function determines whether or not a click event occurs on top of a control point
# def intersectCtrlPt(ctw):
#   for i in range(len(ctl_pts)):
#     diff = ctw.minus(ctl_pts[i])
#     if diff.norm() < ((pointSize*2*radius)/width):
#       return [True, i, diff]
#   return False
  

def screenToWorldCoords(mousex, mousey):
  xnew = 2.0 * (mousex - width/2) / min(width,height)
  ynew = 2.0 * (height/2 - mousey) / min(width,height)
  ctw = [xnew, ynew, 0.0, 0.0]

  return point(ctw[0], ctw[1], ctw[2])

# def mouseDrag(x, y):
#   global ctl_pts
#   ctwpt = screenToWorldCoords(x, y)
#   res = intersectCtrlPt(ctwpt)
#   if res:
#     i = res[1]
#     diff = res[2]
#     ctl_pts[i] = ctl_pts[i].plus(diff)
#     glutPostRedisplay()


def update_site_buffers():
  global site_buffer, site_color_buffer
  site_array, color_array = V.sitesToBuffer()

  site_buffer = glGenBuffers(1)
  glBindBuffer(GL_ARRAY_BUFFER, site_buffer)
  glBufferData(GL_ARRAY_BUFFER,
    (c_float*len(site_array))(*site_array), GL_STATIC_DRAW)

  site_color_buffer = glGenBuffers(1)
  glBindBuffer(GL_ARRAY_BUFFER, site_color_buffer)
  glBufferData(GL_ARRAY_BUFFER,
    (c_float*len(color_array))(*color_array), GL_STATIC_DRAW)

def update_scanline_buffers():
  global scanline_buffer, scanline_color_buffer
  scanline_array, color_array = V.scanline.toBuffer()

  scanline_buffer = glGenBuffers(1)
  glBindBuffer(GL_ARRAY_BUFFER, scanline_buffer)
  glBufferData(GL_ARRAY_BUFFER, len(scanline_array)*4,
    (c_float*len(scanline_array))(*scanline_array), GL_STREAM_DRAW)

  scanline_color_buffer = glGenBuffers(1)
  glBindBuffer(GL_ARRAY_BUFFER, scanline_color_buffer)
  glBufferData(GL_ARRAY_BUFFER, len(color_array)*4,
    (c_float*len(color_array))(*color_array), GL_STATIC_DRAW)

def update_beachline_buffers():
  global beachfront_buffer, beachfront_color_buffer
  beachfront_array, color_array = V.beachline.toBuffer()

  beachfront_buffer = glGenBuffers(1)
  glBindBuffer(GL_ARRAY_BUFFER, beachfront_buffer)
  glBufferData(GL_ARRAY_BUFFER,  len(beachfront_array)*4,
    (c_float*len(beachfront_array))(*beachfront_array), GL_STREAM_DRAW)

  beachfront_color_buffer = glGenBuffers(1)
  glBindBuffer(GL_ARRAY_BUFFER, beachfront_color_buffer)
  glBufferData(GL_ARRAY_BUFFER, len(color_array)*4,
    (c_float*len(color_array))(*color_array), GL_STATIC_DRAW)

def tick(val):
  global V
  if V.scanning:
    V.update()
    update_scanline_buffers()
    update_beachline_buffers()
    glutPostRedisplay()
  glutTimerFunc(50, tick, 0)



def init():
  global V
  V = Voronoi()
  global line_shaders, pt_shaders
  line_shaders = init_shaders('shaders/vert_shader.glsl',
               'shaders/frag_shader.glsl')

  pt_shaders = init_shaders('shaders/vertpt_shader.glsl',
               'shaders/fragpt_shader.glsl')


def resize(w, h):
  """ Register a window resize by changing the viewport.  """
  global width, height, scale, iproj

  glViewport(0, 0, w, h)
  width = w
  height = h

  glMatrixMode(GL_PROJECTION)
  glLoadIdentity()
  r = 1
  if w > h:
      glOrtho(-w/h*r, w/h*r, -r, r, -r, r)
      scale = 2.0 * r / h 
  else:
      glOrtho(-r, r, -h/w * r, h/w * r, -r, r)
      scale = 2.0 * r / w 


def main():
  """ The main procedure, sets up GL and GLUT. """

  # Initialize the GLUT window.
  glutInit([])
  glutInitDisplayMode(GLUT_SINGLE | GLUT_RGB | GLUT_DEPTH)
  glutInitWindowPosition(0, 20)
  glutInitWindowSize(width, height)
  glutCreateWindow( 'view.py - Press ESC to quit' )

  # Initialize the object viewer's state.
  init()

  # Register interaction callbacks.
  glutKeyboardFunc(keypress)
  glutReshapeFunc(resize)
  glutDisplayFunc(draw)
  glutMouseFunc(mouse)
  # glutTimerFunc(100, tick, 0)
  # glutMotionFunc(mouseDrag)
  # glutMotionFunc(motion)

  # Issue some instructions.
  print()
  print('Press SPACE to start the scanline')
  print('Click to add points')
  print('Press ESC to quit.')
  print()

  glutMainLoop()
  return 0


if __name__ == "__main__": main()
