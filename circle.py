from geometry import point as p
from math import sqrt, pi, sin, cos, acos, fabs, degrees

class InvalidCircle(Exception):
  def __init__(self, sites):
    self.sites = sites

  def __str__(self):
    return repr(self.sites)

class NotEmptyCircle(Exception):
  def __init__(self, sites, included):
    self.sites = sites
    self.included = included

  def __str__(self):
    return repr(self.sites) + " " + repr(self.included)


class Circle:
  '''
  given three sites, construct a circle to be used as a circle event
  '''

  sites = []

  def _is_empty(self):
    # print("_is_empty")
    # print(self.sites)
    included = []
    #check to make sure the circle is empty
    for site in self.sites:
      if site not in self.csites():
        square_dist = (self.c.x - site.x) ** 2 + (self.c.y - site.y) ** 2
        if square_dist <= self.r ** 2:
          included.append(str(site))
    if len(included)>0:
      raise NotEmptyCircle(self.csites(), included)
    else:
      return True

  def _get_center(self):
    '''returns the center of the circle, if it exists'''
    self.smoothness = 60
    s1 = self.s1
    s2 = self.s2
    s3 = self.s3

    try:
      m12 = (s1.y - s2.y)/(s1.x - s2.x)
      m23 = (s2.y - s3.y)/(s2.x - s3.x)
      # print("m12: {} m23: {}".format(m12, m23))
      cx = (m12*m23*(s3.y-s1.y) + m12*(s2.x + s3.x) - m23*(s1.x + s2.x))/(2.0*(m12 - m23))
      cy = (-1.0/m12)*(cx - (s1.x + s2.x)/2.0) + (s1.y + s2.y)/2.0
      return p(cx, cy, 0.0)
    except:
      raise InvalidCircle(self.csites())


    # if cx and cy:
    #   return p(cx, cy, 0.0)
    
    # else:
    #   # print("no circle exists")
    #   raise InvalidCircle([s1, s2, s3])

  def dist_to_scanline(self, scanline):
    self.dist2scan = fabs(self.low.y - scanline.y)


  def update(self, scanline):
    self.dist_to_scanline(scanline)

  def csites(self):
    return [str(self.s1), str(self.s2), str(self.s3)]


  def set_eqn(self):
    '''given three points, set the radius, lowest point, & center of the circle'''
    # try:
    center = self._get_center()
    self.c = center
    self.r = sqrt((self.s1.x - self.c.x )**2 + (self.s1.y - self.c.y)**2)
    self.low = p(self.c.x, self.c.y-self.r, 0.0)
    # print("self.c {} self.r {} self.low {} sites: {} {} {}".format(self.c, self.r, self.low, self.s1.x, self.s2.x, self.s3.x))
    empty = self._is_empty()
    # except InvalidCircle:
    #   raise InvalidCircle(self.csites())

    # except NotEmptyCircle:
    #   raise NotEmptyCircle(self.csites(), included)

    # if center:

  def __init__(self, s1, s2, s3):
    self.s1 = s1
    self.s2 = s2
    self.s3 = s3
    self.set_eqn()

  def toBuffer(self):
    buf = []
    radius = self.r
    sides = self.smoothness
    cbuf = []
    for side in range(0, sides):
      ang = float(side) * 2.0 * pi / sides
      x = cos(ang) * radius + self.c.x
      y = sin(ang) * radius + self.c.y
      buf.extend([x, y, 0.0])
      cbuf.extend([.75, .75, .75])
    return buf, cbuf


