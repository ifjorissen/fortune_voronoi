import logging
logger = logging.getLogger(__name__)
logging.basicConfig(filename='logging/dcel.log',level=logging.DEBUG)
logging.basicConfig(filename='logging/errors.log',level=logging.ERROR)

from geometry import point, vector
# from math import inf
from itertools import chain, combinations
from we import fan
from math import pi, sqrt, acos, atan, atan2, degrees, cos, radians, sin, tan

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

  def around(self):
    return fan(self)

  def faces(self):
    return [e.face for e in fan(self)]

  def isSaturated(self):
    if len(self.incident_edges) == 3:
      return True
    elif len(self.outgoing_edges) == 3:
      return True
    else:
      return False

  def sortEdges(self):
    '''
    take the set of outgoing edges and sort them by angle clockwise
    '''
    self.outgoing_edges.sort(key=lambda edge:edge.angle, reverse=True)

  def sortTwinEdges(self):
    '''
    take the set of outgoing edges and sort them by angle clockwise
    '''
    self.outgoing_edges.sort(key=lambda edge:edge.twin.angle, reverse=False)

  def validate_vertex(self):
    if len(self.incident_edges) == self.outgoing_edges == 3:
      #validate that all incident edges have a twin that's an outgoing edge
      return True

    else:
      #raise an invalid vertex error
      print("error")
      return False

class Edge():
  def __init__(self, s1, s2, source, o):
    #for use in animation
    self.c = vector(1.0,1.0,1.0)
    self.s1 = s1
    self.s2 = s2
    self.e1 = None
    self.e2 = None 

    #for use in data stucture
    self.face = s1
    self.twin = None
    self.next = None
    self.prev = None
    self.source = source
    self.angle = self.angle()

    if (s1, s2) in o.edges:
      logging.debug("Bad Edge Orientation for {} src: {}".format(self, self.source))
      logging.debug("REPLACE: This edge already existed there: {} src:{}".format(o.edges[(s1, s2)], o.edges[(s1, s2)].source))

    if self.source is not None:
      self.source.outgoing_edges.append(self)
      

    if (s2, s1) in o.edges:
      self.twin = o.edges[(s2, s1)]
      o.edges[(s2, s1)].twin = self

    o.edges[(s1, s2)] = self

  def angle(self):
    ''' given an edge, calculate its angle based on its sites'''
    dx = self.s2.x-self.s1.x
    dy = self.s2.y-self.s1.y

    l = sqrt(dx**2 + dy**2)
    if dx > 0:
        return degrees(acos(-dy/l))
    else:
        return degrees(2.0*pi - acos(-dy/l))

  def addSource(self, o, source):
    '''given and edge and a dcel object, assign a source and update twin'''
    logging.debug("Updated source of {} with source {}".format(self, source))
    self.source = source
    self.source.outgoing_edges.append(o.edges[(self.s1, self.s2)])
    if (self.s2, self.s1) in o.edges:
      o.edges[(self.s2, self.s1)] = self.twin

  #TO DO: edge clipping should probably be done here?


#To Do: actually create the cells
class Cell():
  def __init__(self, voronoi_vertex, vertices, o):
    self.edges = []
    self.vertices = []
    self.vv = voronoi_vertex

