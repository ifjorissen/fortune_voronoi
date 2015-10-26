import logging
import logging.config

log = logging.getLogger('dcel')

from ..geom.geometry import point, vector
from .we import fan
# from math import inf
from itertools import chain, combinations
from math import pi, sqrt, acos, atan, atan2, degrees, cos, radians, sin, tan, fabs


class Vertex():

    def __init__(self, circle, o):
        if circle:
            self.position = circle.c
            self.sites = circle.csites()
        else:
            self.position = point(float('inf'), float('inf'), float('inf'))
            self.sites = None
            o.infv = self
        o.vertices.append(self)
        self.id = len(o.vertices)
        self.outgoing_edges = []
        self.edge = None

    def sortEdges(self):
        '''
        take the set of outgoing edges and sort them by angle clockwise
        '''
        self.outgoing_edges.sort(key=lambda edge: edge.angle, reverse=True)

    def sortTwinEdges(self):
        '''
        take the set of outgoing edge twins and sort them by angle clockwise
        '''
        self.outgoing_edges.sort(
            key=lambda edge: edge.twin.angle, reverse=False)


class Edge():

    def __init__(self, s1, s2, source, o):
        # for use in animation
        self.c = vector(1.0, 1.0, 1.0)
        self.s1 = s1
        self.s2 = s2
        self.length = None
        self.e1 = None
        self.e2 = None

        # for use in data stucture
        self.twin = None
        self.next = None
        self.prev = None
        self.source = source

        # for use in edge clipping
        self.angle = self.angle()

        if (s1, s2) in o.edges:
            log.debug("Bad Edge Orientation for {} src: {}".format(
                self, self.source))
            log.debug("REPLACE: This edge already existed there: {} src:{}".format(
                o.edges[(s1, s2)], o.edges[(s1, s2)].source))

        # update outgoing edges
        if self.source is not None:
            self.source.outgoing_edges.append(self)

        # update twin
        if (s2, s1) in o.edges:
            self.twin = o.edges[(s2, s1)]
            o.edges[(s2, s1)].twin = self

        # associate this edge with a Cell
        try:
            f = o.cells[s1]
            # f.edges.append(self)
        except:
            f = o.addCell(s1, self)
        self.cell = f
        o.edges[(s1, s2)] = self

    def angle(self):
        ''' given an edge, calculate its angle based on its sites'''
        dx = self.s2.x - self.s1.x
        dy = self.s2.y - self.s1.y

        l = sqrt(dx**2 + dy**2)
        if dx > 0:
            return degrees(acos(-dy / l))
        else:
            return degrees(2.0 * pi - acos(-dy / l))

    def dist_to_boundary(self, bounds, v, e):
        ymax = bounds["ymax"]
        xmax = bounds["xmax"]
        ymin = bounds["ymin"]
        xmin = bounds["xmin"]

        o = self.source.position
        doxmax = fabs((xmax - o.x) / v.dx)
        doymax = fabs((ymax - o.y) / v.dy)
        doxmin = fabs((xmin - o.x) / v.dx)
        doymin = fabs((ymin - o.y) / v.dy)

        # get the distance from boundaries to source in appropriate quadrant
        # calculate that length and then scale the vector by that
        if v.dx > 0:
            # first quadrant
            if v.dy > 0:
                # distance to xmax: (xmax, a) --> solve for a
                # distance to ymax: (b, ymax) --> solve for b
                vs_xmax = v.scale(doxmax)
                bx = o.plus(vs_xmax)

                # find the scalar the vector is scaled by to get to xmax
                vs_ymax = v.scale(doymax)
                by = o.plus(vs_ymax)

            # fourth quadrant
            else:
                vs_xmax = v.scale(doxmax)
                bx = o.plus(vs_xmax)

                vs_ymin = v.scale(doymin)
                by = o.plus(vs_ymin)

        else:
            # second quadrant
            if v.dy > 0:
                vs_xmin = v.scale(doxmin)
                bx = o.plus(vs_xmin)

                vs_ymax = v.scale(doymax)
                by = o.plus(vs_ymax)

            # third quadrant
            else:
                vs_xmin = v.scale(doxmin)
                bx = o.plus(vs_xmin)

                vs_ymin = v.scale(doymin)
                by = o.plus(vs_ymin)

        # take the minimum of the distances between the respective boundaries
        pdx = o.dist(bx)
        pdy = o.dist(by)
        l = min(pdx, pdy)

        return l

    def addSource(self, o, source):
        '''given and edge and a dcel object, assign a source and update twin'''
        log.debug("Updated source of {} with source {}".format(self, source))
        self.source = source
        self.source.outgoing_edges.append(o.edges[(self.s1, self.s2)])
        if (self.s2, self.s1) in o.edges:
            o.edges[(self.s2, self.s1)] = self.twin

# To Do: actually create the cells


