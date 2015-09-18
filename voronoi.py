from geometry import point, vector
from scanline import Scanline
from v_site import Site
from beach import Beach, BeachODBLL
import math

import random
from itertools import chain

class Voronoi:
  colors = [
    vector(0.3451, 1.0, 0.5450),
    vector(1.0, 0.4313, 0.3411),
    vector(1.0, 0.8862, 0.3725),
    vector(1.0, 1.0, 0.0),
    vector(0.0, 1.0, 1.0),
    vector(1.0, 0.0, 1.0),
    vector(0.3804, 0.7647, 1.0)
  ]

  @staticmethod
  def random_color():
    return random.choice(colors)

  def __init__(self):
    self.scanning = False
    self.sites = []
    self.edges = []
    self.event_pq = []
    self.site_buffer = []
    self.color_buffer = []
    self.beaches = []
    self.beachline = BeachODBLL()
    self.circles = []
    self.vvertices = []
    self.createScanline()

  def createScanline(self):
    self.scanline = Scanline()

  def sitesToBuffer(self):
    return self.site_buffer, self.color_buffer

  def beachfrontSegments(self):
    return int(len(self.beachline.beachBuf)/3)

  def circleSegments(self):
    if len(self.circles) > 0:
      return int(len(self.circles)*(self.circles[0].smoothness))
    else:
      return None

  def vverticesToBuffer(self):
    buf = []
    cbuf = []
    for v in self.vvertices:
      buf.extend(v.components())
      cbuf.extend([.9, 0, .2])
    return buf, cbuf

  def circlesToBuffer(self):
    buf = []
    cbuf = []
    for circle in self.circles:
      cb, ccb = circle.toBuffer()
      buf.extend(cb)
      cbuf.extend(ccb)
    return buf, cbuf

  def addSite(self, p, c):
    self.site_buffer.extend(p.components())
    self.color_buffer.extend(c.components())
    site = Site(p, c)
    site.update(self.scanline)

    self.sites.append(site)
    self.event_pq.append(site)

  def scanFinished(self):
    if self.scanline.y < (-1.0-self.scanline.dy):
      return True
    else:
      return False

  # def beachfrontToBuffer(self):
    # arcs = []
    # arc_colors = []
    # for beach in self.beaches
    #   a, c = beach.toBuffer()
    #   arcs.extend(a)
    #   arc_colors.extend(c)
    # return beachline.toBuffer()

  def processEvent(self):
    print("processEvent")
    event = self.event_pq.pop()
    if type(event) is Site:
      #To Do: circle events get removed from sites
      print("site event @{}".format(self.scanline.y))
      site = event
      beach = Beach(site, self.scanline)
      circle_events = self.beachline.insert(beach)
      self.beaches.append(beach)
      if circle_events:
        self.circles.extend(circle_events)
        self.event_pq.extend(circle_events)

    else: 
      circle = event
      print("circle event @{}".format(self.scanline.y))
      arc = self.beachline.find_by_x(circle.low)
      self.vvertices.append(circle.c)
      # print(arc)
      #get all circle events that have this arc in them
      bad_circles = arc.circles
      new_circles = self.beachline.remove(arc)
      if new_circles:
        self.circles.extend(new_circles)
        self.event_pq.extend(new_circles)
      for c in bad_circles:
        try:
          self.event_pq.remove(c)
        except:
          print("could not remove c:{} cx:{}".format(c, c.c))
          pass
        # self.circles.remove(c)


  def update(self):
    if not self.scanFinished():
      self.scanline.update()
      for site in self.sites:
        site.update(self.scanline) 

      for circle in self.circles:
        circle.update(self.scanline)

      self.event_pq.sort(key=lambda site: site.dist2scan, reverse=True)

      if len(self.event_pq)>0 and (self.event_pq[-1].dist2scan <= math.fabs(self.scanline.dy/2)):
        self.processEvent()

