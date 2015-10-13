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
from delaunay import Delaunay
import numpy as np

colors = [
  vector(0.0, .4, 0.9), #blue
  vector(1.0, .5, 0.0), #orange
  vector(1.0, .85, 0.0), #yellow
  vector(.4, .2, .55), #purple
  vector(0, 0.6, .7), #teal
  vector(0.72, 0.32, 0) #dark orange
]
#visibility keys
showCircles = True
showDelaunay = True
showBeachfront = True

#voronoi buffers
site_buffer = None 
site_color_buffer = None   #
beachfront_buffer = None
beachfront_color_buffer = None
vvertex_buffer = None
vvertex_color_buffer = None
vedge_buffer = None
vedge_color_buffer = None

#event buffers
circle_buffer = None
circle_color_buffer = None
scanline_buffer = None
scanline_color_buffer = None

#delaunay buffers
del_edge_buffer = None
del_edge_color_buffer = None

line_shaders = None
pt_shaders = None
# ctl_pts = []
# ctl_pts_color = []
# scan = False

xStart = 0
yStart = 0
width = 1024  
height = 1024
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
       circle_buffer, circle_color_buffer, \
       vvertex_buffer, vvertex_color_buffer, \
       del_edge_buffer, del_edge_color_buffer, \
       vedge_buffer, vedge_color_buffer,\
       pt_shaders, line_shaders

  # Clear the rendering information.
  glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

  # Clear the transformation stack.
  glMatrixMode(GL_MODELVIEW)
  glLoadIdentity()
  glPushMatrix()

  # * * * * * * * * * * * * * * * *
  # Draw the beachfront
  shs = line_shaders
  glUseProgram(shs)
  glEnable(GL_LINE_SMOOTH)
  if V.beachfrontSegments() and showBeachfront:
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

  # * * * * * * * * * * * * * * * *
  # Draw the circles
  if V.circleSegments() and showCircles:
    glLineWidth(3)
    colorAL = glGetAttribLocation(shs,'a_color')
    posAL = glGetAttribLocation(shs,'a_position')

    # # all the vertex positions
    glBindBuffer(GL_ARRAY_BUFFER, circle_buffer)
    glVertexAttribPointer(posAL, 3, GL_FLOAT, GL_FALSE, 0, None)
    glEnableVertexAttribArray(posAL)

    # # all the vertex colors
    glBindBuffer(GL_ARRAY_BUFFER, circle_color_buffer)
    glVertexAttribPointer(colorAL, 3, GL_FLOAT, GL_FALSE, 0, None)
    glEnableVertexAttribArray(colorAL)
    for i in range(0, len(V.circles)):
      glDrawArrays(GL_LINE_LOOP, V.circles[0].smoothness*i, V.circles[0].smoothness)
    glDisableVertexAttribArray(posAL)
    glDisableVertexAttribArray(colorAL)
  glDisable(GL_LINE_SMOOTH)

  # * * * * * * * * * * * * * * * *
  # Draw all the voronoi ctl sites.
  if V.sites:
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
  glEnable(GL_LINE_SMOOTH)
  if V.scanning and showBeachfront and not V.scanFinished():
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
  glDisable(GL_LINE_SMOOTH)

  # * * * * * * * * * * * * * * * *
  # Draw delaunay edges
  if D.face and showDelaunay:
    shs = line_shaders
    glUseProgram(shs)
    glLineWidth(3)
    colorAL = glGetAttribLocation(shs,'a_color')
    posAL = glGetAttribLocation(shs,'a_position')

    # all the vertex positions
    glEnableVertexAttribArray(posAL)
    glBindBuffer(GL_ARRAY_BUFFER, del_edge_buffer)
    glVertexAttribPointer(posAL, 3, GL_FLOAT, GL_FALSE, 0, None)

    # all the vertex colors
    glEnableVertexAttribArray(colorAL)
    glBindBuffer(GL_ARRAY_BUFFER, del_edge_color_buffer)
    glVertexAttribPointer(colorAL, 3, GL_FLOAT, GL_FALSE, 0, None)

    for i in range(0, len(D.face)):
      glDrawArrays(GL_LINE_LOOP, 3*i, 3)
    # glDrawArrays(GL_TRIANGLES, 0, len(D.face)*2)
    glDisableVertexAttribArray(posAL)
    glDisableVertexAttribArray(colorAL)

  # * * * * * * * * * * * * * * * *
  # Draw voronoi edges
  if V.scanFinished():
    V.outputVoronoi()
    shs = line_shaders
    glUseProgram(shs)
    glLineWidth(3)
    colorAL = glGetAttribLocation(shs,'a_color')
    posAL = glGetAttribLocation(shs,'a_position')

    # all the vertex positions
    glEnableVertexAttribArray(posAL)
    glBindBuffer(GL_ARRAY_BUFFER, vedge_buffer)
    glVertexAttribPointer(posAL, 3, GL_FLOAT, GL_FALSE, 0, None)

    # all the vertex colors
    glEnableVertexAttribArray(colorAL)
    glBindBuffer(GL_ARRAY_BUFFER, vedge_color_buffer)
    glVertexAttribPointer(colorAL, 3, GL_FLOAT, GL_FALSE, 0, None)

    glDrawArrays(GL_LINES, 0, len(V.edgeDCEL.edges)*2)
    glDisableVertexAttribArray(posAL)
    glDisableVertexAttribArray(colorAL)

  # * * * * * * * * * * * * * * * *
  # Draw voronoi vertices
  if V.vvertices:
    shs = pt_shaders
    glUseProgram(shs)
    colorAL = glGetAttribLocation(shs,'a_color')
    posAL = glGetAttribLocation(shs,'a_position')

    # all the vertex positions
    glEnable(GL_POINT_SPRITE)
    glEnable(GL_VERTEX_PROGRAM_POINT_SIZE)
    glEnableVertexAttribArray(posAL)
    glBindBuffer(GL_ARRAY_BUFFER, vvertex_buffer)
    glVertexAttribPointer(posAL, 3, GL_FLOAT, GL_FALSE, 0, None)

    # all the vertex colors
    glEnableVertexAttribArray(colorAL)
    glBindBuffer(GL_ARRAY_BUFFER, vvertex_color_buffer)
    glVertexAttribPointer(colorAL, 3, GL_FLOAT, GL_FALSE, 0, None)

    glDrawArrays(GL_POINTS, 0, len(V.vvertices))
    glDisable(GL_POINT_SPRITE);
    glDisable(GL_VERTEX_PROGRAM_POINT_SIZE)
    glDisableVertexAttribArray(posAL)
    glDisableVertexAttribArray(colorAL)

  glPopMatrix()

  # Render the scene.
  glFlush()
  glutSwapBuffers()