class VoronoiDCEL():
  def __init__(self):
    bounds = {"xmin": -1.0, "xmax": 1.0, "ymin": -1.0, "ymax": 1.0}
    self.infv = None
    self.delaunay = None
    self.vertices = []
    self.edges = {}
    self.cells = []
    #create infinite vertex
    if not self.infv:
      infv = Vertex(None, self)
    else:
      infv = self.infv

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

    logging.debug("Added outgoing edges for vertex {}. e1: {} e2: {} e3:{}".format(v, e1, e2, e3))

    return [e1, e2, e3]

  def printVertices(self):
    vert_str = "\n----**** printVertices ****----"
    # print("\n----**** printVertices ****----")
    for vertex in self.vertices:
      # print("Vertex {} x: {} y: {}".format(vertex, vertex.position.x, vertex.position.y))
      vert_str += "\n\tvertex {} x: {} y: {}".format(vertex, vertex.position.x, vertex.position.y)
    # print("\n----**** done with printVertices ****----")
    vert_str += "\n----**** done with printVertices ****----"
    return vert_str

  def printEdgeLinks(self):
    '''Prints the link info for every edge '''
    edge_str = "\n----**** printEdgeLinks ****----"
    # print("\n----**** printEdges ****----")
    for sites, edge in self.edges.items():
      # print("edge:{} face: {} src:{} prev: {} next: {} twin: {}".format(edge, edge.face, edge.source, edge.prev, edge.next, edge.twin))
      edge_str += "\n\tedge:{} face: {} src:{} prev: {} next: {} twin: {}".format(edge, edge.face, edge.source, edge.prev, edge.next, edge.twin)
    edge_str += "\n----**** done with printEdgeLinks ****----"
    # print("\n----**** done with printEdges ****----")
    return edge_str

  def printEdgeGeo(self):
    '''Prints the geometric data for every edge'''
    edge_str = "\n----**** printEdgeGeo ****----"
    # print("\n----**** printEdges ****----")
    for sites, edge in self.edges.items():
      # print("edge:{} face: {} src:{} prev: {} next: {} twin: {}".format(edge, edge.face, edge.source, edge.prev, edge.next, edge.twin))
      edge_str += "\n\tedge:{} angle: {} e1:{} e2: {}".format(edge, edge.angle, edge.e1, edge.e2)
    edge_str += "\n----**** done with printEdgeGeo ****----"
    # print("\n----**** done with printEdges ****----")
    return edge_str

  def validateCells(self):
    validate_cell_str = "\n----**** validateCells ****----"
    # print("\n----**** validateCells ****----")
    for vertex in self.vertices:
      if vertex is not self.infv:
        validate_cell_str += "\nvertex {} with {} outgoing edges".format(vertex, len(vertex.outgoing_edges))
        # print("\nvertex {} with {} outgoing edges".format(vertex, len(vertex.outgoing_edges)))
        for edge in vertex.outgoing_edges:
          e = edge.next
          f = edge.face
          validate_cell_str += "\nfollowing the outgoing edge {}, face {} edge.next:{} of this vertex trying to form a cell".format(edge, edge.face, edge.next)
          # print("following the outgoing edge {}, face {} edge.next:{} of this vertex trying to form a cell".format(edge, edge.face, edge.next))
          while e is not None and e.source is not vertex:
            validate_cell_str += "\nfollowing the outgoing edge {}".format(e)
            validate_cell_str += "\n\tedge: {} face:{} source: {}: twin: {}: prev: {} next: {}".format(e, e.face, e.source, e.twin, e.prev, e.next)
            # print("following the outgoing edge {}".format(e))
            # print("\tedge: {} face:{} source: {}: twin: {}: prev: {} next: {}".format(e, e.face, e.source, e.twin, e.prev, e.next))
            e = e.next
          if e is None:
            validate_cell_str += "\nRESULT: e is none, following {} from vertex {} did not form a valid cell...".format(edge, vertex)
            logging.error("\nINVALID CELL: e is none, following {} from vertex {} did not form a valid cell...".format(edge, vertex))
            # print("RESULT: e is none, vertex {} did not form a valid cell...".format(vertex))
            return False
          elif e.source is vertex:
            validate_cell_str += "\n\tedge: {} face:{} source: {} twin: {}: next: {}".format(e, e.face, e.source, e.twin, e.next)
            # print("\tedge: {} face:{} source: {} twin: {}: next: {}".format(e, e.face, e.source, e.twin, e.next))
            validate_cell_str += "\nRESULT: vertex {} formed a valid cell!\n".format(vertex)
            # print("RESULT: vertex {} formed a valid cell!\n".format(vertex))
          else:
            logging.error("RESULT: something else really weird on vertex v{}".format(vertex))
            validate_cell_str += "\nRESULT: something else really weird on vertex v{}".format(vertex)
            return False
            # print("RESULT: something else really weird on vertex v{}".format(vertex))
    validate_cell_str += "\n----**** done with validateCells ****----\n"
    logging.debug(validate_cell_str)
    # print("----**** done with validateCells ****----\n")
    return True

  def handleCircle(self, circle):
    #add a vertex
    v = self.addVertex(circle)
    logging.debug("Handling circle {} added {} to {}.vertices".format(circle, v, self))

  def finish(self):
    finish_str = "\n----**** voronoi finish ****----"
    # print("----**** voronoi finish ****----")
    #create the edge list
    for vertex in self.vertices:
      if vertex is not self.infv:
        edges = self.addOutgoingEdges(vertex)

    for vertex in self.vertices:
      if vertex is not self.infv:
        for i, edge in enumerate(vertex.outgoing_edges):
          finish_str += "\n{} vertex {} edge{} edge.angle {}".format(i, vertex, edge, edge.angle)
          # print("{} vertex {} edge{}".format(i, vertex, edge))
          try:
            etwin = self.edges[(edge.s2, edge.s1)]
          except:
            etwin = Edge(edge.s2, edge.s1, self.infv, self)
          #set edges prev and next
          if i < len(vertex.outgoing_edges)-1:
            etwin.next = vertex.outgoing_edges[i+1]
            vertex.outgoing_edges[i+1].prev = etwin
          else:
            etwin.next = vertex.outgoing_edges[0]
            vertex.outgoing_edges[0].prev = etwin
          finish_str += "\n\t{} RESULT vertex {}: edge: {} edge.twin {} edge.twin.next{} edge.twin.prev: {}".format(i, vertex, edge, edge.twin, edge.twin.next, edge.twin.prev)

    #now handle the infinite vertex
    finish_str += "\nSorting edges on infinite vertex ... "
    finish_str += "\nPre sort for self.inf {}\n".format(self.infv)
    finish_str += str([(str(edge), str(edge.angle), str(edge.twin.angle)) for edge in self.infv.outgoing_edges])

    self.infv.sortTwinEdges()

    finish_str += "\nPost sort for self.infv {}".format(self.infv)
    finish_str += str([(str(edge), str(edge.angle), str(edge.twin.angle)) for edge in self.infv.outgoing_edges])
    for i, edge in enumerate(self.infv.outgoing_edges):
      finish_str += "\n{} vertex {} edge{} edge.angle {}".format(i, self.infv, edge, edge.angle)
      if i < len(self.infv.outgoing_edges)-1:
        edge.twin.next = self.infv.outgoing_edges[i+1]
        self.infv.outgoing_edges[i+1].prev = edge.twin
      else:
        edge.twin.next = self.infv.outgoing_edges[0]
        self.infv.outgoing_edges[0].prev = edge.twin
      finish_str += "\n\tRESULT for {} vertex {}: edge: {} edge.twin {} edge.twin.next{} edge.twin.prev: {}".format(i, vertex, edge, edge.twin, edge.twin.next, edge.twin.prev)
    # print("----**** done with voronoi finish ****----")
    finish_str += "\n----**** done with voronoi finish ****----"
    logging.debug(finish_str)
    return finish_str

  def clipEdge(self, edge):
    '''
    given an edge, return the endpoints (as points, to be drawn by opengl)
    '''
    if edge.next.source is self.infv or edge.source is self.infv:
      # ur_br = self.bounds["ymax"]/self.bounds["xmax"]
      # ul_br = self.bounds["ymax"]/self.bounds["xmin"]
      # br_br = self.bounds["ymin"]/self.bounds["xmax"]
      # bl_br = self.bounds["ymin"]/self.bounds["xmin"]

      #construct a unit vector according to edge angle
      if edge.next.source is self.infv:
        angle = edge.angle
        e1 = edge.source.position

      else:
        angle = edge.twin.angle
        e1 = edge.next.source.position
      
      v = vector(cos(radians(angle)), sin(radians(angle)), 0.0)
      t = tan(radians(angle))

      #to do: scale each edge according to boundaries
      #interim solution: make sure the vector is long enough to cover the longest diagonal
      dx = self.bounds["xmax"] - self.bounds["xmin"]
      dy = self.bounds["ymax"] - self.bounds["ymin"]
      e_scale = sqrt(dx**2 + dy**2)

      #scale the vector and assign endpoints
      v2 = v.scale(e_scale)
      e2 = e1.plus(v2)
      edge.e1 = e1
      edge.e2 = e2
      # print("SRC INF edge: {} v:{} e1:{} e2: {}".format(edge, v, e1, e2))
      return e1, e2

    else:
      # print("NORMAL edge: {} e1:{} e2: {}".format(edge, edge.source.position, edge.next.source.position))
      return edge.source.position, edge.next.source.position

  def edgesToBuffer(self):
    #return the edge buffer
    edges = []
    colors = []
    color1 = vector(0, 0, 1.0)
    color2 = vector(0,  1.0, 0)
    color3 = vector(1.0, 0, 0)
    for edge in self.edges.values():
      e1, e2 = self.clipEdge(edge)
      edges.extend(e1.components())
      edges.extend(e2.components())
      colors.extend(edge.s1.c.components())
      colors.extend(edge.s2.c.components())
    return (edges, colors)

  def constructCells(self):
    '''constructs voronoi cells for the diagram, simliar to the faces in we.py (counterclockwise)'''
    pass

  def validateDCEL(self):
    '''validate the diagram'''
    pass






