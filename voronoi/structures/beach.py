from math import fabs, sqrt, isinf
from .circle import Circle, InvalidCircle, NotEmptyCircle, CircleAlreadyCreated, CircleAboveSweepline

import logging
import logging.config
logging.config.fileConfig('logging.conf')
logger = logging.getLogger('beach')


class Beach:
    # default bounds if we're using the opengl simulation
    bounds = {"xmin": -1.0, "xmax": 1.0, "ymin": -1.0, "ymax": 1.0}

    def __init__(self, site, scanline):
        self.directrix = scanline
        self.focus = site

    def intersect(self, beach):
        a = self.focus.x
        b = self.focus.y
        c = self.directrix.y

        # calculate intersection of two parabolas
        h = beach.focus.x
        j = beach.focus.y

        try:
            x1 = ((-1.0) * (sqrt((-b * c + b * j + c * c - c * j) * (a * a - 2.0 * a * h +
                  b * b - 2 * b * j + h * h + j * j))) + a * c - a * j + b * h - c * h) / (b - j)
        except:
            x1 = min(a, h)
        try:
            x2 = ((sqrt((-b * c + b * j + c * c - c * j) * (a * a - 2.0 * a * h + b *
                  b - 2.0 * b * j + h * h + j * j))) + a * c - a * j + b * h - c * h) / (b - j)
        except:
            if x1 < a:
                x2 = max(a, h)
            else:
                x2 = min(a, h)

        if x1 > x2:
            return [x2, x1]
        else:
            return [x1, x2]

    def arceqn(self, x):
        a = self.focus.x
        b = self.focus.y
        c = self.directrix.y
        y = (1.0 / (2.0 * (b - c))) * (((x - a) * (x - a)) + (b * b - c * c))

        return y

    def inv_arceqn(self):
        y = self.bounds["ymax"]
        a = self.focus.x
        b = self.focus.y
        c = self.directrix.y
        try:
            x1 = a + sqrt(-1.0 * (b - c) * (b + c - 2.0 * y))
            x2 = a - sqrt(-1.0 * (b - c) * (b + c - 2.0 * y))
            if x1 > x2:
                return x2, x1
            else:
                return x1, x2
        except:
            return a, a

    def update(self, bl, br):
        DRAW_EPSILON = .002
        INC = 3 * DRAW_EPSILON
        arcBuf = []
        cBuf = []
        c = self.focus.c

        if isinf(br):
            tmp, br = self.inv_arceqn()

        if isinf(bl):
            bl, tmp = self.inv_arceqn()

        if self.focus.y >= self.directrix.y:
            i = bl - DRAW_EPSILON
            while i <= br + DRAW_EPSILON:
                try:
                    y = self.arceqn(i)
                    cBuf.extend(c.components())
                    arcBuf.extend([i, y, 0.0])
                except:
                    pass
                i += INC
        return arcBuf, cBuf

    def toBuffer(self, bl, br):
        return self.update(bl, br)


class BeachNode:

    def __init__(self, beach, left=None, right=None, breakl=None, breakr=None):
        self.beach = beach
        self.circles = []
        self.x = beach.focus.x
        self.y = beach.focus.y
        self.breakl = breakl
        self.breakr = breakr
        self.next = right
        self.prev = left


