import math
from circle import Circle, InvalidCircle, NotEmptyCircle, CircleAlreadyCreated

class Beach:
  #default bounds if we're using the opengl simulation
  bounds = {"xmin": -1.0, "xmax": 1.0, "ymin": -1.0, "ymax": 1.0}
  def __init__(self, site, scanline):
    self.directrix = scanline
    self.focus = site

  def intersect(self, beach):
    a = self.focus.x
    b = self.focus.y
    c = self.directrix.y

    #calculate intersection of two parabolas
    h = beach.focus.x
    j = beach.focus.y

    # breakpoints = []
    try:
      x1 = ((-1.0) * (math.sqrt((-b*c+b*j+c*c - c*j)*(a*a - 2.0*a*h + b*b - 2*b*j + h*h + j*j))) + a*c-a*j + b*h - c*h)/(b-j)
    except:
      x1 = min(a, h)
    try:
      x2 = ((math.sqrt((-b*c+b*j+c*c - c*j)*(a*a - 2.0*a*h + b*b - 2.0*b*j + h*h + j*j))) + a*c-a*j + b*h - c*h)/(b-j)
    except:
      x2 = min(a, h)

    if x1 > x2:
      return [x2, x1]
    else:
      return [x1, x2]

  def old_arceqn(self, x):
    a = self.focus.x
    b = self.focus.y
    c = self.directrix.y
    y = (1.0/(2.0*(b-c))) * ((x-a)*(x-a)) + (1.0/2.0)*(b+c)

    return y

  def arceqn(self, x):
    a = self.focus.x
    b = self.focus.y
    c = self.directrix.y
    verty = b - (self.focus.dist2scan / 2.0)
    y = (1.0/(2.0*(b-c))) * (((x-a)*(x-a)) + (b*b - c*c))

    return y

  def inv_arceqn(self):
    # y = y
    y = self.bounds["ymax"]
    a = self.focus.x
    b = self.focus.y
    c = self.directrix.y
    try:
      x1 = a + math.sqrt(-1.0*(b-c)*(b+c - 2.0*y))
      x2 = a - math.sqrt(-1.0*(b-c)*(b+c - 2.0*y))
      if x1 > x2:
        return x2, x1
      else:
        return x1, x2

    except:
      return a, a


  def update(self, bl, br):
    arcBuf = []
    cBuf = []
    c = self.focus.c

    if self.focus.y >= self.directrix.y:
      i = bl
      while i <= br:
        y = self.arceqn(i)
        cBuf.extend(c.components()) 
        arcBuf.extend([i, y, 0.0])
        i += .005
    return arcBuf, cBuf

  def toBuffer(self, bl, br):
    return self.update(bl, br)


class BeachNode:
  def __init__(self, beach, left=None, right=None, breakl=None, breakr=None):
    self.beach = beach
    self.circles = [] 
    self.x = beach.focus.x
    self.y = beach.focus.y
    if (breakl is None) and (breakr is None):
      self.breakl, self.breakr = beach.inv_arceqn()
    else:
      self.breakl = breakl
      self.breakr = breakr
    self.next = right
    self.prev = left


