from math import fabs, sqrt, isinf
from ..geom.constants import EPSILON
from .rbtree.rbtree import Node
from .circle import Circle, InvalidCircle, CircleAboveSweepline

import logging
import logging.config
logging.config.fileConfig('logging.conf')
logger = logging.getLogger('beach')

RED = "RED"
BLACK = "BLACK"

class BeachNode(Node):
    next_id = 0

    def __init__(self, site, color=RED, left=None, right=None, parent=None, next=None, prev=None):
        self.site = site
        self.edge = None
        self.circle = None 

        self.color = color
        self.left = left
        self.right = right
        self.parent = parent

        self.next = next
        self.prev = prev
        self._bkpt = float('-inf')

        self.id = BeachNode.next_id
        BeachNode.next_id += 1

    @property
    def bkpt(self):
        return self._bkpt

    @bkpt.setter
    def bkpt(self, directrix):
        self._bkpt = self.left_bkpt(directrix)

    def left_bkpt(self, directrix):
        ''' returns the leftmost intersection of two parabolic arcs, assumes site is left of self '''
        if not self.site:
            return float('-inf')

        arc_x = self.site.x
        arc_y = self.site.y
        drx = directrix
        arc_drx = arc_y - drx

        #case where the distance between this arc's focus and the y-coord of directrix is zero
        if arc_drx ==  0:
            return arc_x

        #case where this is the leftmost arc, so there is no site to the left
        prev_site = self.prev.site
        if not prev_site:
            return float('-inf')

        larc_x = prev_site.x
        larc_y = prev_site.y
        larc_drx = larc_y - drx

        #case where the distance between left arc's focus and the y-coord of directrix is zero
        if larc_drx == 0:
            return larc_x

        #define some other things to make the eqn less cumbersome
        foc_dist = larc_x - arc_x
        # print(arc_drx, larc_drx)
        aby2 = 1.0 / arc_drx - 1.0 / larc_drx
        b = foc_dist / larc_drx 
        # print(aby2, arc_x)
        if aby2 != 0:
            bkpt = (-b - sqrt(b * b - 2.0 * aby2 * (foc_dist * foc_dist / (-2.0 * larc_drx) - larc_y + larc_drx / 2.0 + arc_y - arc_drx / 2.0))) / aby2 + arc_x;
        else:
            bkpt = (arc_x + larc_x)/2.0

        return bkpt

    def right_bkpt(self, directrix):
        '''
        right_bkpt takes an instance of a beach node and a directrix and returns the right breakpoint of the parabolic segment. if there is no beachfront to the left, then it returns infinity as the right breakpoint
        '''
        next_beach = self.next
        if next_beach != None:
            return next_beach.left_bkpt(directrix)
        else:
            if self.site and self.site.y == directrix:
                return self.site.x
            else:
                return float('inf')

    # @bkpt.setter
    # def bkpt(self, event_loc):
    #     if self.site and self.prev:
    #         if not self.prev.site and self.prev.parent:
    #             print("hmmm")
    #             self._bkpt = self.site.left_bkpt(self.prev.parent.site, event_loc)
    #         else:
    #             self._bkpt = self.site.left_bkpt(self.prev.site, event_loc)
    #     elif self.site:
    #         self._bkpt = self.site.left_bkpt(None, event_loc)
    #     # return self._bkpt   

    @property
    def x(self):
        if self.site:
            return self.site.x
        else:
            return float('-inf')


    def arceqn(self, x, y_pos):
        arc_x = self.site.x
        arc_y = self.site.y
        drx = y_pos
        y = (1.0 / (2.0 * (arc_y - drx))) * (((x - arc_x) * (x - arc_x)) + (arc_y * arc_y - drx * drx))

        return y

    def inv_arceqn(self, y_pos):
        y = 1.0
        arc_x = self.site.x
        arc_y = self.site.y
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


    def __repr__(self):
        if self.site:
            return "\n\t(beach: {}; id:{}; color:{}; bkpt: {}; \n\t\t left: ({}); \n\t\t right: ({}); \n\t\t prev: ({}, {}); \n\t\tnext: ({}, {});\n\t\tcircle: {} edge: {})\n".format(self.site, self.id, self.color, self._bkpt, self.left.site, self.right.site, self.prev.site, self.prev.id, self.next.site, self.next.id, self.circle, self.edge)
            # return "\n\t(beach: {}; color:{}; bkpt: {}; \n\t\t left: ({}); \n\t\t right: ({}); \n\t\t prev: ({}); \n\t\tnext: ({});)\n".format(self.site, self.color, self._bkpt, self.left, self.right, self.prev.site, self.next.site)
        else:
            return "\n\t (beach: NIL node)"

    def __sub__(self, other):
        return self.bkpt - other

    def __add__(self, other):
        return self.bkpt + other

        
    def __lt__(self, other):
        if isinstance(other, float):
            if self.bkpt < other:
                return True

        elif isinstance(other, BeachNode):
            if self.bkpt < other.bkpt:
                return True

        # elif isinstance(other, Circle):
        #     if self.site:
        #         if self.site.y < circle.y 
            
        #     else:
        #         print("BeachNode __lt__::you should raise an exception")
        return False

    def __gt__(self, other):
        if isinstance(other, float):
            if self.bkpt > other:
                return True

        elif isinstance(other, BeachNode):
            if self.bkpt > other.bkpt:
                return True
        
        return False

    def __eq__(self, other):
        if self.site is None and other is None:
            return True

        elif isinstance(other, float):
            if fabs(self.bkpt - other) < EPSILON:
                return True

        elif isinstance(other, BeachNode):
            if fabs(self.bkpt - other.bkpt) < EPSILON:
                return True

        return False

