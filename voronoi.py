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
    self.site_pq = []
    self.site_buffer = []
    self.color_buffer = []
    self.beaches = []
    self.beachline = BeachODBLL()
    self.createScanline()

  def createScanline(self):
    self.scanline = Scanline()

  def sitesToBuffer(self):
    return self.site_buffer, self.color_buffer

  def beachfrontSegments(self):
    return int(len(self.beachline.beachBuf)/3)

  def addSite(self, p, c):
    self.site_buffer.extend(p.components())
    self.color_buffer.extend(c.components())
    site = Site(p, c)
    site.update(self.scanline)

    self.sites.append(site)
    self.site_pq.append(site)

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
    site = self.site_pq.pop()
    beach = Beach(site, self.scanline)
    self.beachline.insert(beach)
    self.beaches.append(beach)

  def update(self):
    if not self.scanFinished():
      self.scanline.update()
      for site in self.sites:
        site.update(self.scanline) 

      self.site_pq.sort(key=lambda site: site.dist2scan, reverse=True)

      if len(self.site_pq)>0 and (self.site_pq[-1].dist2scan <= math.fabs(self.scanline.dy/2)):
        self.processEvent()