# *** Beachfront ***
class BeachODBLL:

    def __init__(self, head=None, tail=None):
        self.head = head
        self.tail = tail
        self.beachBuf = []
        self.colorBuf = []

    def printDBL(self):
        ptr = self.head
        ptr_str = ""
        while ptr is not None:
            ptr_str += "\n\tptr: {} ptr.x: {} ptr.breakl: {} ptr.breakr: {} ".format(
                ptr, ptr.x, ptr.breakl, ptr.breakr)
            ptr = ptr.next
        logger.debug("\nPRINT BEACHFRONT: {}".format(ptr_str))

    def validateDBLL(self):
        ptr = self.head
        validate_str = ""
        validate_str += "\n******STARTING: VALIDATE BEACHFRONT******"
        while ptr is not None:
            if ptr.prev is not None and ptr.prev.next is ptr:
                validate_str += "\n\tptr.prev.next is ptr for {}".format(ptr)
            else:
                if ptr.prev is None and ptr is self.head:
                    validate_str += "\n\thead for ptr{}".format(ptr)
                else:
                    validate_str += "\n\tptr.prev.next is NOT ptr for {}".format(
                        ptr)
                    validate_str += "\n\tptr.prev.next is {}".format(
                        ptr.prev.next)

            if ptr.next is not None and ptr.next.prev is ptr:
                validate_str += "\n\tptr.next.prev is ptr for {}".format(ptr)
            else:
                if ptr.next is None and ptr is self.tail:
                    validate_str += "\n\ttail for ptr{}".format(ptr)
                    # to do: make sure this is self.tail
                else:
                    validate_str += "\n\tptr.next.prev is NOT ptr for {}".format(
                        ptr)
                    validate_str += "\n\tptr.next.prev is {}".format(
                        ptr.next.prev)
            ptr = ptr.next

        self.printDBL()
        validate_str += "\n******FINISHED: VALIDATE BEACHFRONT******\n"
        logger.debug(validate_str)

    def removeCircles(self, bn):
        '''given a beach node, remove all circle events associated with that node'''
        # note: the arc that disappears must be the oldest one
        bad_circles = []
        for circle in bn.circles:
            if bn.next is not None:
                try:
                    bn.next.circles.remove(circle)
                    bad_circles.append(circle)
                except:
                    pass
                if bn.next.next is not None:
                    try:
                        bn.next.next.circles.remove(circle)
                        bad_circles.append(circle)
                    except:
                        pass
            if bn.prev is not None:
                try:
                    bn.prev.circles.remove(circle)
                    bad_circles.append(circle)
                except:
                    pass
                if bn.prev.prev is not None:
                    try:
                        bn.prev.prev.circles.remove(circle)
                        bad_circles.append(circle)
                    except:
                        pass
        return bad_circles

    def addCircle(self, n1, n2, n3):
        circle_events = []
        asap_circles = []
        scanline = n1.beach.directrix
        try:
            circle = Circle(n1.beach.focus, n2.beach.focus, n3.beach.focus, scanline)
            circle.update(scanline)
            circ_str = "\nADD CIRCLE"
            # make sure the circle's lowest point is below the scanline (i.e, where we just added the site)
            # note that this isnt quite correct (e.g think abt case where we
            # removed arc & are recomputing)
            circ_str += "\n\t adding a circle @cx {}, cy {}, low {}, dist2scan {})".format(
                circle.c.x, circle.c.y, circle.low.y, circle.dist2scan)
            circ_str += "\n\t circle.sites(): :{}".format(
                str([str(site) for site in circle.csites()]))
            logger.debug(circ_str)
            if circle.asap:
                asap_circles.append(circle)
            else:
                n1.circles.append(circle)
                n2.circles.append(circle)
                n3.circles.append(circle)
                circle_events.append(circle)
        except InvalidCircle as IC:
            logger.error("CIRCLE ERROR: Not a valid circle {}".format(str(IC)))
        except NotEmptyCircle as NEC:
            logger.error(
                "CIRCLE ERROR: Not an empty circle sites included {}".format(
                    str(NEC)))
        except CircleAlreadyCreated as CAC:
            logger.error(
                "CIRCLE ERROR: Circle already created {}".format(str(CAC)))

        return circle_events, asap_circles

    # TO DO: insert does not account for degenerate case where the new site
    # is inserted exactly at the intersection of the sites to the right and
    # left
    def insert(self, beach):
        # print("inserting")
        circle_events = []
        bad_circles = []
        asap_circles = []
        bn = BeachNode(beach)
        self.validateDBLL()
        insert_str = "\nINSERT SITE"
        insert_str += "\n\tinserting site @(x{}, y{}) bn{}".format(
            beach.focus.x, beach.focus.y, bn)

        # list is empty, insert the beach node
        if self.head is None:
            self.head = self.tail = bn
            bn.breakl = - float('inf')
            bn.breakr = float('inf')
            insert_str += "\n\tthis is the first and only node {}, bl = {}, br={} and  new site {}".format(
                bn.x, bn.breakl, bn.breakr, bn.x)
            logger.debug(insert_str)
            return asap_circles, circle_events, bad_circles

        # list is not empty, insert the beach node
        else:
            ptr = self.head
            while ptr is not None:
                # site is to the right of the left breakpoint and left of right
                # breakpoint
                if (ptr.breakl <= bn.x):
                    if (ptr.next is not None and (ptr.next.breakl > bn.x) or isinf(ptr.breakr)):
                        insert_str += "\n\tthis is the node {}, bl = {}, br={} and  new site {}".format(
                            ptr.x, ptr.breakl, ptr.breakr, bn.x)
                        bn.breakl, bn.breakr = ptr.beach.intersect(bn.beach)

                        # make a new node
                        rbn = BeachNode(ptr.beach, bn, ptr.next,
                                        bn.breakr, ptr.breakr)

                        # update links / set tail based on whether or not it's
                        # the last node
                        if ptr.next:
                            rbn.next.prev = rbn
                        else:
                            self.tail = rbn

                        bn.next = rbn
                        bn.prev = ptr
                        ptr.next = bn

                        ptr.breakr = bn.breakl
                        bn.breakr = bn.next.breakl

                        # *** REMOVE Circle Events ***
                        bad_circles = self.removeCircles(ptr)
                        # *** ADD Circle Events ***
                        # 2 sites to the left
                        if bn.prev and bn.prev.prev:
                            cetmp, asaptmp = self.addCircle(bn.prev.prev, bn.prev, bn)
                            circle_events.extend(cetmp)
                            asap_circles.extend(asaptmp)

                        # (we don't need to handle sites to left and right for bn since bn.prev and bn.next are the same arc)

                        # two sites to the right of bn
                        if bn.next and bn.next.next:
                            cetmp, asaptmp = self.addCircle(bn, bn.next, bn.next.next)
                            circle_events.extend(cetmp)
                            asap_circles.extend(asaptmp)

                        # sites to the left and right of rbn and, if possible,
                        # two sites to the right of rbn
                        if rbn.next:
                            cetmp, asaptmp = self.addCircle(rbn.prev, rbn, rbn.next)
                            circle_events.extend(cetmp)
                            asap_circles.extend(asaptmp)
                            if rbn.next.next:
                                cetmp, asaptmp = self.addCircle(
                                    rbn, rbn.next, rbn.next.next)
                                circle_events.extend(cetmp)
                                asap_circles.extend(asaptmp)

                        logger.debug(insert_str)
                        self.validateDBLL()
                        return list(set(asap_circles)), list(set(circle_events)), list(set(bad_circles))

                if ptr.next is not None:
                    ptr = ptr.next
                else:
                    print("uh oh")

    def remove(self, ptr):
        logger.debug(
            "\nREMOVE ARC: \n\tremoving arc bn{} @(x{} y{}) with bl {} br {}".format(
                ptr, ptr.x, ptr.y, ptr.breakl, ptr.breakr))
        self.printDBL()
        circle_events = []
        bad_circles = []
        asap_circles = []
        cur = self.head
        while cur is not None:
            if cur is ptr:
                # remove circle events associated with this node
                bad_circles = self.removeCircles(cur)
                # special case where we remove the first node, we know it's not
                # the only node
                if cur is self.head:
                    self.head = cur.next
                    cur.next.prev = None
                    # update circle events
                    if cur.next and cur.next.next and cur.next.next.next:
                        cetmp, asaptmp = self.addCircle(
                            cur.next, cur.next.next, cur.next.next.next)
                        circle_events.extend(cetmp)
                        asap_circles.extend(asaptmp)
                    self.validateDBLL()
                    return asap_circles, circle_events, bad_circles
                else:
                    cur.prev.next = cur.next
                    if cur.next is not None:
                        cur.next.prev = cur.prev
                        if cur.next.next is not None:
                            cetmp, asaptmp = self.addCircle(
                                cur.prev, cur.next, cur.next.next)
                            circle_events.extend(cetmp)
                            asap_circles.extend(asaptmp)
                        if cur.prev.prev is not None:
                            cetmp, asaptmp = self.addCircle(
                                cur.prev.prev, cur.prev, cur.next)
                            circle_events.extend(cetmp)
                            asap_circles.extend(asaptmp)

                        self.validateDBLL()
                        return asap_circles, circle_events, bad_circles
                    else:
                        self.tail = cur.prev
                        return asap_circles, circle_events, bad_circles
            cur = cur.next

    def update(self, ptr):
        if ptr is not None:
            # update right breakpoint of ptr and left bkpt of ptr.next
            if ptr.next is not None:
                bkpts = ptr.beach.intersect(ptr.next.beach)
                if ptr.y > ptr.next.y:
                    bpt = min(bkpts)
                    if bpt is not ptr.x:
                        ptr.breakr = bpt
                        ptr.next.breakl = bpt
                else:
                    bpt = max(bkpts)
                    if bpt is not ptr.x:
                        ptr.breakr = bpt
                        ptr.next.breakl = bpt

                if (ptr.breakr < ptr.breakl):
                    if (ptr.breakl > ptr.beach.bounds["xmin"]) and (
                            ptr.breakr > ptr.beach.bounds["xmin"]):
                        logger.error(
                            "\nUPDATE ERROR: \n\tURGENT: should remove: bn {} ptr.x {} bl:{} br:{}".format(
                                ptr, ptr.x, ptr.breakl, ptr.breakr))
                    else:
                        logger.warning(
                            "\nUPDATE WARNING: \n\tOUT OF BOUNDS: should remove: bn {} ptr.x {} bl:{} br:{}".format(
                                ptr, ptr.x, ptr.breakl, ptr.breakr))
                    self.printDBL()
                self.update(ptr.next)
            else:
                return

    def find_by_x(self, circle):
        ''' given a circle and a beachfront, return the arc directly above circle.low'''
        cur = self.head
        #don't we *always* remove the arc associated w/ the 2nd site?
        while cur is not None:
            if circle.low.x >= cur.breakl and circle.low.x <= cur.breakr:
                if fabs(
                    fabs(
                        circle.low.x) -
                    fabs(
                        cur.breakl)) > .0025 and fabs(
                    fabs(
                        circle.low.x) -
                    fabs(
                        cur.breakr)) > .0025:
                    return cur
                else:
                    arcs = {}
                    dist = fabs(cur.breakl - cur.breakr)
                    arcs[dist] = cur
                    if cur.prev and cur.prev.x != cur.prev.breakl and cur.prev.x != cur.prev.breakr:
                        dist = fabs(cur.prev.breakl - cur.prev.breakr)
                        arcs[dist] = cur.prev
                    if cur.next and cur.next.x != cur.next.breakl and cur.next.x != cur.next.breakr:
                        dist = fabs(cur.next.breakl - cur.next.breakr)
                        arcs[dist] = cur.next

                    mindist = min(arcs.keys())
                    return arcs[mindist]
            else:
                cur = cur.next

        # while cur is not None:
        #     if circle.low.x >= cur.breakl and circle.low.x <= cur.breakr:
        #         if fabs(
        #             fabs(
        #                 circle.low.x) -
        #             fabs(
        #                 cur.breakl)) > .005 and fabs(
        #             fabs(
        #                 circle.low.x) -
        #             fabs(
        #                 cur.breakr)) > .005:
        #             return cur
        #         else:
        #             arcs = {}
        #             dist = fabs(cur.breakl - cur.breakr)
        #             arcs[dist] = cur
        #             if cur.prev and cur.prev.x != cur.prev.breakl and cur.prev.x != cur.prev.breakr:
        #                 dist = fabs(cur.prev.breakl - cur.prev.breakr)
        #                 arcs[dist] = cur.prev
        #             if cur.next and cur.next.x != cur.next.breakl and cur.next.x != cur.next.breakr:
        #                 dist = fabs(cur.next.breakl - cur.next.breakr)
        #                 arcs[dist] = cur.next

        #             mindist = min(arcs.keys())
        #             return arcs[mindist]
        #     else:
        #         cur = cur.next

    def getHead(self):
        return self.head

    def toBuffer(self):
        self.update(self.head)

        self.beachBuf = []
        self.colorBuf = []
        ptr = self.head
        while ptr is not None:
            b, c = ptr.beach.toBuffer(ptr.breakl, ptr.breakr)
            self.beachBuf.extend(b)
            self.colorBuf.extend(c)
            ptr = ptr.next
        return self.beachBuf, self.colorBuf
