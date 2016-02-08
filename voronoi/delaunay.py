import logging
from .geom.geometry import point, vector
from .structures.we import face, vertex, edge
from .structures.witness_circle import CircleWitness
from .structures.bubble import Bubble
logger = logging.getLogger(__name__)
logging.basicConfig(filename='logging/delaunay.log', level=logging.DEBUG)
logging.basicConfig(filename='logging/errors.log', level=logging.WARNING)


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

    def __init__(self, voronoi):
        self.vertex = []
        self.edge = {}
        self.voronoi = voronoi
        self.face = []
        self.site_vert = dict.fromkeys(voronoi.sites)
        self.infv = self.set_infinite_vertex()
        self.leftmost = None
        self.rightmost = None

        self.witnesses = {}
        self.face_voronoi = {}

    def set_infinite_vertex(self):
        p = point(float('inf'), float('inf'), float('inf'))
        return vertex(p, self)

    def get_or_add_vertex(self, site):
        '''
        given a vertex, either add it to the triangulation
        or return the vertex associated with that site
        '''
        if site not in self.site_vert:
            #add it, otherwise we're good to continue
            self.site_vert[site] = None

        if self.site_vert[site] is None:
            #create a vertex and add to dict
            v = vertex(site.p, self)
            self.site_vert[site] = v
        else:
            v = self.site_vert[site]

        return v

    def add_face(self, circle):
        v1 = self.get_or_add_vertex(circle.s1)
        v2 = self.get_or_add_vertex(circle.s2)
        v3 = self.get_or_add_vertex(circle.s3)
        f = face(v1, v2, v3, self)
        self.face_voronoi[face] = circle.c

    def inf_face(self, face):
        '''
        given a face, return the vertex at infinity if it exists
        '''
        v1 = face.vertex(0)
        v2 = face.vertex(1)
        v3 = face.vertex(2)
        if v1 is self.infv:
            return 1
        elif v2 is self.infv:
            return 2
        elif v3 is self.infv:
            return 3
        else:
            return None

    def get_inf_vert_pos(self, face, v_index):
        if v_index == 0:
            #avg 1 and 2
            vec = face.edge(1).vector()
            a = face.vertex(1).position.components()
            b = face.vertex(2).position.components()
        elif v_index == 1:
            #avg 0 and 2
            vec = face.edge(2).vector()
            a = face.vertex(0).position.components()
            b = face.vertex(2).position.components()
        else:
            #avg 0 and 1
            vec = face.edge(0).vector()
            a = face.vertex(0).position.components()
            b = face.vertex(1).position.components()
        #construct a purpendicular vector
        p_vec = vector(-vec[1], vec[0], vec[2]).neg()
        c = point((a[0] + b[0])/2, (a[1] + b[1])/2, (a[2] + b[2])/2)
        #add to mp of two verts
        pos = c.plus(p_vec)
        return pos

    def toBuffer(self):
        varray = []
        carray = []
        inf_edge_color = [1.0, .8, .8]
        for f in self.face:
            special_color = self.inf_face(f)
            for i in [0, 1, 2]:
                if special_color:
                    if i == (special_color-1):
                        position = self.get_inf_vert_pos(f, i)
                        varray.extend(position)
                        carray.extend(inf_edge_color)
                        # if self.leftmost.source == f.vertex(i):
                        #     print("WOAH leftmost src")
                        #     carray.extend([0.0, 1.0, 0.0])

                        # elif self.rightmost.source == f.vertex(i):
                        #     print("WOAH rightmost src")
                        #     carray.extend([0.0, 0.0, 1.0])
                        # else:
                        #     carray.extend(inf_edge_color)
                    else:
                        varray.extend(f.vertex(i).position.components())
                        carray.extend(f.vertex(i).color().components())
                        # if self.leftmost.source == f.vertex(i):
                        #     print("WOAH leftmost src")
                        #     carray.extend([0.0, 1.0, 0.0])

                        # elif self.rightmost.source == f.vertex(i):
                        #     print("WOAH rightmost src")
                        #     carray.extend([0.0, 0.0, 1.0])
                        # else:
                        #     carray.extend(f.vertex(i).color().components())
                else:
                    varray.extend(f.vertex(i).position.components())
                    carray.extend(f.vertex(i).color().components())
                    # if self.leftmost and self.rightmost:
                    #     if self.leftmost.source == f.vertex(i):
                    #         print("WOAH leftmost src")
                    #         carray.extend([0.0, 1.0, 0.0])
                    #     elif self.rightmost.source == f.vertex(i):
                    #         print("WOAH rightmost src")
                    #         carray.extend([0.0, 0.0, 1.0])
                    #     elif self.leftmost.next.source == f.vertex(i):
                    #         print("WOAH leftmost dest")
                    #         carray.extend([0.0, 1.0, 0.0])
                    #     elif self.rightmost.next.source == f.vertex(i):
                    #         print("WOAH rightmost dest")
                    #         carray.extend([0.0, 0.0, 1.0])
                    #     else:
                    #         carray.extend(f.vertex(i).color().components())
                    # else:
                    #     carray.extend(f.vertex(i).color().components())
        return (varray, carray)

    def tri_is_delaunay(self, circle):
        '''
        uses the sites of a voronoi diagram to test that a given circle does not 
        include any of the points
        return true if every vertex is NOT included in the circle
        '''
        for vertex in self.vertex:
            #using this if statement because it seems we have precision issues
            if vertex is not self.infv and vertex not in circle.csites():
                in_circle = circle.includes(vertex)
                if in_circle:
                    print("\t vertex {} v.x {} v.y {} included in circle {} with radius {}".format(vertex, vertex.position.x, vertex.position.y, circle, circle.r))
                    return False
        return True


    def get_convex_hull(self):
        '''
        '''
        leftmost = None
        rightmost = None
        ch_edges = []
        for e in self.infv.around():
            ch_edges.append(e.next)
            if not leftmost:
                leftmost = e.next
            elif e.next.source.position.x < leftmost.source.position.x:
                leftmost = e.next
            if not rightmost:
                rightmost = e.next
            elif e.next.source.position.x >= rightmost.source.position.x:
                rightmost = e.twin.next.next.twin
        self.leftmost = leftmost
        self.rightmost = rightmost
        return ch_edges

    def make_twins(self):
        '''
        makes sure that all of the edges in the triangulation have twins
        note that the only edges which should require twins should be on the convex hull
        '''
        new_faces = 0
        print("*** making edges twins ***")
        for edge_id, edge in self.edge.copy().items():
            print("Edge {}: Twin: {}".format(edge, edge.twin))
            if edge.twin is None:
                print("creating an infinite face")
                src = self.vertex[edge_id[1]]
                dest = self.vertex[edge_id[0]]
                face(src, dest, self.infv, self)
                new_faces += 1
        return new_faces

    def verify_delaunay(self):
        '''
        given a diagram (self) verify that it is, in fact, a delaunay triangulation
        this can be tested in two ways
        1: that every edge has a point free circle that goes through its endpoints
        2: that every face (triangle) has a circumcircle and it is point-free 
        '''
        inf_faces = self.make_twins()
        # set the vertex fan ordering
        for v in self.vertex:
            v.set_first_edge_ccw()
        delaunay = True
        print("*** Verify Property ***")
        print("# of vertices: {} infv: {} vertices: {}".format(len(self.vertex), self.infv, self.vertex))
        print("# of edges: {}".format(len(self.edge.items())))
        print("# of faces: {}, {} of which are infinite".format(len(self.face), inf_faces))
        for face in self.face:
            #we can use the circle to dict to check this
            #but let's just start by making our own circles
            #don't check the inclusion property on the faces with infinite vertices
            if not self.inf_face(face):
                c_witness = CircleWitness(face.vertex(0), face.vertex(1), face.vertex(2))
                res = self.tri_is_delaunay(c_witness)
                if not res:
                    delaunay = res
                print("\nTesting the delaunayhood of face: {} circle witness: {} result: {}".format(face, c_witness, res))
            else:
                print("This was an infinite face: {}".format(face))
        ch = self.get_convex_hull()
        print("\n *** CONVEX HULL ***")
        print("Convex hull is a(n) {}-gon".format(len(ch)))
        print("leftmost edge: {} src: {} dest: {}".format(self.leftmost, self.leftmost.source.position, self.leftmost.next.source.position))
        print("rightmost edge: {} src: {} dest: {}".format(self.rightmost, self.rightmost.source.position, self.rightmost.next.source.position))
        for edge in ch:
            print(edge)
        print("\n *** END CONVEX HULL ***")
        return delaunay

    #these shoudl probably be somewhere else
    @staticmethod
    def ccw(a, b, c):
        d = a.x * b.y * 1 + a.y * 1 * c.x + 1 * b.x * c.y - 1 * b.y * c.x - a.y * b.x * 1 - a.x * 1 * c.y
        print(d)
        return d

    @staticmethod 
    def leftOf(a, b, c):
        return Delaunay.ccw(a, b, c)

    @staticmethod
    def rightOf(a, b, c):
        return Delaunay.ccw(a, c, b)

    @staticmethod
    def get_lower_common_tangent(d1, d2):
        '''
        given two delaunay triangulations, return the lower common tangent between the two 
        '''
        ldi = d1.rightmost
        rdi = d2.leftmost

        while Delaunay.leftOf(rdi.source.position, ldi.source.position, ldi.next.source.position) > 0 or Delaunay.rightOf(ldi.source.position, rdi.next.source.position, rdi.source.position)>0:
            if Delaunay.leftOf(rdi.source.position, ldi.source.position, ldi.next.source.position) > 0:
                #get the next edge whose left side has the same face
                print("move ldi: {} to {}".format(ldi, ldi.twin.next.next.twin.next.next.twin))
                ldi = ldi.twin.next.next.twin.next.next.twin #next edge on the hull?
            elif Delaunay.rightOf(ldi.source.position, rdi.next.source.position, rdi.source.position) > 0: 
                print("move rdi: {} to {}".format(rdi, rdi.next.twin.next))
                rdi = rdi.next.twin.next
            else:
                print("huh")

        return ldi, rdi


    @staticmethod
    def merge_triangulations(t1, t2):
        '''
        given two adjacent triangulations, verify their delaunayhood and try to merge them
        '''
        d1 = t1.verify_delaunay()
        d2 = t2.verify_delaunay()

        if not (d1 and d2):
            print("These are not valid delaunay triangulations... we could not fix them up enough to merge them.")
            return False

        else:
            ldi, rdi = Delaunay.get_lower_common_tangent(t1, t2)
            print("lowest common tangent edges {} {}".format(ldi, rdi))
            print("ldi src: {} rdi src: {}".format(ldi.source.position, rdi.source.position))
            print("ldi dest: {} rdi dest: {}".format(ldi.next.source.position, rdi.next.source.position))



