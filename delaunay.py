from we import face, edge, vertex, fan

class Delaunay:
  # edges = []
  # edge_buffer = []
  # faces = []
  vertices = None

  def __init__(self, voronoi):
    self.vertex = []
    self.edge = {}
    self.voronoi = voronoi
    self.face = []

  def add_face(self, circle):
    v1 = vertex(circle.s1.p, self)
    v2 = vertex(circle.s2.p, self)
    v3 = vertex(circle.s3.p, self)
    f = face(v1, v2, v3, self)
    self.face.append(f)

  def toBuffer(self):
    varray = []
    carray = []
    for f in self.face:
      for i in [0,1,2]:
        varray.extend(f.vertex(i).position.components())
        carray.extend(f.vertex(i).color().components())
    if len(varray) > 0:
      print(varray)
    return (varray, carray)