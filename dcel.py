from geometry import point, vector
# from math import inf
from itertools import chain, combinations
from we import fan
from math import pi, sqrt, acos, atan, atan2, degrees, cos

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
    # self.incident_edges = []
    # self.outgoing_edges = set()
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

def hsort(e1, e2):
  '''Sorts two edges counterclockwise'''

  if e1.angle < e2.angle:
      return -1
  elif e1.angle > e2.angle:
      return 1
  else:
      return 0

class Edge():
  def __init__(self, s1, s2, source, o):
    #for use in animation
    self.c = vector(1.0,1.0,1.0)
    self.s1 = s1
    self.s2 = s2

    #for use in data stucture
    self.face = s1
    self.twin = None
    self.next = None
    self.prev = None
    self.source = source
    self.angle = self.angle()
    # self.dest = None


    if (s1, s2) in o.edges:
      print("Bad Edge Orientation for {} src: {}".format(self, self.source))
      print("REPLACE: This edge already existed there: {} src:{}".format(o.edges[(s1, s2)], o.edges[(s1, s2)].source))

    if self.source is not None:
      # self.source.outgoing_edges.add(self)
      self.source.outgoing_edges.append(self)
      

    if (s2, s1) in o.edges:
      self.twin = o.edges[(s2, s1)]
      o.edges[(s2, s1)].twin = self

    o.edges[(s1, s2)] = self

  def angle(self):
    # dx = self.s2.x-self.s1.x
    # dy = self.s2.y-self.s1.y
    dx = self.s2.x-self.s1.x
    dy = self.s2.y-self.s1.y
    # return degrees(atan2(-dx, dy))
    # return degrees(atan(-dx/dy))
    l = sqrt(dx**2 + dy**2)
    if dx > 0:
        return degrees(acos(-dy/l))
    else:
        return degrees(2.0*pi - acos(-dy/l))
    # l = sqrt(dx**2 + dy**2)
    # # return cos(-dy/l)
    # if dx > 0:
    #   return cos(-dy/l)
    # else:
    #   return - cos(-dy/l)

  def addSource(self, o, source):
    self.source = source
    # if self.dest is not o.infv:
    # if o.edges
    self.source.outgoing_edges.append(o.edges[(self.s1, self.s2)])
    if (self.s2, self.s1) in o.edges:
      # print("add src")
      # print(self.twin)
      # self.twin.dest = source
      o.edges[(self.s2, self.s1)] = self.twin

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

  def addVertex(self, circle):
    ''' when a circle event gets handled, add the vertex to the list and create edges'''
    v = Vertex(circle, self)
    return v

  def _get_or_create(self, s1, s2, v):
    '''given two sites and a voronoit vertex, return the edge'''
    pass

  def addOutgoingEdges(self, v):
    s1 = v.sites[0]
    s2 = v.sites[1]
    s3 = v.sites[2]
    e1 = Edge(s1, s2, v, self)
    e2 = Edge(s2, s3, v, self)
    e3 = Edge(s3, s1, v, self)

    return [e1, e2, e3]

  def addEdges(self, v):
    s1 = v.sites[0]
    s2 = v.sites[1]
    s3 = v.sites[2]

    #create or update the outgoing edges
    if (s1, s2) in self.edges:
      e1 = self.edges[(s1, s2)]
      # print("UPDATE e1: {} src {} dest{} next{} twin{}".format(e1, e1.source, e1.dest, e1.next, e1.twin))
    else:
      e1 = Edge(s1, s2, v, self)
      # print("CREATE e1: {} src {} dest{} next{} twin{}".format(e1, e1.source, e1.dest, e1.next, e1.twin))

    if (s2, s3) in self.edges:
      e2 = self.edges[(s2, s3)]
      # print("UPDATE e2: {} src {} dest{} next{} twin{}".format(e2, e2.source, e2.dest, e2.next, e2.twin))
    else:
      e2 = Edge(s2, s3, v, self)
      # print("CREATE e2: {} src {} dest{} next{} twin{}".format(e2, e2.source, e2.dest, e2.next, e2.twin))

    if (s3, s1) in self.edges:
      e3 = self.edges[(s3, s1)]
      # print("UPDATE e3: {} src {} dest{} next{} twin{}".format(e3, e3.source, e3.dest, e3.next, e3.twin))
    else:
      e3 = Edge(s3, s1, v, self)
      # print("CREATE e3: {} src {} dest{} next{} twin{}".format(e3, e3.source, e3.dest, e3.next, e3.twin))

    #create or update all the incoming edges
    if (s2, s1) in self.edges:
      e1t = self.edges[(s2, s1)]
      # print("TWIN UPDATE e1t: {} src {} dest{} next{} twin{}".format(e1t, e1t.source, e1t.dest, e1t.next, e1t.twin))
    else:
      e1t = Edge(s2, s1, None, self)
      # print("TWIN CREATE e1t: {} src {} dest{} next{} twin{}".format(e1t, e1t.source, e1t.dest, e1t.next, e1t.twin))

    if (s3, s2) in self.edges:
      e2t = self.edges[(s3, s2)]
      # print("TWIN UPDATE e2t: {} src {} dest{} next{} twin{}".format(e2t, e2t.source, e2t.dest, e2t.next, e2t.twin))
    else:
      e2t = Edge(s3, s2, None, self)
      # print("TWIN CREATE e2t: {} src {} dest{} next{} twin{}".format(e2t, e2t.source, e2t.dest, e2t.next, e2t.twin))

    if (s1, s3) in self.edges:
      e3t = self.edges[(s1, s3)]
      # print("TWIN UPDATE e3t: {} src {} dest{} next{} twin{}".format(e3t, e3t.source, e3t.dest, e3t.next, e3t.twin))
    else:
      e3t = Edge(s1, s3, None, self)
      # print("TWIN CREATE e3t: {} src {} dest{} next{} twin{}".format(e3t, e3t.source, e3t.dest, e3t.next, e3t.twin))

    # create next/ prev links
    e1.addSource(self, v)
    e2.addSource(self, v)
    e3.addSource(self, v)

    e1t.next = e2
    e2t.next = e3
    e3t.next = e1

    e2.prev = e1t
    e3.prev = e2t
    e2.prev = e3t

    return [e1, e2, e3], [e1t, e2t, e3t]

  def postProcessEdges(self):
    print("----**** postprocessEdges ****----")
    infv = self.infv
    for vertex in self.vertices:
      #first, make sure every edge has a next
      for i, edge in enumerate(vertex.outgoing_edges):
        if edge.next is None:
          # print("{} vertex {} edge:{} edge.next is none".format(i, vertex, edge))
          # print("edge.twin.next.twin.next.twin {}".format(edge.twin.next.twin.next.twin))
          # edge.next = edge.twin.next.twin.next.twin
          if edge.twin.prev is not None:
            edge.next = edge.twin.prev
          elif edge.prev is not None:
            edge.next = edge.prev
          else:
            edge.next = edge.twin.next.twin.next.twin
            # edge.prev = edge.next
          # edge.dest = edge.next.source

        print("RESULT {} vertex {} edge:{} edge seemed fine... infv: {}".format(i, vertex, edge, self.infv))
        print("RESULT edge:{} face:{} src:{} next: {} twin: {}".format(edge, edge.face, edge.source, edge.next, edge.twin))
        print("RESULT twin:{} face:{} src:{} next: {} twin: {}\n".format(edge.twin, edge.twin.face, edge.twin.source, edge.twin.next, edge.twin.twin))
        # if edge.next.source is not None:
        #   print("edge {} edge.source {} edge.dest {}".format(edge, edge.source, edge.dest))
        #   print("edge {} edge.next {} edge.next.source {}".format(edge, edge.next, edge.next.source))
        #   print("edge {} edge.twin {} edge.twin.source {}".format(edge, edge.twin, edge.twin.source))
        #   edge.twin.addSource(self, edge.next.source)
        # elif edge.twin.source is not None:
        #   print("EDGE TWIN")
        #   print("edge {} edge.next {} edge.next.source {}".format(edge, edge.next, edge.next.source))
        #   print("edge {} edge.twin {} edge.twin.source {}".format(edge, edge.twin, edge.twin.source))
        # else:
        #   edge.next.addSource(self, infv)
        #   edge.twin.addSource(self, infv)
        # print("RESULT: edge {} edge.next {} edge.next.source {}".format(edge, edge.next, edge.next.source))
        # print("RESULT: edge {} edge.twin {} edge.twin.source {}".format(edge, edge.twin, edge.twin.source))

      #second, make sure every edge has a source and a dest
      for i, edge in enumerate(vertex.outgoing_edges):
        if edge.next.source is not None:
          print("edge {} edge.source {}".format(edge, edge.source))
          print("edge {} edge.next {} edge.next.source {}".format(edge, edge.next, edge.next.source))
          print("edge {} edge.twin {} edge.twin.source {}".format(edge, edge.twin, edge.twin.source))
          edge.twin.addSource(self, edge.next.source)
        elif edge.twin.source is not None:
          print("EDGE TWIN")
          print("edge {} edge.next {} edge.next.source {}".format(edge, edge.next, edge.next.source))
          print("edge {} edge.twin {} edge.twin.source {}".format(edge, edge.twin, edge.twin.source))
        else:
          edge.next.addSource(self, infv)
          edge.twin.addSource(self, infv)
        print("RESULT: edge {} edge.next {} edge.next.source {}".format(edge, edge.next, edge.next.source))
        print("RESULT: edge {} edge.twin {} edge.twin.source {}".format(edge, edge.twin, edge.twin.source))

    print("----**** done with postprocessEdges ****----")

  def printVertices(self):
    print("\n----**** printVertices ****----")
    for vertex in self.vertices:
      print("Vertex {} x: {} y: {}".format(vertex, vertex.position.x, vertex.position.y))
    print("\n----**** done with printVertices ****----")

  def printEdges(self):
    print("\n----**** printEdges ****----")
    for sites, edge in self.edges.items():
      print("Sites:{} edge:{} face: {} src:{} prev: {} next: {} twin: {}".format(str(sites), edge, edge.face, edge.source, edge.prev, edge.next, edge.twin))
    print("\n----**** done with printEdges ****----")

  def validateEdges():
    print("\n----**** validateEdges ****----")
    print("\n----**** done with validateEdges ****----")

  def validateCells(self):
    print("\n----**** validateCells ****----")
    # self.postProcessEdges()
    # self.printEdges()
    for vertex in self.vertices:
      if vertex is not self.infv:
        print("\nvertex {} with {} outgoing edges".format(vertex, len(vertex.outgoing_edges)))
        for edge in vertex.outgoing_edges:
          e = edge.next
          f = edge.face
          print("following the outgoing edge {}, face {} edge.next:{} of this vertex trying to form a cell vinf = {}".format(edge, edge.face, edge.next, self.infv))
          while e is not None and e.source is not vertex:
            print("following the outgoing edge {}".format(e, self.infv))
            print("\tedge: {} face:{} source: {}: twin: {}: prev: {} next: {}".format(e, e.face, e.source, e.twin, e.prev, e.next))
            e = e.next
          if e is None:
            print("RESULT: e is none, vertex {} did not form a valid cell...".format(vertex))
            return False
          elif e.source is vertex:
            print("\tedge: {} face:{} source: {} twin: {}: next: {}".format(e, e.face, e.source, e.twin, e.next))
            print("RESULT: vertex {} formed a valid cell!\n".format(vertex))
          else:
            return False
            print("RESULT: something else really weird on vertex v{}".format(vertex))
    return True
    print("----**** done with validateCells ****----\n")

  def handleCircle(self, circle):
    #add a vertex
    v = self.addVertex(circle)
    print(v)
    print(circle)
    # edges, twins = self.addEdges(v)

    #add edges

  def finish(self):
    #create the edge list
    for vertex in self.vertices:
      if vertex is not self.infv:
        print("vertex {}".format(vertex))
        edges = self.addOutgoingEdges(vertex)
        print(edges)

    for vertex in self.vertices:
      if vertex is not self.infv:
        # print("Pre sort for vertex {}".format(vertex))
        # [print(edge, edge.angle, edge.twin.angle) for edge in vertex.outgoing_edges]
        # vertex.sortEdges()
        # print("Post sort for vertex {}".format(vertex))
        # [print(edge, edge.angle, edge.twin.angle) for edge in vertex.outgoing_edges]
        for i, edge in enumerate(vertex.outgoing_edges):
          print("{} vertex {} edge{}".format(i, vertex, edge))
          try:
            etwin = self.edges[(edge.s2, edge.s1)]
          except:
            etwin = Edge(edge.s2, edge.s1, self.infv, self)
          #set edges
          # print("edge.twin {}, etwin {}".format(edge.twin, etwin))
          # edge.twin = etwin
          # etwin.twin = edge
          if i < len(vertex.outgoing_edges)-1:
            etwin.next = vertex.outgoing_edges[i+1]
            vertex.outgoing_edges[i+1].prev = etwin
          else:
            etwin.next = vertex.outgoing_edges[0]
            vertex.outgoing_edges[0].prev = etwin
        # print("Pre sort for vertex {}".format(vertex))
        # [print(edge, edge.angle, edge.twin.angle) for edge in vertex.outgoing_edges]
        # vertex.sortEdges()
        # print("Post sort for vertex {}".format(vertex))
        # [print(edge, edge.angle, edge.twin.angle) for edge in vertex.outgoing_edges]
          # if etwin.source is self.infv:
          #     etwin.prev = etwin.next

    #now handle the infinite vertex
    print("Pre sort for self.inf {}".format(self.infv))
    [print(edge, edge.angle, edge.twin.angle) for edge in self.infv.outgoing_edges]
    self.infv.sortTwinEdges()
    print("Post sort for self.infv {}".format(self.infv))
    [print(edge, edge.angle) for edge in self.infv.outgoing_edges]
    for i, edge in enumerate(self.infv.outgoing_edges):
      if i < len(self.infv.outgoing_edges)-1:
        edge.twin.next = self.infv.outgoing_edges[i+1]
        self.infv.outgoing_edges[i+1].prev = edge.twin
      else:
        edge.twin.next = self.infv.outgoing_edges[0]
        self.infv.outgoing_edges[0].prev = edge.twin



    for vertex in self.vertices:
      if vertex is not self.infv:
        for i, e in enumerate(vertex.outgoing_edges):
          if e.twin.prev is not None:
            if e.twin.source is self.infv:
              print("\n HALF INF EDGE")
            else:
              print("\n NORMAL EDGE EDGE")
            print("Setting e{} e.next: {} e.twin: {} e.twin.prev: {} e.twin.prev.twin: {}, e.twin.prev.twin.prev: {}, e.twin.prev.twin.prev.twin: {}".format(e, e.next, e.twin, e.twin.prev, e.twin.prev.twin, e.twin.prev.twin.prev, e.twin.prev.twin.prev.twin))
            print("source info: infv: {} e.src: {} e.twin.src {} e.twin.prev.src: {} e.twin.prev.twin.src: {} e.twin.prev.twin.prev.src: {} e.twin.prev.twin.prev.twin.src: {}".format(self.infv, e.source, e.twin.source, e.twin.prev.source, e.twin.prev.twin.source, e.twin.prev.twin.prev.source, e.twin.prev.twin.prev.twin.source))
            if e.next is not None:
              print("e.next: {} e.next.source {}".format(e.next, e.next.source))
            else:
              print("e.next: {}".format(e.next))
              # e.next = e.twin.prev.twin
            # e.next = e.twin.prev.twin.prev.twin
            print("RESULT: e{} e.face:{} e.next: {} e.next.face: {} e.next.source {} e.twin.prev.twin {} e.twin.prev.twin.prev: {}".format(e, e.face, e.next, e.next.face, e.next.source, e.twin.prev.twin, e.twin.prev.twin.prev))
          else:
            if e.twin.source is self.infv:
              print("oh this is a half infinite edge")
              print("e.twin {} e.twin.next:{} e.twin.next.next: {} e.twin.next.prev {}".format(e.twin, e.twin.next, e.twin.next.next, e.twin.next.prev))
              # print("e.next.twin {} e.next.twin.src: {}".format(e.next.twin, e.next.twin.source))
            else:
              print("HMMMM no twin prev for edge")
    # self.validateCells()
    # pass

  def clipEdge(self, edge):
    '''
    given an edge, return the endpoints (as points, to be drawn by opengl)
    '''
    if edge.next.source is self.infv:
      e1 = edge.source.position
      #make a movement vector 
      #this is the angle of the vector
      mp_sites = point((edge.s1.x + edge.s2.x)/2.0, (edge.s1.y + edge.s2.y)/2.0, 0.0)
      dy = edge.source.position.y - mp_sites.y
      dx = edge.source.position.x - mp_sites.x
      v = vector(dx, dy, 0.0)
      # print()
      unit_v = v.unit()
      v2 = unit_v.scale(2.0*sqrt(2.0))
      negv2 = v2.neg()
      #now v2 has length 2*2(1/2) (the total length of the longest diagonal)
      #do a point vector sum
      e2 = e1.plus(negv2)
      print("edge: {} v:{} e1:{} e2: {} mp_sites {}".format(edge, v, e1, e2, mp_sites))
      return e1, e2
    else:
      return edge.source.position, edge.dest.position

  def edgesToBuffer(self):
    #return the edge buffer
    if self.validateCells():
      self.printEdges()
      edges = []
      colors = []
      color1 = vector(0, 0, 1.0)
      color2 = vector(0,  1.0, 0)
      color3 = vector(1.0, 0, 0)
      # for edge in self.edges.values():
      for vertex in self.vertices:
        print(vertex)
        for edge in vertex.outgoing_edges:
          print(edge)
          #we only need to draw half the edges
          #right now, we're only excluding the outgoing half infinite edges
          # if edge.source is not None or edge.dest is not None or edge.source is not self.infv:
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





