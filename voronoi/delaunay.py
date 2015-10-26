import logging
logger = logging.getLogger(__name__)
logging.basicConfig(filename='logging/delaunay.log', level=logging.DEBUG)
logging.basicConfig(filename='logging/errors.log', level=logging.WARNING)

from .structures.we import face, edge, vertex, fan


class fan_face:
    ''' iterator that yields the faces around a vertex of the delaunay '''
    # returns a fan of the faces of the DT at a site

    def __init__(self, vertex):
        self.vertex = vertex
        self.which = None

    # __iter__
    #
    # (Re)sets this as an iterator for the start of a loop.
    #
    def __iter__(self):
        self.which = self.vertex.edge     # First edge on the fan.
        return self

    # __next__
    #
    # Advances the iterator to the next edge on the fan.
    #
    def __next__(self):

        if self.which is None:
            # If we've exhausted the edges that form the fan, stop.
            raise StopIteration
        else:
            # Otherwise, note where we are in the fan...
            current = self.which

            # ...and advance to the next edge.

            # To advance, make sure that we're not the whole way around...
            if current.next.next.twin is not None and \
               current.next.next.twin != self.vertex.edge:

                # ...and, if not, advance to the next fan edge.
                self.which = current.next.next.twin

            # Otherwise, signal that we've exhausted our edges.  This
            # "None" signal will be noticed by a subsequent call to
            # __next__.
            else:
                self.which = None

            # Regardless, give back the current edge.
            return current.face


class Delaunay:
    vertices = None

    def __init__(self, voronoi):
        self.vertex = []
        self.edge = {}
        self.voronoi = voronoi
        self.face = []
        self.face_vertex = {}

    # def v_faces(self, vertex):
    #   return fan_face(vertex)

    def add_face(self, circle):
        v1 = vertex(circle.s1.p, self)
        v2 = vertex(circle.s2.p, self)
        v3 = vertex(circle.s3.p, self)
        f = face(v1, v2, v3, self)
        self.face.append(f)
        self.face_vertex[face] = circle.c

    def toBuffer(self):
        varray = []
        carray = []
        for f in self.face:
            for i in [0, 1, 2]:
                varray.extend(f.vertex(i).position.components())
                carray.extend(f.vertex(i).color().components())
        return (varray, carray)
