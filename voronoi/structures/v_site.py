from math import fabs


class Site:

    def __init__(self, point, color):
        self.p = point
        self.c = color
        self.x = point.x
        self.y = point.y

    def dist_to_scanline(self, scanline):
        self.dist2scan = fabs(self.y - scanline.y)

    def update(self, scanline):
        self.dist_to_scanline(scanline)

    def toBuffer(self):
        point = self.p.components()
        color = self.c.components()
        return point, color

    def __str__(self):
        return "site x:{} y:{}".format(self.x, self.y)
