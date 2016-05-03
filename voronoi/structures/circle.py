from ..geom.geometry import point as p
from math import sqrt, pi, sin, cos, fabs


class InvalidCircle(Exception):

    def __init__(self, sites):
        self.sites = sites

    def __str__(self):
        return repr([str(site) for site in self.sites])

class CircleAboveSweepline(Exception):

    def __init__(self, sweepline):
        self.sites = sites
        self.sweep = sweepline.y

    def __str__(self):
        return repr([str(site) for site in self.sites] + " " +\
            "c.low: {} scanline.y: {}".format(self.y, self.sweep))

class CircleAlreadyCreated(Exception):

    def __init__(self, circle):
        self.sites = circle.csites()

    def __str__(self):
        return repr(self.sites)


class Circle:
    '''
    given three sites, construct a circle to be used as a circle event
    '''
    created_circles = []
    sites = []

    # should probably be a class method
    # def already_created(self):
    #     if set(self.csites()) in self.created_circles:
    #         raise CircleAlreadyCreated(self)
    #         return True
    #     else:
    #         self.created_circles.append(set(self.csites()))
    #         return False

    # def equals(self, circle):
    #     uncommon_sites = set(
    #         self.csites()).symmetric_difference(circle.csites())
    #     if len(uncommon_sites) > 0:
    #         return False
    #     else:
    #         return True

    # def _is_empty(self):
    #     included = []
    #     # check to make sure the circle is empty
    #     for site in Circle.sites:
    #         if site not in self.csites():
    #             square_dist = (self.c.x - site.x) ** 2 + \
    #                 (self.c.y - site.y) ** 2
    #             if square_dist <= self.r ** 2:
    #                 included.append(str(site))
    #     if len(included) > 0:
    #         raise NotEmptyCircle(self.csites(), included)
    #     else:
    #         # this is a valid circle
    #         return True

    def _get_center(self):
        '''returns the center of the circle, if it exists'''
        self.smoothness = 60
        s1 = self.s1
        s2 = self.s2
        s3 = self.s3

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
        return [self.s1, self.s2, self.s3]

    def set_eqn(self):
        '''given three points, set the radius, lowest point, & center of the circle'''
        center = self._get_center()
        self.c = center
        self.r = sqrt((self.s1.x - self.c.x)**2 + (self.s1.y - self.c.y)**2)
        self.low = p(self.c.x, self.c.y - self.r, 0.0)


    def above_sweepline(self, sweepline):
        if (self.low.y > sweepline):
            raise CircleAboveSweepline(self, sweepline)
            return True
        else:
            return False

    def __init__(self, arc, directrix):
        self.arc = arc
        arc.circle = self
        self.s1 = arc.prev.site
        self.s2 = arc.site
        self.s3 = arc.next.site
        self.set_eqn()
        self.above_sweepline(directrix)
        if self.low is not None:
            self.y = self.low.y


    def __str__(self):
        return "cx:{}, cy:{}, clow:{}".format(
            self.c.x, self.c.y, self.csites(), self.low)

    def circleData(self):
        buf = []
        radius = self.r
        sides = self.smoothness
        for side in range(0, sides):
            ang = float(side) * 2.0 * pi / sides
            x = cos(ang) * radius + self.c.x
            y = sin(ang) * radius + self.c.y
            buf.append([x, y])
        return buf

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