def keypress(key, x, y):
  """ Handle a "normal" keypress. """
  global V, control, showCircles, showDelaunay, showBeachfront

  # Handle ESC key.
  if key == b'\033':  
  # "\033" is the Escape key
    sys.exit(1)

  # Handle SPACE key.
  if key == b' ': 
    V.scanning = not V.scanning
    tick(0)

  #hide circles
  if key == b'c':
    showCircles = not showCircles
    glutPostRedisplay()

  if key == b'd':
    showDelaunay = not showDelaunay
    glutPostRedisplay()

  if key == b'b':
    showBeachfront = not showBeachfront
    glutPostRedisplay()


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


def screenToWorldCoords(mousex, mousey):
  xnew = 2.0 * (mousex - width/2) / min(width,height)
  ynew = 2.0 * (height/2 - mousey) / min(width,height)
  ctw = [xnew, ynew, 0.0, 0.0]

  return point(ctw[0], ctw[1], ctw[2])

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


def update_circle_buffers():
  global circle_buffer, circle_color_buffer
  circle_array, color_array = V.circlesToBuffer()

  circle_buffer = glGenBuffers(1)
  glBindBuffer(GL_ARRAY_BUFFER, circle_buffer)
  glBufferData(GL_ARRAY_BUFFER,  len(circle_array)*4,
    (c_float*len(circle_array))(*circle_array), GL_STATIC_DRAW)

  circle_color_buffer = glGenBuffers(1)
  glBindBuffer(GL_ARRAY_BUFFER, circle_color_buffer)
  glBufferData(GL_ARRAY_BUFFER, len(color_array)*4,
    (c_float*len(color_array))(*color_array), GL_STATIC_DRAW)


