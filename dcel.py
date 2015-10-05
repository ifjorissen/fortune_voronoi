from geometry import point, vector
# from math import inf
from itertools import chain
from we import fan

#if you don't animate this you can use the delaunay digram to do A LOT of this work

class Vertex():
  def __init__(self, circle, o):
    if circle:
      self.position = circle.c
      self.sites = circle.csites()
    else:
      self.position = point(float('inf'), float('inf'), float('inf'))
      self.sites = None
      o.infv = self
      # else:
        #raise an error
    o.vertices.append(self)
    self.id = len(o.vertices)
    self.incident_edges = []
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

  def validate_vertex(self):
    if len(self.incident_edges) == self.outgoing_edges == 3:
      #validate that all incident edges have a twin that's an outgoing edge
      return True

    else:
      #raise an invalid vertex error
      print("error")
      return False

class Edge():
  # def __init__(self, s1, s2, arc, source=None, dest=None,):
  #   #for use in animation
  #   self.c = vector(1.0,1.0,1.0)
  #   self.s1 = s1
  #   self.s2 = s2
  #   self.arc = arc
  #   self.e1 = point(arc.breakr, arc.beach.arcqn(arc.breakr))
  #   self.e2 = point((self.s1.x + self.s2.x)/2.0, (self.s1.y + self.s2.x)/2.0)

  #   #for use in data stucture
  #   self.face = None
  #   self.twin = None
  #   self.next = None
  #   self.prev = None
  #   self.source = source
  #   self.dest = dest

  def __init__(self, s1, s2, source, o):
    #for use in animation
    self.c = vector(1.0,1.0,1.0)
    self.s1 = s1
    self.s2 = s2
    # self.arc = arc
    if source is not None:
      self.end1 = source.position
      source.edge = self
      source.outgoing_edges.append(self)
      #do math

    # self.end1 = point(arc.breakr, arc.beach.arcqn(arc.breakr))
    # self.end2 = point((self.s1.x + self.s2.x)/2.0, (self.s1.y + self.s2.x)/2.0)

    #for use in data stucture
    self.face = None
    self.twin = None
    self.next = None
    # self.prev = None
    self.source = source
    self.dest = None
    

    if (s1, s2) in o.edges:
      #update an edge or figure out that we had an error
      print(type((s1, s2)))
      print((s1, s2) == (s2, s1))
      if self.source is not None: 
        print("UPDATE: This edge already existed there: {} src:{} dst:{}, updating that edge with nsrc{}".format(o.edges[(s1, s2)], o.edges[(s1, s2)].source, o.edges[(s1, s2)].dest, self.source))
        o.edges[(s1, s2)].source = self.source
      else:
        print("Bad Edge Orientation for {} src: {} dst: {}".format(self, self.source, self.dest))
        print("REPLACE: This edge already existed there: {} src:{} dst:{}".format(o.edges[(s1, s2)], o.edges[(s1, s2)].source, o.edges[(s1, s2)].dest))
        o.edges[(s1, s2)] = self
    else:
      #brand new edge
      o.edges[(s1, s2)] = self

    if (s2, s1) in o.edges:
      print("Good Edge Orientation for {}".format(self))
      self.twin = o.edges[(s2, s1)]
      self.twin.twin = self
      self.dest = self.twin.source

  #even though we know where the edge goes, if the circle event hasn't 
  #occurred yet we can't draw the whole thing
  def clipEdge(self):
    # if not self.source:
    #   #midpoint of two sites
    #   e1 = self.circle.c
    #   e2 = self.circle.c
    pass

  def handleCircle(self, circle, o):
    pass

  def toBuffer(self):
    #draw a line beginning at breakpoint(or the vertex) and going through midpt
    e1 = [0, 0]
    e2 = [0, 0]
    line = list(chain.from_iterable([e1.components(), e2.components()]))
    color = list(chain.from_iterable([self.c.components(), self.c.components()]))
    return line, color

class Cell():
  def __init__(self, voronoi_vertex, vertices, o):
    self.edges = []
    self.vertices = []
    self.vv = voronoi_vertex


class DoublyConnectedEdgeList():
  def __init__(self):
    self.vertex = []
    self.edge = {}
    self.cell = []