class Cell():

    def __init__(self, site, o):
        self.site = site
        self.edge = None
        o.cells[site] = self

        # self.edges = []


class VoronoiDCEL():

    def __init__(self):
        self.bounds = {"xmin": -1.0, "xmax": 1.0, "ymin": -1.0, "ymax": 1.0}
        self.infv = None
        self.delaunay = None
        self.vertices = []
        self.edges = {}
        self.cells = {}
        # create infinite vertex
        if not self.infv:
            infv = Vertex(None, self)
        else:
            infv = self.infv

    def addCell(self, s1, e):
        '''given a site and a vertex, add it to the Cell'''
        f = Cell(s1, self)
        f.edge = e
        # f.edges.append(e)

    def addVertex(self, circle):
        ''' when a circle event gets handled, add the vertex to the list and create edges'''
        v = Vertex(circle, self)
        return v

    def addOutgoingEdges(self, v):
        s1 = v.sites[0]
        s2 = v.sites[1]
        s3 = v.sites[2]
        e1 = Edge(s1, s2, v, self)
        e2 = Edge(s2, s3, v, self)
        e3 = Edge(s3, s1, v, self)

        log.debug("Added outgoing edges for vertex {}. e1: {} e2: {} e3:{}".format(
            v, e1, e2, e3))
        return [e1, e2, e3]

    def clipEdge(self, edge):
        '''
        given an edge, return & set the endpoints and edge length
        '''
        if edge.next.source is self.infv or edge.source is self.infv:
            # construct a unit vector according to edge angle
            if edge.next.source is self.infv:
                e = edge
            else:
                e = edge.twin

            angle = e.angle
            nv = vector(cos(radians(angle)), sin(radians(angle)), 0.0)
            v = nv.unit()

            if edge.length is None:
                l = e.dist_to_boundary(self.bounds, v, edge)
            else:
                l = e.length

            e1 = e.source.position
            v2 = v.scale(l)
            e2 = e1.plus(v2)

        else:
            e1 = edge.source.position
            e2 = edge.next.source.position
            vl = e1.minus(e2)
            l = vl.norm()

        edge.e1 = e1
        edge.e2 = e2
        if edge.length is None:
            edge.length = l
            edge.twin.length = l
        return e1, e2

    def clipEdges(self):
        for edge in self.edges.values():
            self.clipEdge(edge)

    def printCells(self):
        cell_str = "\n\n----**** printCells ****----"
        for site, cell in self.cells.items():
            cell_str += "\n\tCell: {} site: {} edge: {}".format(
                cell, cell.site, cell.edge)
            e = cell.edge
            v = e.source
            while e is not None and e.next.source is not v:
                cell_str += "\n\t\tfollowing the outgoing edge: {}, edge.source:{}, edge.next.source: {}".format(
                    e, e.source, e.next.source)
                e = e.next
            cell_str += "\n\t\tlast edge of this cell {}\n".format(
                e, e.source, e.next.source)

        cell_str += "\n----**** done with printCells ****----"
        return cell_str

    def printVertices(self):
        vert_str = "\n\n----**** printVertices ****----"
        for vertex in self.vertices:
            vert_str += "\n\tvertex {} x: {} y: {}".format(
                vertex, vertex.position.x, vertex.position.y)
        vert_str += "\n----**** done with printVertices ****----"
        return vert_str

    def printEdgeLinks(self):
        '''Prints the link info for every edge '''
        edge_str = "\n\n----**** printEdgeLinks ****----"
        for sites, edge in self.edges.items():
            edge_str += "\n\tedge:{} Cell: {} src:{} prev: {} next: {} twin: {}".format(
                edge, edge.cell, edge.source, edge.prev, edge.next, edge.twin)
        edge_str += "\n----**** done with printEdgeLinks ****----"
        return edge_str

    def printEdgeGeo(self):
        '''Prints the geometric data for every edge'''
        edge_str = "\n\n----**** printEdgeGeo ****----"
        for sites, edge in self.edges.items():
            edge_str += "\n\tedge:{} angle: {}  length:{} e1:{} e2: {}".format(
                edge, edge.angle, edge.length, edge.e1, edge.e2)
        edge_str += "\n----**** done with printEdgeGeo ****----"
        return edge_str

    def validateCells(self):
        validate_cell_str = "\n\n----**** validateCells ****----"
        for vertex in self.vertices:
            if vertex is not self.infv:
                validate_cell_str += "\nvertex {} with {} outgoing edges".format(
                    vertex, len(vertex.outgoing_edges))
                for edge in vertex.outgoing_edges:
                    e = edge.next
                    f = edge.cell
                    validate_cell_str += "\nfollowing the outgoing edge {}, Cell {} edge.next:{} of this vertex trying to form a cell".format(
                        edge, edge.cell, edge.next)
                    while e is not None and e.source is not vertex:
                        validate_cell_str += "\nfollowing the outgoing edge {}".format(
                            e)
                        validate_cell_str += "\n\tedge: {} Cell:{} source: {}: twin: {}: prev: {} next: {}".format(
                            e, e.Cell, e.source, e.twin, e.prev, e.next)
                        e = e.next
                    if e is None:
                        validate_cell_str += "\nRESULT: e is none, following {} from vertex {} did not form a valid cell...".format(
                            edge, vertex)
                        log.error("\nINVALID CELL: e is none, following {} from vertex {} did not form a valid cell...".format(
                            edge, vertex))
                        return False
                    elif e.source is vertex:
                        validate_cell_str += "\n\tedge: {} Cell:{} source: {} twin: {}: next: {}".format(
                            e, e.Cell, e.source, e.twin, e.next)
                        validate_cell_str += "\nRESULT: vertex {} formed a valid cell!\n".format(
                            vertex)
                    else:
                        log.error(
                            "RESULT: something else really weird on vertex v{}".format(vertex))
                        validate_cell_str += "\nRESULT: something else really weird on vertex v{}".format(
                            vertex)
                        return False
        validate_cell_str += "\n----**** done with validateCells ****----\n"
        log.debug(validate_cell_str)
        return True

    def handleCircle(self, circle):
        # add a vertex
        v = self.addVertex(circle)
        log.debug("Handling circle {} added {} to {}.vertices".format(
            circle, v, self))

    def finish(self):
        finish_str = "\n\n----**** voronoi finish ****----"
        # create the edge list
        for vertex in self.vertices:
            if vertex is not self.infv:
                edges = self.addOutgoingEdges(vertex)

        for vertex in self.vertices:
            if vertex is not self.infv:
                for i, edge in enumerate(vertex.outgoing_edges):
                    finish_str += "\n{} vertex {} edge{} edge.angle {}".format(
                        i, vertex, edge, edge.angle)
                    try:
                        etwin = self.edges[(edge.s2, edge.s1)]
                    except:
                        etwin = Edge(edge.s2, edge.s1, self.infv, self)
                    # set edges prev and next
                    if i < len(vertex.outgoing_edges) - 1:
                        etwin.next = vertex.outgoing_edges[i + 1]
                        vertex.outgoing_edges[i + 1].prev = etwin
                    else:
                        etwin.next = vertex.outgoing_edges[0]
                        vertex.outgoing_edges[0].prev = etwin
                    finish_str += "\n\t{} RESULT vertex {}: edge: {} edge.twin {} edge.twin.next{} edge.twin.prev: {}".format(
                        i, vertex, edge, edge.twin, edge.twin.next, edge.twin.prev)

        # now handle the infinite vertex
        finish_str += "\nSorting edges on infinite vertex ... "
        finish_str += "\nPre sort for self.inf {}\n".format(self.infv)
        finish_str += str([(str(edge), str(edge.angle), str(edge.twin.angle))
                           for edge in self.infv.outgoing_edges])

        self.infv.sortTwinEdges()

        finish_str += "\nPost sort for self.infv {}".format(self.infv)
        finish_str += str([(str(edge), str(edge.angle), str(edge.twin.angle))
                           for edge in self.infv.outgoing_edges])
        for i, edge in enumerate(self.infv.outgoing_edges):
            finish_str += "\n{} vertex {} edge{} edge.angle {}".format(
                i, self.infv, edge, edge.angle)
            if i < len(self.infv.outgoing_edges) - 1:
                edge.twin.next = self.infv.outgoing_edges[i + 1]
                self.infv.outgoing_edges[i + 1].prev = edge.twin
            else:
                edge.twin.next = self.infv.outgoing_edges[0]
                self.infv.outgoing_edges[0].prev = edge.twin
            finish_str += "\n\tRESULT for {} vertex {}: edge: {} edge.twin {} edge.twin.next{} edge.twin.prev: {}".format(
                i, vertex, edge, edge.twin, edge.twin.next, edge.twin.prev)
        # print("----**** done with voronoi finish ****----")
        finish_str += "\n----**** done with voronoi finish ****----"
        log.debug(finish_str)

        # self.createCells()
        self.clipEdges()
        return finish_str

    def printDCEL(self):
        self.printVertices()
        self.printEdges()
        self.printCells()

    def edgesToBuffer(self):
        # return the edge buffer
        edges = []
        colors = []
        color1 = vector(0, 0, 1.0)
        color2 = vector(0,  1.0, 0)
        color3 = vector(1.0, 0, 0)
        for edge in self.edges.values():
            edges.extend(edge.e1.components())
            edges.extend(edge.e2.components())
            colors.extend(edge.s1.c.components())
            colors.extend(edge.s2.c.components())
        return edges, colors

    def validateDCEL(self):
        '''validate the diagram'''
        self.finish()
        self.validateCells()