def update_vvertex_buffers():
  global vvertex_buffer, vvertex_color_buffer
  vvertex_array, color_array = V.vverticesToBuffer()

  vvertex_buffer = glGenBuffers(1)
  glBindBuffer(GL_ARRAY_BUFFER, vvertex_buffer)
  glBufferData(GL_ARRAY_BUFFER, len(vvertex_array)*4,
    (c_float*len(vvertex_array))(*vvertex_array), GL_STATIC_DRAW)

  vvertex_color_buffer = glGenBuffers(1)
  glBindBuffer(GL_ARRAY_BUFFER, vvertex_color_buffer)
  glBufferData(GL_ARRAY_BUFFER, len(color_array)*4,
    (c_float*len(color_array))(*color_array), GL_STATIC_DRAW)

def update_delaunay_buffers():
  global del_edge_buffer, del_edge_color_buffer
  edge_array, color_array = D.toBuffer()

  del_edge_buffer = glGenBuffers(1)
  glBindBuffer(GL_ARRAY_BUFFER, del_edge_buffer)
  glBufferData(GL_ARRAY_BUFFER, len(edge_array)*4,
    (c_float*len(edge_array))(*edge_array), GL_STATIC_DRAW)

  del_edge_color_buffer = glGenBuffers(1)
  glBindBuffer(GL_ARRAY_BUFFER, del_edge_color_buffer)
  glBufferData(GL_ARRAY_BUFFER, len(color_array)*4,
    (c_float*len(color_array))(*color_array), GL_STATIC_DRAW)

def update_vedge_buffers():
  global vedge_buffer, vedge_color_buffer
  vedge_array, color_array = V.edgesToBuffer()

  vedge_buffer = glGenBuffers(1)
  glBindBuffer(GL_ARRAY_BUFFER, vedge_buffer)
  glBufferData(GL_ARRAY_BUFFER, len(vedge_array)*4,
    (c_float*len(vedge_array))(*vedge_array), GL_STATIC_DRAW)

  vedge_color_buffer = glGenBuffers(1)
  glBindBuffer(GL_ARRAY_BUFFER, vedge_color_buffer)
  glBufferData(GL_ARRAY_BUFFER, len(color_array)*4,
    (c_float*len(color_array))(*color_array), GL_STATIC_DRAW)


def tick(val):
  global V
  if V.scanning and not V.scanFinished():
    if val:
      val = not val
      V.update()
      update_scanline_buffers()
      update_beachline_buffers()
      update_circle_buffers()
      update_vvertex_buffers()
      update_delaunay_buffers()
      glutPostRedisplay()
      glutTimerFunc(8, tick, val)
    else:
      val = not val
      V.update()
      glutTimerFunc(8, tick, val)

  elif V.scanFinished():
    # V.update()
    V.scanning = False
    update_vedge_buffers()
    # glutTimerFunc(10, tick, 0)
    glutPostRedisplay()

  else:
    V.scanning = False
    # update_beachline_buffers()
    glutTimerFunc(10, tick, 0)



def init():
  global V, D
  V = Voronoi(view=True)
  D = V.delaunay
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
  print('\'b\' to hide the beachfront')
  print('\'c\' to hide circle events')
  print('\'d\' to hide delaunay triangulation')
  print('Press ESC to quit.')
  print()

  glutMainLoop()
  return 0


if __name__ == "__main__": main()