class BeachODBLL:
  def __init__(self, head=None, tail=None):
    self.head = head
    self.tail = tail
    self.beachBuf = []
    self.colorBuf = []
    self.to_remove = []


  def removeCircles(self, bn):
    '''given a beach node, remove all circle events associated with that node'''
    #note: the arc that disappears must be the oldest one
    for circle in bn.circles:
      if bn.next is not None:
        try:
          bn.next.circles.remove(circle)
        except:
          pass
        if bn.next.next is not None:
          try:
            bn.next.next.circles.remove(circle)
          except:
            pass
      if bn.prev is not None:
        try:
          bn.prev.circles.remove(circle)
        except:
          pass
        if bn.prev.prev is not None:
          try:
            bn.prev.prev.circles.remove(circle)
          except:
            pass

  def printDBL(self):
    pts = []
    ptr = self.head
    while ptr is not None:
      pts.append((ptr,ptr.x, ptr.breakl, ptr.breakr))
      ptr = ptr.next
    print(pts)

  def validateDBLL(self):
    ptr = self.head
    print("\n******STARTING: VALIDATE BEACHFRONT******")
    while ptr is not None:
      if ptr.prev is not None and ptr.prev.next is ptr:
        print("ptr.prev.next is ptr for {}".format(ptr))
      else:
        if ptr.prev is None and ptr is self.head:
          print("head for ptr{}".format(ptr))
        else:
          print("ptr.prev.next is NOT ptr for {}".format(ptr))
          print("ptr.prev.next is {}".format(ptr.prev.next))

      if ptr.next is not None and ptr.next.prev is ptr:
        print("ptr.next.prev is ptr for {}".format(ptr))
      else:
        if ptr.next is None and ptr is self.tail:
          print("tail for ptr{}".format(ptr))
          #to do: make sure this is self.tail
        else:
          print("ptr.next.prev is NOT ptr for {}".format(ptr))
          print("ptr.next.prev is {}".format(ptr.next.prev))
      ptr = ptr.next
    self.printDBL()
    print("******FINISHED: VALIDATE BEACHFRONT******\n")
    
  def addCircle(self, n1, n2, n3):
    circle_events = []
    newest = min(n1.y, n2.y, n3.y)
    scanline = n1.beach.directrix
    try:
      circle = Circle(n1.beach.focus, n2.beach.focus, n3.beach.focus)
      circle.update(scanline)
      #make sure the circle's lowest point is below the scanline (i.e, where we just added the site)
      #note that this isnt quite correct (e.g think abt case where we removed arc & are recomputing)
      print("adding a circle @cx {}, cy {}, low {}, dist2scan {})".format(circle.c.x, circle.c.y, circle.low.y, circle.dist2scan))
      print("circle.sites(): :{}".format([str(site) for site in circle.csites()]))
      n1.circles.append(circle)
      n2.circles.append(circle)
      n3.circles.append(circle)
      circle_events.append(circle)
    except InvalidCircle as IC:
      print("CIRCLE ERROR: Not a valid circle {}".format(str(IC)))
    except NotEmptyCircle as NEC:
      print("CIRCLE ERROR: Not an empty circle sites included {}".format(str(NEC)))
    except CircleAlreadyCreated as CAC:
      print("CIRCLE ERROR: Circle already created {}".format(str(CAC)))
    return circle_events

  #TO DO: insert does not account for degenerate case where the new site
  # is inserted exactly at the intersection of the sites to the right and left
  def insert(self, beach):
    # print("inserting")
    circle_events = []
    bn = BeachNode(beach)
    self.validateDBLL()
    print("inserting site @(x{}, y{}) bn{}".format(beach.focus.x, beach.focus.y, bn))
    #list is empty, insert the beach node
    if self.head is None:
      self.head = self.tail = bn
    #list is not empty, insert the beach node
    else:
      ptr = self.head

      #this is the leftmost breakpoint
      if bn.x <= ptr.breakl:
        #set the new breakpoints
        bn.breakr = bn.x
        bn.breakl = bn.x
        ptr.breakl = bn.x

        #update the links
        self.head = bn
        bn.next = ptr
        ptr.prev = bn

        #add a circle event if there are at least two sites to the right
        #don't need to check that they're all unique since we knoe bn != bn.next
        #and there's no way bn.next can equal bn.next.next
        if bn.next.next is not None:
          return self.addCircle(bn, bn.next, bn.next.next)

      else:
        while ptr is not None:
          #site is to the right of the left breakpoint and left of right breakpoint
          if (ptr.breakl <= bn.x) and (ptr.breakr >= bn.x):
            print("this is the node {}, bl = {}, br={} and  new site {}".format(ptr.x, ptr.breakl, ptr.breakr, bn.x))
            bn.breakl = bn.x
            bn.breakr = bn.x

            # rbn = BeachNode(ptr.beach, bn, ptr.next, bn.breakr, ptr.breakr)
            # if ptr.next:
            #   rbn.next.prev = rbn
            # bn.next = rbn
            # ptr.breakr = bn.breakl
            # bn.prev = ptr
            # ptr.next = bn

            #make a new node to the right if we need to
            pl, pr = ptr.beach.inv_arceqn()
            if bn.x > pl or bn.x < pr:
              rbn = BeachNode(ptr.beach, bn, ptr.next, bn.breakr, ptr.breakr)
              if ptr.next:
                rbn.next.prev = rbn
              bn.next = rbn

            else:
              bn.next = ptr.next

            ptr.breakr = bn.breakl
            bn.prev = ptr
            ptr.next = bn


            #add circle events
            #2 sites to the left
            if bn.prev and bn.prev.prev:
              circle_events.extend(self.addCircle(bn.prev.prev, bn.prev, bn))
            #we don't need to handle sites to left and right for bn

            #two sites to the right
            if bn.next and bn.next.next:
              circle_events.extend(self.addCircle(bn, bn.next, bn.next.next))

            if rbn:
              #two sites to the right
              if rbn.next and rbn.next.next:
                # print("two sites to the right")
                circle_events.extend(self.addCircle(rbn, rbn.next, rbn.next.next))

              if not rbn.next:
                self.tail = rbn

            self.validateDBLL()
            return circle_events
          else:
            #rightmost node
            if ptr.next is None:
              ptr.next = bn
              bn.prev = ptr
              bn.breakr = bn.x
              bn.breakl = bn.x
              ptr.breakr = bn.x
              self.tail = bn
              #add circle event to the left
              if bn.prev and bn.prev.prev:
                # print("two sites to the left")
                circle_events.extend(self.addCircle(bn.prev.prev, bn.prev, bn))
              return circle_events
            else:
              ptr = ptr.next


  def remove(self, ptr):
    #find the ptr
    #TO DO: add circle event if necessary
    print("removing site bn{} @(x{} y{}) with bl {} br {}".format(ptr, ptr.x, ptr.y, ptr.breakl, ptr.breakr))
    self.printDBL()
    circle_events = []
    cur = self.head
    while cur is not None:
      if cur is ptr:
        #remove circle events associated with this node
        if len(cur.circles) > 0:
          self.removeCircles(cur)
        #special case where we remove the first node, we know it's not the only node
        if cur is self.head:
          self.head = cur.next
          cur.next.prev = None
          #update circle events
          if cur.next and cur.next.next and cur.next.next.next:
            circle_events.extend(self.addCircle(cur.next, cur.next.next, cur.next.next.next))
          self.validateDBLL()
          return circle_events
        if cur.prev is not None:
          cur.prev.next = cur.next
        if cur.next is not None:
          cur.next.prev = cur.prev
          if cur.next.next is not None:
            circle_events.extend(self.addCircle(cur.prev, cur.next, cur.next.next))
          if cur.prev.prev is not None:
            circle_events.extend(self.addCircle(cur.prev.prev, cur.prev, cur.next))
          self.validateDBLL()
          return circle_events
        else:
          self.tail = cur.prev
      cur = cur.next

  def update(self, ptr):
    if ptr is not None:
      if (ptr.next is None) and (ptr is self.head):
        ptr.breakl, ptr.breakr = ptr.beach.inv_arceqn()
      else:
      #update right breakpoint of ptr and left bkpt of ptr.next
        if ptr.next is not None:
          bkpts = ptr.beach.intersect(ptr.next.beach)
          if ptr.prev is None:
            ptr.breakl, tmp = ptr.beach.inv_arceqn()
            ptr.breakl = min(ptr.breakl, min(bkpts))
          if ptr.y >= ptr.next.y:
            bpt = min(bkpts)
            ptr.breakr = bpt
            ptr.next.breakl = bpt
          else:
            bpt = max(bkpts)
            ptr.breakr = bpt
            ptr.next.breakl = bpt

          if (ptr.breakr < ptr.breakl):
            if (ptr.breakl > -1.0) and (ptr.breakr > -1.0):
              print("URGENT: should remove: bn {} ptr.x {} bl:{} br:{}".format(ptr, ptr.x, ptr.breakl, ptr.breakr))

            else:
              print("OUT OF BOUNDS: should remove: bn {} ptr.x {} bl:{} br:{}".format(ptr, ptr.x, ptr.breakl, ptr.breakr))
            self.printDBL()
            # self.remove(ptr)
            # self.printDBL()
            # pass
          self.update(ptr.next)
        else:
          tmp, ptr.breakr = ptr.beach.inv_arceqn()
          return


  def find_by_x(self, circle):
    ''' given a point (presumable circle.low) and an beachfront, 
    return the arc directly above it'''
    cur = self.head
    while cur is not None:
      if circle.low.x >= cur.breakl and circle.low.x <= cur.breakr:
        #remove beachfront associated with rightmost site
        if math.fabs(math.fabs(circle.low.x) - math.fabs(cur.breakl)) > .005 and math.fabs(math.fabs(circle.low.x) - math.fabs(cur.breakr)) > .005:
          print(math.fabs(math.fabs(circle.low.x) - math.fabs(cur.breakl)))
          print(math.fabs(math.fabs(circle.low.x) - math.fabs(cur.breakr)))
          # print("cur.breakl {} br{}".format(cur.breakl, cur.breakr))
          # print("cur{} cur dist {}".format(cur, dist))
          if cur.prev and cur.prev.x != cur.prev.breakl and cur.prev.x != cur.prev.breakr:
            dist = math.fabs(cur.prev.breakl - cur.prev.breakr)
            # print("cur{} cur.prev dist {}".format(cur.prev, dist))
          if cur.next and cur.next.x != cur.next.breakl and cur.next.x != cur.next.breakr:
            dist = math.fabs(cur.next.breakl - cur.next.breakr)
            # print("cur {} cur.next dist {}".format(cur.next, dist))
          return cur
        else:
          arcs = {}
          dist = math.fabs(cur.breakl - cur.breakr)
          arcs[dist] = cur
          print(math.fabs(math.fabs(circle.low.x) - math.fabs(cur.breakl)))
          print(math.fabs(math.fabs(circle.low.x) - math.fabs(cur.breakr)))
          # print("cur.breakl {} br{}".format(cur.breakl, cur.breakr))
          # print("cur{} cur dist {}".format(cur, dist))
          if cur.prev and cur.prev.x != cur.prev.breakl and cur.prev.x != cur.prev.breakr:
            dist = math.fabs(cur.prev.breakl - cur.prev.breakr)
            arcs[dist] = cur.prev
            # print("cur{} cur.prev dist {}".format(cur.prev, dist))
          if cur.next and cur.next.x != cur.next.breakl and cur.next.x != cur.next.breakr:
            dist = math.fabs(cur.next.breakl - cur.next.breakr)
            arcs[dist] = cur.next
            # print("cur {} cur.next dist {}".format(cur.next, dist))

          mindist = min(arcs.keys())
          # print("mindist {}".format(mindist))
          return arcs[mindist]
      else:
        cur = cur.next

  def getHead(self):
    return self.head

  def toBuffer(self):
    self.update(self.head)
    self.beachBuf = []
    self.colorBuf = []
    ptr = self.head
    while ptr is not None:
      b, c = ptr.beach.toBuffer(ptr.breakl, ptr.breakr)
      self.beachBuf.extend(b)
      self.colorBuf.extend(c)
      ptr = ptr.next
    return self.beachBuf, self.colorBuf



