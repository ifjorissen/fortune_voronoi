from math import fabs, sqrt, isinf
from ..geom.constants import EPSILON


class Site:
    next_id = 0

    def __init__(self, point, color):
        self.p = point
        self.c = color
        self.x = point.x
        self.y = point.y
        self._dist2scan = float('inf')

        #assign an id
        self.id = Site.next_id
        Site.next_id += 1

    def dist_to_scanline(self, scanline):
        # self._dist2scan = fabs(self.y - scanline.y)
        pass

    def update(self, scanline):
        # self.dist_to_scanline(scanline)
        pass

    def toBuffer(self):
        point = self.p.components()
        color = self.c.components()
        return point, color

    def __hash__(self):
        return self.id

    def __lt__(self, other):
        if self.y > other.y:
            return True
        else:
            return False

    def __gt__(self, other):
        if self.y < other.y:
            return True
        else:
            return False

    def __eq__(self, other):
        if fabs(self.y - other.y) < EPSILON:
            return True
        else:
            return False

    def __cmp__(self, other):
        return cmp(self.y, other.y)

    def __str__(self):
        return "site x:{} y:{}".format(self.x, self.y)

    #take out beach and get necessary arcs from RBtree and/or make this a class method
    def left_bkpt(self, site, y):
        ''' returns the leftmost intersection of two parabolic arcs, assumes site is left of self '''
        arc_x = self.x
        arc_y = self.y
        drx = y
        arc_drx = arc_y - drx

        #case where the distance between this arc's focus and the y-coord of directrix is zero
        if arc_drx ==  0:
            return self.x 

        #case where this is the leftmost arc, so there is no site to the left
        if not site:
            return float('-inf')

        larc_x = site.x
        larc_y = site.y
        larc_drx = larc_y - drx

        #case where the distance between left arc's focus and the y-coord of directrix is zero
        if larc_drx == 0:
            return site.x

        #define some other things to make the eqn less cumbersome
        foc_dist = arc_x - larc_x
        # print(arc_drx, larc_drx)
        aby2 = 1.0 / arc_drx - 1.0 / larc_drx
        b = foc_dist / larc_drx 
        # print(aby2, arc_x)
        if aby2 != 0:
            bkpt =  (-b + sqrt(b * b - 2.0 * aby2 * (foc_dist * foc_dist / (-2.0 * larc_drx) - larc_y + larc_drx / 2.0 + arc_y - arc_drx / 2.0))) / aby2 + arc_x;
        else:
            bkpt = (arc_x + larc_x)/2.0

        return bkpt

    def right_bkpt(self, y_pos, site=None):
        return self.site.left_bkpt(self, site, y_pos)

    def arceqn(self, x, y_pos):
        arc_x = self.x
        arc_y = self.y
        drx = y_pos
        y = (1.0 / (2.0 * (arc_y - drx))) * (((x - arc_x) * (x - arc_x)) + (arc_y * arc_y - drx * drx))

        return y

    def inv_arceqn(self, y_pos):
        y = 1.0
        arc_x = self.x
        arc_y = self.y
        drx = y_pos
        try:
            x1 = arc_x + sqrt(-1.0 * (arc_y - drx) * (arc_y + drx - 2.0 * y))
            x2 = arc_x - sqrt(-1.0 * (arc_y - drx) * (arc_y + drx - 2.0 * y))
            if x1 > x2:
                return x2, x1
            else:
                return x1, x2
        except:
            return arc_x, arc_x
