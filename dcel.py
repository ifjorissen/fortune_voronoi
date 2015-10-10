from geometry import point, vector
# from math import inf
from itertools import chain
from we import fan
from math import pi, sqrt

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
    self.outgoing_edges = set()
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
  def __init__(self, s1, s2, source, o):
    #for use in animation
    self.c = vector(1.0,1.0,1.0)
    self.s1 = s1
    self.s2 = s2

    #for use in data stucture
    self.face = None
    self.twin = None
    self.next = None
    self.source = source
    self.dest = None
    
    if (s1, s2) in o.edges:
      #update an edge or figure out that we had an error
      if self.source is not None and o.edges[(s1, s2)].source is None: 
        print("UPDATE: This edge already existed there: {} src:{} dst:{}, updating that edges src with nsrc{}".format(o.edges[(s1, s2)], o.edges[(s1, s2)].source, o.edges[(s1, s2)].dest, self.source))
        o.edges[(s1, s2)].source = self.source
      else:
        print("Bad Edge Orientation for {} src: {} dst: {}".format(self, self.source, self.dest))
        print("REPLACE: This edge already existed there: {} src:{} dst:{}".format(o.edges[(s1, s2)], o.edges[(s1, s2)].source, o.edges[(s1, s2)].dest))
        # o.edges[(s1, s2)] = self
    else:
      #brand new edge
      o.edges[(s1, s2)] = self

    if o.edges[(s1, s2)].source is not None:
      o.edges[(s1, s2)].source.outgoing_edges.add(o.edges[(s1, s2)])

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
    #To do: ideally a create or update type function because this is
    # a) wildly inefficient and b) feels really wrong
    #constructs the three outgoing edges (i.e v is the source)
    #check to see if the edges exist, if they do, update them
    #if they don't create them

    #add or update these edges
    Edge(v.sites[0], v.sites[1], v, self)
    Edge(v.sites[1], v.sites[2], v, self)
    Edge(v.sites[2], v.sites[0], v, self)

    #add or update the twins
    Edge(v.sites[1], v.sites[0], None, self)
    Edge(v.sites[2], v.sites[1], None, self)
    Edge(v.sites[0], v.sites[2], None, self)

    #get the results from self.edges
    e1 = self.edges[(v.sites[0], v.sites[1])]
    e1t = self.edges[(v.sites[1], v.sites[0])]
    e2 = self.edges[(v.sites[1], v.sites[2])]
    e2t = self.edges[(v.sites[2], v.sites[1])]
    e3 = self.edges[(v.sites[2], v.sites[0])]
    e3t = self.edges[(v.sites[0], v.sites[2])]

    #update dest, source and twin relevant edges
    e1t.dest = e1.source
    e1.twin = e1t
    e1t.twin = e1
    e1t.next = e2

    e2t.dest = e2.source
    e2.twin = e2t
    e2t.twin = e2
    e2t.next = e3

    e3t.dest = e3.source
    e3.twin = e3t
    e3t.twin = e3
    e3t.next = e1

    return [e1, e2, e3]

  def postProcessEdges(self):
    print("----**** postprocessEdges ****----")
    infv = self.infv
    for vertex in self.vertices:
      for edge in vertex.outgoing_edges:
        if edge.twin.source is None:
          print("edge:{} edge.twin{} has no source: edge.twin.dest{}, edge.source{} edge.dest {}".format(edge, edge.twin, edge.twin.dest, edge.source, edge.dest))
          edge.twin.source = infv
          edge.dest = infv
          if edge.next is None:
            print("edge.next is none")
            print("edge.twin.next.twin {}".format(edge.twin.next.twin))
            edge.next = edge.twin.next.twin.next
          print("RESULT")  
          print("edge:{} src:{} dst:{} next: {} twin: {}".format(edge, edge.source, edge.dest, edge.next, edge.twin))
          print("twin:{} src:{} dst:{} next: {} twin: {}\n".format(edge.twin, edge.twin.source, edge.twin.dest, edge.twin.next, edge.twin.twin))
        else:
          print("edge seemed fine... infv: {}".format(self.infv))
          print("edge:{} src:{} dst:{} next: {} twin: {}".format(edge, edge.source, edge.dest, edge.next, edge.twin))
          print("twin:{} src:{} dst:{} next: {} twin: {}\n".format(edge.twin, edge.twin.source, edge.twin.dest, edge.twin.next, edge.twin.twin))

    print("----**** done with postprocessEdges ****----")

  def printVertices(self):
    print("\n----**** printEdges ****----")
    for vertex in self.vertices:
      print("Vertex {} x: {} y: {}".format(vertex, vertex.position.x, vertex.position.y))
    print("\n----**** done with printEdges ****----")

  def printEdges(self):
    print("\n----**** printEdges ****----")
    for sites, edge in self.edges.items():
      print("Sites: {} edge:{} src:{} dst:{} next: {} twin: {}".format(str(sites), edge, edge.source, edge.dest, edge.next, edge.twin))
    print("\n----**** done with printEdges ****----")

  def validateEdges():
    print("\n----**** validateEdges ****----")
    print("\n----**** done with validateEdges ****----")

  def validateCells(self):
    print("\n----**** validateCells ****----")
    self.postProcessEdges()
    # self.printEdges()
    for vertex in self.vertices:
      if vertex is not self.infv:
        print("\nvertex {} with {} outgoing edges".format(vertex, len(vertex.outgoing_edges)))
        for edge in vertex.outgoing_edges:
          e = edge.next
          print("following the outgoing edge {}, edge.next:{} of this vertex trying to form a cell vinf = {}".format(edge, edge.next, self.infv))
          while e is not None and e.source is not vertex:
            print("following the outgoing edge {}".format(e, self.infv))
            print("\tedge: {} source: {} dest: {}: twin: {}: next: {}".format(e, e.source, e.dest, e.twin, e.next))
            if e.next is not None and e.dest is not e.next.source:
              print("\tERROR edge: {} source: {} dest: {}: twin: {}: next: {} next.source: {}".format(e, e.source, e.dest, e.twin, e.next, e.next.source))
              print("RESULT: e.next.source is not e.dest, vertex {} did not form a valid cell...".format(vertex))
              return False
            e = e.next
          if e is None:
            print("RESULT: e is none, vertex {} did not form a valid cell...".format(vertex))
            return False
          elif e.source is vertex:
            print("\tedge.next: {} source: {} dest: {}: twin: {}: next: {}".format(e.next, e.next.source, e.next.dest, e.next.twin, e.next.next))
            print("RESULT: vertex {} formed a valid cell!\n".format(vertex))
          else:
            return False
            print("RESULT: something else really weird on vertex v{}".format(vertex))
    return True
    print("----**** done with validateCells ****----\n")

  def handleCircle(self, circle):
    v = self.addVertex(circle)
    edges = self.addEdges(v)

  def clipEdge(self, edge):
    '''
    given an edge, return the endpoints (as points, to be drawn by opengl)
    '''
    if edge.dest is self.infv:
      e1 = edge.source.position
      #make a movement vector 
      #this is the angle of the vector
      mp_sites = point((edge.s1.x + edge.s2.x)/2.0, (edge.s1.y + edge.s2.y), 0.0)
      dy = edge.source.position.y - mp_sites.y
      dx = edge.source.position.x - mp_sites.x
      v = vector(dx, dy, 0.0)
      unit_v = v.unit()
      v2 = unit_v.scale(2.0*sqrt(2.0))
      negv2 = v2.neg()
      #now v2 has length 2*2(1/2) (the total length of the longest diagonal)
      #do a point vector sum
      e2 = e1.plus(negv2)
      return e1, e2
    else:
      return edge.source.position, edge.dest.position

  def edgesToBuffer(self):
    #return the edge buffer
    if self.validateCells():
      edges = []
      colors = []
      color1 = vector(0, 0, 1.0)
      color2 = vector(0,  1.0, 0)
      color3 = vector(1.0, 0, 0)
      for edge in self.edges.values():
        #we only need to draw half the edges
        #right now, we're only excluding the outgoing half infinite edges
        if edge.source is not self.infv:
          e1, e2 = self.clipEdge(edge)
          edges.extend(e1.components())
          edges.extend(e2.components())
          colors.extend(edge.s1.c.components())
          colors.extend(edge.s2.c.components())
      return (edges, colors)
    else:
      print("ERROR: some voronoi cells were not valid")

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





