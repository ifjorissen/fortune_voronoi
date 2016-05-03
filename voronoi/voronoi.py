#python lib imports
from math import fabs, sqrt, isinf

#logging & logging config imports
import logging
import logging.config
logging.config.fileConfig('logging.conf')
logger = logging.getLogger('voronoi')

#geometry imports
from .geom.geometry import point, vector
from .geom.constants import EPSILON

#misc structures imports
from .structures.circle import Circle, InvalidCircle, CircleAboveSweepline
# from .structures.scanline import Scanline
from .structures.v_site import Site
# from .structures.beach import Beach, BeachODBLL
from .delaunay import Delaunay
from .structures.dcel import VoronoiDCEL
from .structures.rbtree.rbtree import RBTree as Beachfront
from .structures.priority_queue import PriorityQueueSet as EventQueue
from .structures.new_beach import BeachNode

RED = "RED"
BLACK = "BLACK"

class Voronoi:
    def __init__(self, sites, y_pos, view=True, id_prefix=None):
        #pyopengl settings
        self.view = view
        self.site_buffer = []
        self.color_buffer = []
        self.view_bounds = {"xmin": -1.0, "xmax": 1.0, "ymin": -1.0, "ymax": 1.0} 

        #structures & items
        self.circles = []
        self.sites = []
        self.event_pq = EventQueue(key=lambda event: (-1)*event.y)
        self.beachfront = Beachfront(create_node=BeachNode)
        self.vvertices = []
        self.handled_circles = set()
        self.edgeDCEL = VoronoiDCEL()
        self.createScanline()

        #output and dual info
        self.y_pos = y_pos
        self.delaunay = Delaunay(self, id_prefix=id_prefix)
        self.id_prefix = id_prefix

        #initialize sites
        for site in sites:
            self.addSite(site)

    def setBounds(self):
        '''
        given an array of sites, find the boundaries
        '''
        min_y = min(self.sites, key=lambda site: site.y)
        max_y = max(self.sites, key=lambda site: site.y)

        min_x = min(self.sites, key=lambda site: site.x)
        max_x = max(self.sites, key=lambda site: site.x)
        self.bounds = {"xmin": min_x.x, "xmax": max_x.x, "ymin": min_y.y, "ymax": max_y.y}

    def read(self, filename):
        # a site file contains one site per line, x, y coordinates
        read_str = "\n----**** voronoi read ****----"
        site_xmin = None
        site_ymin = None
        site_xmax = None
        site_ymax = None

        site_file = open(filename, 'r')
        for line in site_file:
            coords = line.split()
            x = float(coords[0])
            y = float(coords[1])
            read_str += "\n adding a site located at x: {}, y: {}".format(x, y)
            p = point(x, y, 0.0)
            self.addSite(p)

            # update the bounds
            if site_xmin is None or x < site_xmin:
                site_xmin = x

            if site_xmax is None or x > site_xmax:
                site_xmax = x

            if site_ymin is None or y < site_ymin:
                site_ymin = y

            if site_ymax is None or y > site_ymax:
                site_ymax = y

        self.bounds = {"xmin": site_xmin, "xmax": site_xmax,
                       "ymin": site_ymin, "ymax": site_ymax}
        read_str += "\nDiagram Bounds: xmin: {} xmax: {} ymin: {} ymax: {}".format(
            site_xmin, site_xmax, site_ymin, site_ymax)
        self.startScan()
        read_str += "\n----**** done with voronoi read ****----"
        logger.debug(read_str)
        return read_str

    def rawEdgeData(self):
        return self.edgeDCEL.edgeData()
    
    def rawVertData(self):
        return self.edgeDCEL.vertData()

    def rawSiteData(self):
        site_str = "#site.x site.y\n"
        for site in self.sites:
            site_str += "{} {}\n".format(site.x, site.y)
        return site_str

    def rawCircleData(self):
        circle_str = "#circle.x circle.y radius\n"
        for circle in self.circles:
            data = circle.circleData()
            circle_str += "#circle.x: {} circle.y: {} radius: {}\n".format(circle.c.x, circle.c.y, circle.r)
            for d in data:
                circle_str += "{} {}\n".format(d[0], d[1])
            circle_str += "\n"
        return circle_str

    def rawBeachfrontData(self):
        beachfronts = self.beachfront.beachfrontData()
        beach_str = "#bp1.x bp1.y\n"
        # print(beachfronts)
        print(len(beachfronts))
        for beach in beachfronts:
            beach_str += "\n#beach bl ~{} br~{}\n".format(beach[0], beach[-1])
            for point in beach:
                beach_str += "{} {}\n".format(point[0], point[1])
        return beach_str

    def rawScanlineData(self):
        # scanline_data = self.scanline.scanData()
        # scan_str = "#scan.y scan.y\n"
        # # scan_str += "{} {}\n{} {}\n\n".format(scanline.e1.x, scanline.y, scanline.e2.x, scanline.y)
        # for point in scanline_data:
        #     scan_str += "{} {}\n".format(point[0], point[1])
        # return scan_str
        pass

    def rawDelData(self):
        return self.delaunay.edgeData()

    def outputVoronoi(self):
        ''' writes the results of the voronoi diagram to results/voronoi.txt '''
        if(self.validateDCEL()):
            f = open('results/voronoi.txt', 'w')
            vertices = self.edgeDCEL.printVertices()
            edgeLinks = self.edgeDCEL.printEdgeLinks()
            edgeGeo = self.edgeDCEL.printEdgeGeo()
            cells = self.edgeDCEL.printCells()
            # delaunay = self.delaunay.printEdges()
            f.write("\n----**** voronoi results ****----")
            f.write("\n\tThere are {} sites, {} vertices, {} edges\n".format(len(
                self.sites), len(self.vvertices) + 1, len(self.edgeDCEL.edges.items()) / 2.0))
            f.write(
                "\n\tDiagram Bounds: xmin: {} xmax: {} ymin: {} ymax: {}".format(
                    self.bounds["xmin"],
                    self.bounds["xmax"],
                    self.bounds["ymin"],
                    self.bounds["ymax"]))
            f.write(vertices)
            f.write(edgeLinks)
            f.write(edgeGeo)
            f.write(cells)
            f.write("\n----**** done outputting voronoi results ****----\n")
        else:
            print("...dcel was not valid for some reason... writing raw data anyway")
        fverts = open('results/vertices.dat', 'w')
        fedges = open('results/edges.dat', 'w')
        fsites = open('results/sites.dat', 'w')
        fdel = open('results/del.dat', 'w')
        fdel_ghost = open('results/del_ghost.dat', 'w')
        edges = self.rawEdgeData()
        vertices = self.rawVertData()
        sites = self.rawSiteData()
        del_edges, del_ghost = self.rawDelData()
        fverts.write(vertices)
        fedges.write(edges)
        fsites.write(sites)
        fdel.write(del_edges)
        fdel_ghost.write(del_ghost)
        return self

    def writeState(self):
        '''
        write the current state of the voronoi diagram to the appropriate files
        (beachfront, circle events, sites, vertices, etc)
        '''

        #make files
        # fverts = open('results/vertices_{:.2}.dat'.format(scan_y), 'w')
        # fedges = open('results/edges_{:.2}.dat'.format(scan_y), 'w')
        fsites = open('results/sites_{:.2}.dat'.format(self.y_pos), 'w')
        fbeach = open('results/beach_{:.2}.dat'.format(self.y_pos), 'w')
        fcircle = open('results/circles_{:.2}.dat'.format(self.y_pos), 'w')

        #get data
        # edges = self.rawEdgeData()
        # vertices = self.rawVertData()
        sites = self.rawSiteData()
        circles = self.rawCircleData()
        beachfront = self.rawBeachfrontData()

        # fverts.write(vertices)
        # fedges.write(edges)
        fsites.write(sites)
        fcircle.write(circles)
        fbeach.write(beachfront)

    def edgesToBuffer(self):
        edges, cBuf = self.edgeDCEL.edgesToBuffer()
        return edges, cBuf

    def createScanline(self):
        # e1 = point(self.view_bounds["xmin"], self.view_bounds["ymax"], 0.0)
        # e2 = point(self.view_bounds["xmax"], self.view_bounds["ymax"], 0.0)
        # self.scanline = Scanline(e1, e2)
        pass

    def beachfrontToBuffer(self):
        # beaches, cBuf = self.beachfront.toBuffer()
        # return beaches, cBuf
        pass

    def parabolasToBuffer(self):
        #get the control points for each site
        self.beachfront.print_level_order()
        ctl_pts = []
        directrix = self.y_pos
        self.updateBeachfront(directrix)
        #generate 4 control points for cubic bezier curve (i.e parabolic segment)
        beachfront = self.beachfront.inorder()
        # print("parabolasToBuffer::beachfront: {}".format(beachfront))
        for beach in beachfront:
            p = (beach.site.y - directrix)/2
            left_pos = beach.left_bkpt(directrix)
            # print("initial left_bkpt: {}".format(left_pos))
            if isinf(left_pos):
                # print("leftpos:: is inf!")
                left_pos = beach.inv_arceqn(directrix)[0]

            f_left = beach.arceqn(left_pos, directrix)
            right_pos = beach.next.left_bkpt(directrix)
           
            if isinf(right_pos):
                right_pos = beach.inv_arceqn(directrix)[1]

            f_right = beach.arceqn(right_pos, directrix)
            # print("left_bkpt: {} right_bkpt: {}\n f_left: {} f_right: {}".format(left_pos, right_pos, f_left, f_right))

            b = (-1.0/(2.0*p))*(beach.x)
            a = (1.0/(4.0*p))

            # the two endpoints
            e1 = point(left_pos, f_left, 0)
            e2 = point(right_pos, f_right, 0)

            #the control point for the quadratic curve--> used to generate ctlpts for cubic 
            ctl1 = point((left_pos+right_pos)/2.0, f_left + (2.0*a*left_pos+b)*((right_pos-left_pos)/2.0), 0)

            ctl01x = (2/3.0)*ctl1.x + (1/3.0)*e1.x
            ctl01y = (2/3.0)*ctl1.y + (1/3.0)*e1.y
            ctl01 = point(ctl01x, ctl01y, 0)

            ctl12x = (2/3.0)*ctl1.x + (1/3.0)*e2.x
            ctl12y = (2/3.0)*ctl1.y + (1/3.0)*e2.y
            ctl12 = point(ctl12x, ctl12y, 0)

            ctl_pts.append([e1.components(), ctl01.components(), ctl12.components(), e2.components()])
        return ctl_pts

        # generates 3 control points for quadratic bezier curve (i.e parabola)
        # for site in self.sites:
        #     p = (site.y - directrix)/2
        #     left_pos, right_pos = inv_arceqn(self.y_pos)
        #     b = (-1.0/(2.0*p))*(site.x)
        #     a = (1.0/(4.0*p))
        #     ctl0 = point(left_pos, 1, 0)
        #     ctl1 = point((left_pos+right_pos)/2.0, 1.0 + (2.0*a*left_pos+b)*((right_pos-left_pos)/2.0), 0)
        #     ctl2 = point(right_pos, 1, 0)
        #     ctl_pts.append([ctl0.components(), ctl1.components(), ctl2.components()])
        # return ctl_pts

    def sitesToBuffer(self):
        return self.site_buffer, self.color_buffer

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

    def beachfrontSegments(self):
        return int(len(self.beachfront.beachBuf) / 3)

    def circleSegments(self):
        if len(self.circles) > 0:
            return int(len(self.circles) * (self.circles[0].smoothness))
        else:
            return None

    def addSite(self, p, c=vector(1.0, 1.0, 0.0)):
        if self.view:
            self.site_buffer.extend(p.components())
            self.color_buffer.extend(c.components())
        site = Site(p, c)

        self.sites.append(site)
        self.event_pq.put(site)
        Delaunay.vertices = self.sites

    def validateDCEL(self):
        return self.edgeDCEL.validateCells()

    def startScan(self):
        # print("starting scan...")
        # self.setBounds()
        # self.edgeDCEL.setBounds(self.bounds)
        # self.scanning = True
        pass

    def finishScan(self):
        # print("finishing scan...")
        # self.delaunay.verify_delaunay()
        # self.outputVoronoi()
        pass

    # def scanStarted(self):
        # if self.scanline.y < (self.view_bounds["ymax"]):
        #     return True
        # else:
        #     return False
        # return True

    # def scanFinished(self):
        # if self.scanline.y < (self.view_bounds["ymin"] - self.scanline.dy):
        #     return True
        # else:
        #     return False
        # return False

    def updateBeachfront(self, y_pos):
        for beach in self.beachfront.inorder():
            beach.bkpt = y_pos

    def addCircle(self, arc, directrix):
        circle = None
        try:
            circle = Circle(arc, directrix)
            circ_str = "\nADD CIRCLE"
            # make sure the circle's lowest point is below the scanline (i.e, where we just added the site)
            # note that this isnt quite correct (e.g think abt case where we
            # removed arc & are recomputing)
            circ_str += "\n\t adding a circle @cx {}, cy {}, low {})".format(
                circle.c.x, circle.c.y, circle.low.y)
            circ_str += "\n\t circle.sites(): :{}".format(
                str([str(site) for site in circle.csites()]))
            logger.debug(circ_str)
            self.circles.append(circle)
            self.event_pq.put(circle)
        except InvalidCircle as IC:
            logger.error("CIRCLE ERROR: Not a valid circle {}".format(str(IC)))

        except CircleAboveSweepline as CAS:
            logger.error("CIRCLE ERROR::Sweepline Not a valid circle {}".format(str(CAS)))

        return circle

    def processEvent(self, event):
        process_str = ""
        directrix = event.y
        self.updateBeachfront(directrix)
        if isinstance(event, Site):
            site = event
            process_str += "\nSite EVENT: \n\tsite event site{} @y = {}".format(
                site, site.y)

            #get the arc to the left of this one and add the new arc to the right of left_arc
            left_arc = self.beachfront.search_val(site.x)
            left_arc.circle = None
            right_bkpt = left_arc.right_bkpt(directrix)
            # print("\nleft arc: {}".format(left_arc))
            # print("processEvent::beachfront before\n {}".format(self.beachfront))

            #if new_arc splits left_arc then add a new parabolic segment associated with the left arc's site to the beachfront
            #if the next arc is None, then this bkpt will be INF 
            if left_arc != None:
                new_arc = self.beachfront.insert(site, left_arc)
                #if statement excludes the edge case where x coordinate of site is the breakpoint; we don't split in that case
                if site.x is not right_bkpt:
                    split_arc = self.beachfront.insert(left_arc.site, new_arc)
            else:
                new_arc = self.beachfront.insert(site)

            # add new edges
            if new_arc.prev != None:
                edge = self.edgeDCEL.addEdge(new_arc.prev.site, site)
                new_arc.edge = edge
            if new_arc.next != None:
                edge = self.edgeDCEL.addEdge(site, new_arc.next.site)
                new_arc.next.edge = edge

            #try to add circle events
            if new_arc.prev != None and new_arc.prev.prev != None:
                self.addCircle(new_arc.prev, directrix)

            if new_arc.next != None and new_arc.next.next != None:
                self.addCircle(new_arc.next, directrix)

        else:
            circle = event
            deleted_arcs = []

            print("circle event: c.y {} directrix: {}".format(circle.y, directrix))
            process_str += "\nCircle EVENT: \n\tcircle event @(cx{}, cy{}), sy{}".format(
                circle.c.x, circle.c.y, directrix)
            print("processEventCircle::beachfront before\n {}".format(self.beachfront))

            arc = circle.arc
            prev_arc = arc.prev
            next_arc = arc.next

            #add vertex in dcel
            new_vert = self.edgeDCEL.handleCircle(circle)

            #update edge destinations
            arc.edge.dest = new_vert
            next_arc.edge.dest = new_vert
            # arc.edge.next = next_arc.twin

            #remove arc

            self.beachfront.delete(arc)
            print("processEventCircle::beachfront after\n {}".format(self.beachfront))
            #remove circle events for neighboring arcs since they are no longer valid
            if prev_arc.circle:
                self.event_pq.remove(prev_arc.circle)
                prev_arc.circle = None
            if next_arc.circle:
                self.event_pq.remove(next_arc.circle)
                next_arc.circle = None

            #add a new edge
            new_edge = self.edgeDCEL.addEdge(prev_arc.site, next_arc.site, new_vert)

            #add new circle events
            if prev_arc.prev != None:
                self.addCircle(prev_arc, directrix)
            if next_arc.next != None:
                self.addCircle(next_arc, directrix)

            self.vvertices.append(circle.c)
            self.delaunay.add_face(circle)

        logger.debug(process_str)


    def precompute(self):
        '''
            precomputes the voronoi & delaunay digrams without visualization
            instead of doing it on-the-fly as is currently implemented
            could lead to functions such as showBeach(scanline),
            showCircle(circle) etc, where the events are all precomputed & precise
        '''
        precompute_str = "\n----**** voronoi precompute ****----"
        print("starting scan...")
        if self.sites:
            self.setBounds()
            self.edgeDCEL.setBounds(self.bounds)

            while (not self.event_pq.empty()):
                print("\nprocessEvent::event_pq")
                print(self.event_pq)
                event = self.event_pq.get()
                if event.y > self.y_pos:
                    self.processEvent(event)

            print("queue is empty")
            # self.edgeDCEL.finish()

        print("finishing scan...")
        # self.delaunay.verify_delaunay()
        # self.outputVoronoi()

        precompute_str += "\n----**** done with voronoi precompute ****----"
        # print("\n----**** done with voronoi precompute ****----")
