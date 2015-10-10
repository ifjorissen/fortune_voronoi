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
    # self.arc = arc
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

    if (s2, s1) in o.edges:
      if self.source is not None and o.edges[(s2, s1)].dest is None:
        print("UPDATE TWIN: This edge already existed there: {} src:{} dst:{}, updating that edges dst with nsrc{}".format(o.edges[(s2, s1)], o.edges[(s2, s1)].source, o.edges[(s2, s1)].dest, self.source))
        o.edges[(s2, s1)].dest = self.source
      print("Good Edge Orientation for {}".format(self))

    if o.edges[(s1, s2)].source is not None:
      o.edges[(s1, s2)].source.edge = o.edges[(s1, s2)]
      o.edges[(s1, s2)].source.outgoing_edges.add(o.edges[(s1, s2)])
      #set twins
      # o.edges[(s1, s2)].twin = o.edges[(s2, s1)]
      # o.edges[(s2, s1)].twin = o.edges[(s1, s2)] 
      # self.dest = self.twin.source

  #even though we know where the edge goes, if the circle event hasn't 
  #occurred yet we can't draw the whole thing
  def clipEdge(self):
    '''
    given an edge in the DCEL, return it's endpoints as points
    '''
    pass
    # return e1, e2

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
    e1.twin.next = e2

    e2t.dest = e2.source
    e2.twin = e2t
    e2t.twin = e2
    e2.twin.next = e3

    e3t.dest = e3.source
    e3.twin = e3t
    e3t.twin = e3
    e3.twin.next = e1

    #add twins if they don't exist 
    # if e1.twin is None:
    #   Edge(v.sites[1], v.sites[0], None, self)
    #   e1t = self.edges[(v.sites[1], v.sites[0])]
    #   e1t.dest = e1.source
    #   if e1 is not e1t.twin:
    #     print("WHAT setting e1's twin")
    #     e1.twin = e1t
    #     if e1t.twin is not e1:
    #       print("WHAT setting e1t's twin")
    #       e1t.twin = e1
    #   print("created {} src:{} dst:{}, twin:{}".format(e1t, e1t.source, e1t.dest, e1t.twin))
    # e1.twin.next = e2

    # if e2.twin is None:
    #   Edge(v.sites[2], v.sites[1], None, self)
    #   e2t = self.edges[(v.sites[2], v.sites[1])]
    #   e2t.dest = e2.source
    #   if e2 is not e2t.twin:
    #     print("WHAT setting e2's twin")
    #     e2.twin = e2t
    #     if e2t.twin is not e2:
    #       print("WHAT setting e2t's twin")
    #       e2t.twin = e3
    #   print("created {} src:{} dst:{}, twin:{}".format(e2t, e2t.source, e2t.dest, e2t.twin))
    # e2.twin.next = e3

    # if e3.twin is None:
    #   Edge(v.sites[0], v.sites[2], None, self)
    #   e3t = self.edges[(v.sites[0], v.sites[2])]
    #   e3t.dest = e3.source
    #   if e3 is not e3t.twin:
    #     print("WHAT setting e3's twin")
    #     e3.twin = e3t
    #     if e3t.twin is not e3:
    #       print("WHAT setting e3t's twin")
    #       e3t.twin = e3
    #   print("created {} src:{} dst:{}, twin:{}".format(e3t, e3t.source, e3t.dest, e3t.twin))
    # e3.twin.next = e1

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

    # for edge in list(self.edges.values()):
    #   if edge.source is None:
    #     edge.source = infv
    #     print("edge{} has no source: edge.twin.source {}".format(edge, edge.twin.source))
    #     if edge.twin.dest is None:
    #       if edge.twin.next is not None:
    #         print("Settin dest, checking that edge.twin.next.source {} is edge.src{}".format(edge.twin.next.source, edge.source))
    #         edge.twin.dest = edge.twin.next.source
    #       else:
    #         print("edge {} edge.next{}".format(edge, edge.next))
    #         print("edge.next.twin{}".format(edge.next.twin))
    #         print("edge.next.twin.next {}".format(edge.next.twin.next))
    #         print("edge.next.twin.next.twin {}".format(edge.next.twin.next.twin))
    #         print("Edge.twin.next DNE is edge{} edge.src{}, edge.next.twin.next.twin.src{}".format(edge, edge.source, edge.next.twin.next.twin.source))
    #         edge.twin.dest = edge.source
    #         edge.twin.next = edge.next.twin.next.twin
    #         print("Edge.twin.next {} edge.next.twin.next.twin.next{}\n".format(edge.twin.next, edge.next.twin.next.twin.next))
    #   else:
    #     print("edge seemed fine... vinf: {}".format(self.infv))
    #     # if edge.twin.source is None:
    #       # pass
    #     print("edge:{} src:{} dst:{} next: {} twin: {}".format(edge, edge.source, edge.dest, edge.next, edge.twin))
    #     print("twin:{} src:{} dst:{} next: {} twin: {}\n".format(edge.twin, edge.twin.source, edge.twin.dest, edge.twin.next, edge.twin.twin))
    print("----**** done with postprocessEdges ****----")

  def printEdges(self):
    print("\n----**** printEdges ****----")
    for sites, edge in self.edges.items():
      print("Sites: {} edge:{} src:{} dst:{} next: {} twin: {}".format(str(sites), edge, edge.source, edge.dest, edge.next, edge.twin))
    print("\n----**** done with printEdges ****----")

  def validateCells(self):
    print("\n----**** validateCells ****----")
    self.postProcessEdges()
    self.printEdges()
    for vertex in self.vertices:
      if vertex is not self.infv:
        print("\nvertex {} with {} outgoing edges".format(vertex, len(vertex.outgoing_edges)))
        for edge in vertex.outgoing_edges:
          e = edge.next
          print("following the outgoing edge {}, edge.next:{} of this vertex trying to form a cell vinf = {}".format(edge, edge.next, self.infv))
          while e is not None and e.source is not vertex:
            print("following the outgoing edge {}".format(e, self.infv))
            print("\tedge: {} source: {} dest: {}: twin: {}: next: {}".format(e, e.source, e.dest, e.twin, e.next))
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
    # if edge.source is self.infv:
    #   # we don't *really* need to draw this edge, but it's basically as below
    #   e1 = edge.dest.position
    #   #make a movement vector 
    #   #this is the angle of the vector
    #   mp_sites = point((edge.s1.x + edge.s2.x)/2.0, (edge.s1.y + edge.s2.y)/2.0, 0.0)
    #   dy = edge.dest.position.y - mp_sites.y
    #   dx = edge.dest.position.x - mp_sites.x
    #   v = vector(dx, dy, 0.0)
    #   unit_v = v.unit()
    #   v2 = unit_v.scale(2.0*sqrt(2.0))
    #   negv2 = v2.neg()
    #   #now v2 has length 2*2(1/2) (the total length of the longest diagonal)
    #   #do a point vector sum
    #   e2 = e1.plus(negv2)
    #   return e1, e2

    if edge.dest is self.infv:
      e1 = edge.source.position
      #make a movement vector 
      #this is the angle of the vector
      mp_sites = point((edge.s1.x + edge.s2.x)/2.0, (edge.s1.y + edge.s2.y)/2.0, 0.0)
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
        if edge.source is not None:
          e1, e2 = self.clipEdge(edge)
          edges.extend(e1.components())
          edges.extend(e2.components())
          colors.extend(edge.s1.c.components())
          colors.extend(edge.s2.c.components())
      return (edges, colors)
    else:
      print("some vornonoi cells were not valid")

    



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





