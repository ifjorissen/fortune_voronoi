from itertools import chain
from ..geom.geometry import point as p
from ..geom.geometry import vector as v


class Scanline:

    def __init__(self, e1=p(-1.0, 1.0, 0.0), e2=p(1.0, 1.0, 0.0),
                 vec=v(0.0, -.0005, 0.0), color=v(1.0, 1.0, 1.0)):
        self.y = e1.y
        self.dy = vec.dy
        self.dx = vec
        self.e1 = e1
        self.e2 = e2
        self.vec = vec
        self.c = color

    def update(self):
        self.e1 = self.e1.plus(self.vec)
        self.e2 = self.e2.plus(self.vec)
        self.y = self.e1.y

    def scanData(self):
        DRAW_EPSILON = .025
        INC = DRAW_EPSILON
        scan_points = []
        x = self.e1.x
        while x <= self.e2.x:
            y = self.y
            scan_points.append([x, y])
            x += INC
        return scan_points

    def toBuffer(self):
        line = list(chain.from_iterable(
            [self.e1.components(), self.e2.components()]))
        color = list(chain.from_iterable(
            [self.c.components(), self.c.components()]))
        return line, color