class VoronoiDCEL():
  def __init__(self):
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
    # self.site_tuples = {}

  def addVertex(self, circle):
    ''' when a circle event gets handled, add the vertex to the list and create edges'''
    v = Vertex(circle, self)
    return v

  def addEdges(self, v):
    #constructs the three outgoing edges (i.e v is the source)
    e1 = Edge(v.sites[0], v.sites[1], v, self)
    e2 = Edge(v.sites[1], v.sites[2], v, self)
    e3 = Edge(v.sites[2], v.sites[0], v, self)

    #add twins if they don't exist
    if e1.twin is None:
      e1t = Edge(v.sites[1], v.sites[0], None, self)
      e1t.dest = e1.source
      print("created {} src:{} dst:{}, twin:{}".format(e1t, e1t.source, e1t.dest, e1t.twin))
    e1.twin.next = e2

    if e2.twin is None:
      e2t = Edge(v.sites[2], v.sites[1], None, self)
      e2t.dest = e2.source
      print("created {} src:{} dst:{}, twin:{}".format(e2t, e2t.source, e2t.dest, e2t.twin))
    e2.twin.next = e3

    if e3.twin is None:
      e3t = Edge(v.sites[0], v.sites[2], None, self)
      e3t.dest = e3.source
      print("created {} src:{} dst:{}, twin:{}".format(e3t, e3t.source, e3t.dest, e3t.twin))
    e3.twin.next = e1

    # if e1.twin is not None:
    #   e1.twin.next = e2

    # if e2.twin is not None:
    #   e2.twin.next = e3

    # if e3.twin is not None:
    #   e3.twin.next = e1

    return [e1, e2, e3]

  def postProcessEdges(self):
    print("----**** postprocessEdges ****----")
    # edges = self.edges.values()
    #add the vertex at infinity
    # if not self.infv:
    #   infv = Vertex(None, self)
    # else:
    infv = self.infv

    for edge in list(self.edges.values()):
      if edge.twin is None:
        if edge.dest is not None:
          print("edge {} had no twin but has a destination ...".format(edge))
          new_edge = Edge(edge.s2, edge.s1, edge.dest, self)
          print("successfully created one: {}".format(new_edge))
        else:
          print("edge {} had no twin...".format(edge))
          new_edge = Edge(edge.s2, edge.s1, infv, self)
          print("successfully created one: {}".format(new_edge))
      elif edge.source is None:
        print("edge {} had no source...".format(edge))
        edge.source = infv
        edge.twin.dest = infv
        if edge.twin.next is None:
          print("SETTING edge.twin:{}'s twin.next to: {}".format(edge.twin, edge.next.twin))
          edge.twin.next = edge.next.twin
        else:
          print("had a twin.next tho: {}".format(edge.twin.next))
    print("----**** done with postprocessEdges ****----")

  def printVoronoiEdges(self):
    print("\n----**** printVoronoiEdges ****----")
    self.postProcessEdges()
    for vertex in self.vertices:
      if vertex is not self.infv:
        print("\nvertex {} with {} outgoing edges".format(vertex, len(vertex.outgoing_edges)))
        for edge in vertex.outgoing_edges:
          while edge is not None and edge.dest is not vertex:
            print("following the outgoing edge {} of this vertex trying to form a cell".format(edge))
            print("\tedge: {} source: {} dest: {}: twin: {}: next: {}".format(edge, edge.source, edge.dest, edge.twin, edge.next))
            edge = edge.next
          if edge is None:
            #raise error
            print("vertex {} did not form a valid cell".format(vertex))
          elif edge.dest is vertex:
            print("vertex {} formed a valid cell!".format(vertex))
          else:
            print("something else really weird on vertex v{}".format(vertex))
    print("----**** done with printVoronoiEdges ****----\n")


  def constructVertices(self):
    pass

  def handleCircle(self, circle):
    v = self.addVertex(circle)
    edges = self.addEdges(v)


  def constructCells(self):
    '''constructs voronoi cells for the diagram, simliar to the faces in we.py (counterclockwise)'''
    pass

  def validateDCEL(self):
    '''validate the diagram'''
    pass

  def processFromDelaunay(self, vertices, delaunay):
    '''actually constructs the whole thing'''
    print("----**** processFromDelaunay ****----")
    #create vertices
    for vertex in vertices:
      Vertex(vertex, self)

    #create cells by looking at the delaunay sites
    for site in delaunay.vertex:
      sedges = [e.face for e in site.around()]
      print(sedges)
    print("----**** end processFromDelaunay ****----")





