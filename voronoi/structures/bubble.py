from ..geom.geometry import point as p
from math import sqrt, pi, sin, cos, fabs

class InvalidCircle(Exception):

    def __init__(self, sites):
        self.sites = sites

    def __str__(self):
        return repr([str(site) for site in self.sites])

class Bubble:
    '''
    rising bubble to merge delaunay candidates
    '''

    def includes(self, vertex):
        '''
        given a vertex, return true is the vertex lies inside the circle
        '''
        #if the distance between the vertex and the center of the circle
        #is less than its radius, return false
        d2 = (self.c.x - vertex.position.x)**2 + (self.c.y - vertex.position.y)**2
        return True if d2 < self.r**2 else False

    def _get_center(self):
        '''returns the center of the circle, if it exists'''
        self.smoothness = 60
        s1 = self.v1.position
        s2 = self.v2.position
        s3 = self.v3.position

        try:
            m12 = (s1.y - s2.y) / (s1.x - s2.x)
            m23 = (s2.y - s3.y) / (s2.x - s3.x)
            cx = (m12 * m23 * (s3.y - s1.y) + m12 * (s2.x + s3.x) -
                  m23 * (s1.x + s2.x)) / (2.0 * (m12 - m23))
            cy = (-1.0 / m12) * (cx - (s1.x + s2.x) / 2.0) + \
                (s1.y + s2.y) / 2.0
            return p(cx, cy, 0.0)
        except:
            raise InvalidCircle(self.csites())

    def csites(self):
        return [self.v1, self.v2, self.v3]

    def set_eqn(self):
        '''given three points, set the radius, lowest point, & center of the circle'''
        center = self._get_center()
        s1 = self.v1.position
        self.c = center
        self.r = sqrt((s1.x - self.c.x)**2 + (s1.y - self.c.y)**2)

    def __init__(self, v1, v2, v3):
        self.v1 = v1
        self.v2 = v2
        self.v3 = v3
        self.set_eqn()


    def __str__(self):
        return "cx:{}, cy:{}, csites:{}".format(
            self.c.x, self.c.y, self.csites())

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
