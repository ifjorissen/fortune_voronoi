from geometry import point, vector
from scanline import Scanline
from v_site import Site
from beach import Beach, BeachODBLL
import math
from circle import Circle
from delaunay import Delaunay
from dcel import VoronoiDCEL

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

  def __init__(self, view=True):
    self.view = view
    self.scanning = False
    self.sites = []
    self.event_pq = []
    self.site_buffer = []
    self.color_buffer = []
    self.beaches = []
    self.beachline = BeachODBLL()
    self.circles = []
    self.vvertices = []
    self.handled_circles = []
    self.delaunay = Delaunay(self)
    self.edgeDCEL = VoronoiDCEL()
    self.bounds = {"xmin": -1.0, "xmax": 1.0, "ymin": -1.0, "ymax": 1.0}
    self.createScanline()

  def read(self, filename):
    #a site file contains one site per line, x, y coordinates
    print("\n----**** voronoi read ****----")
    print("reading sites from file...")
    site_xmin = None
    site_ymin = None
    site_xmax = None
    site_ymax = None

    site_file = open(filename, 'r')
    for line in site_file:
      coords = line.split()
      x = float(coords[0])
      y = float(coords[1])
      print("adding a site located at x: {}, y: {}".format(x, y))
      p = point(x, y, 0.0)
      #to do: raise an error if this site already exists
      self.addSite(p)

      #update the bounds
      if site_xmin is None or x < site_xmin:
        site_xmin = x

      if site_xmax is None or x > site_xmax:
        site_xmax = x

      if site_ymin is None or y < site_ymin:
        site_ymin = y
        
      if site_ymax is None or y > site_ymax:
        site_ymax = y

    self.bounds = {"xmin": site_xmin, "xmax": site_xmax, "ymin": site_ymin, "ymax": site_ymax}
    print("Bounds: xmin: {} xmax: {} ymin: {} ymax: {}".format(site_xmin, site_xmax, site_ymin, site_ymax))
    Beach.bounds = self.bounds
    self.createScanline()
    print("\n----**** done with voronoi read ****----")


  def outputVoronoi(self):
    ''' prints the results of the voronoi diagram '''
    print("\n----**** output voronoi ****----")
    print("There are {} sites, {} vertices, {} edges".format(len(self.sites), len(self.vvertices), len(self.edgeDCEL.edges.items())/2.0))
    self.edgeDCEL.printVertices()
    self.edgeDCEL.printEdges()
    print("\n----**** done with output voronoi ****----")


  def precompute(self):
    '''
        precomputes the voronoi & delaunay digrams without visualization
        instead of doing it on-the-fly as is currently implemented
        could lead to functions such as showBeach(scanline), 
        showCircle(circle) etc, where the events are all precomputed & precise
    '''
    print("\n----**** voronoi precompute ****----")
    # self.event_pq.sort(key=lambda site: site.dist2scan, reverse=True)
    #can't we just order by y coordinate?
    self.event_pq.sort(key=lambda site: site.y, reverse=False)
    for site in self.sites:
      site.update(self.scanline) 

    for circle in self.circles:
      circle.update(self.scanline)

    while (len(self.event_pq) > 0):
      #take the latest event
      event = self.event_pq.pop()
      # self.scanline.y = event.y

      #process the event
      # self.processEvent()
      self.scanline.y = event.y
      self.beachline.update(self.beachline.getHead())
      if type(event) is Site:
        print("\nsite event @{}".format(event.y))
        site = event
        # self.scanline.y = site.y
        beach = Beach(site, self.scanline)
        circle_events = self.beachline.insert(beach)
        self.beaches.append(beach)
        if circle_events:
          print([str(c) for c in circle_events])
          self.circles.extend(circle_events)
          self.event_pq.extend(circle_events)

      else: 
        circle = event
        # self.scanline.y = circle.low.y
        print("\ncircle event @(cx{}, cy{}), sy{}".format(circle.c.x, circle.c.y, self.scanline.y))
        arc = self.beachline.find_by_x(circle)
        self.vvertices.append(circle.c)
        self.delaunay.add_face(circle)
        self.edgeDCEL.handleCircle(circle)

        bad_circles = arc.circles
        new_circles = self.beachline.remove(arc)
        if new_circles:
          for c in new_circles:
            if not c.equals(circle):
              self.circles.append(c)
              self.event_pq.append(c)
        for c in bad_circles:
          try:
            for i in range(0, self.event_pq.count(c)):
              self.event_pq.remove(c)
          except:
            if not c.equals(circle):
              print("could not remove c:{} cx:{}".format(c, c.c))
            else:
              print("Weird, bro: circle  c:{} cx:{}".format(c, c.c))
              # pass
        self.handled_circles.append(circle)
        #update all the new sites
      self.event_pq.sort(key=lambda site: site.y, reverse=False)
    self.edgeDCEL.finish()

    print("\n----**** done with voronoi precompute ****----")

  # def edgesToBuffer(self):
  #   #show the edges as they are being traced out
  #   pass

  def edgesToBuffer(self):
    #reveal the computed diagram
    edges, cBuf = self.edgeDCEL.edgesToBuffer()
    return edges, cBuf

  def createScanline(self):
    e1 = point(self.bounds["xmin"], self.bounds["ymax"], 0.0)
    e2 = point(self.bounds["xmax"], self.bounds["ymax"], 0.0)
    self.scanline = Scanline(e1, e2)
    print(self.scanline.e1)
    print(self.scanline.e2)

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

  def addSite(self, p, c=vector(1.0, 1.0, 0.0)):
    if self.view:
      self.site_buffer.extend(p.components())
      self.color_buffer.extend(c.components())
    site = Site(p, c)
    site.update(self.scanline)

    self.sites.append(site)
    self.event_pq.append(site)
    Circle.sites = self.sites
    Delaunay.vertices = self.sites

  def validateEdges(self):
    return self.edgeDCEL.validateCells()

  def scanFinished(self):
    if self.scanline.y < (-1.0-self.scanline.dy):
      return True
    else:
      return False

  def processEvent(self):
    while len(self.event_pq)>0 and (self.event_pq[-1].dist2scan <= math.fabs(self.scanline.dy/2)):
      print("processing an event")
      print([site.dist2scan for site in self.event_pq])
      event = self.event_pq.pop()
      self.scanline.y = event.y
      self.beachline.update(self.beachline.getHead())
      if type(event) is Site:
        #To Do: circle events get removed from sites
        print("\nsite event @{}".format(self.scanline.y))
        site = event
        beach = Beach(site, self.scanline)
        circle_events = self.beachline.insert(beach)
        self.beaches.append(beach)
        if circle_events:
          print([str(c) for c in circle_events])
          self.circles.extend(circle_events)
          self.event_pq.extend(circle_events)

      else: 
        circle = event
        print("\ncircle event @(cx{}, cy{}), sy{}".format(circle.c.x, circle.c.y, self.scanline.y))
        arc = self.beachline.find_by_x(circle)
        self.vvertices.append(circle.c)
        self.delaunay.add_face(circle)
        self.edgeDCEL.handleCircle(circle)

        bad_circles = arc.circles
        new_circles = self.beachline.remove(arc)
        if new_circles:
          for c in new_circles:
            if not c.equals(circle):
              self.circles.append(c)
              self.event_pq.append(c)
        for c in bad_circles:
          try:
            for i in range(0, self.event_pq.count(c)):
              self.event_pq.remove(c)
          except:
            if not c.equals(circle):
              print("could not remove c:{} cx:{}".format(c, c.c))
              print("circle  c:{} cx:{}".format(c, c.c))
            pass
        self.handled_circles.append(circle)
      self.event_pq.sort(key=lambda site: site.y, reverse=False)


  def update(self):
    if not self.scanFinished():
      self.scanline.update()
      for site in self.sites:
        site.update(self.scanline) 

      for circle in self.circles:
        circle.update(self.scanline)

      self.event_pq.sort(key=lambda site: site.y, reverse=False)
      # if len(self.event_pq)>0 and (self.event_pq[-1].dist2scan <= math.fabs(self.scanline.dy/2)):
      #   self.processEvent()
      if len(self.event_pq) == 0:
        self.scanline.y = -1.0
        self.edgeDCEL.finish()

      elif self.event_pq[-1].dist2scan <= math.fabs(self.scanline.dy/2):
        self.processEvent()

