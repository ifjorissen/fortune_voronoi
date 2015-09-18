import math
from circle import Circle, InvalidCircle

class Beach:
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
      x1 = ((-1) * (math.sqrt((-b*c+b*j+c*c - c*j)*(a*a - 2*a*h + b*b - 2*b*j + h*h + j*j))) + a*c-a*j + b*h - c*h)/(b-j)
    except:
      x1 = min(a, h)
    try:
      x2 = ((math.sqrt((-b*c+b*j+c*c - c*j)*(a*a - 2*a*h + b*b - 2*b*j + h*h + j*j))) + a*c-a*j + b*h - c*h)/(b-j)
    except:
      x2 = min(a, h)

    if x1 > x2:
      return [max(-1.0, x2), min(1.0, x1)]
    else:
      return [max(-1.0, x1), min(1.0, x2)]

    #return the breakpoint [inner, outer]
    #four cases
    # if (x1 >= h) and (x1 <= a):
    #   return [x1, x2]

    if (x1 >= a) and (x1 <= h):
      return [x1, x2]

    else:
      return [x2, x1]

    # elif (x2 >= h) and (x2 <= a):
    #   return [x2, x1]

    # elif (x2 >= a) and (x2 <= h):
    #   return [x2, x1]

    # else:
    #   print("we've got a problem a:{} h:{} x1:{} x2:{}".format(a, h, x1, x2))


    # print(x1)
    # print(x2)
    # if (x1 >= h) and (x1 <= a):
    #   print("x1 inner bkpt")
    #   breakpoints = [x1, x2]

    # elif (x2 >= h) and (x2 <= a):
    #   print("x2 inner bkpt")
    #   breakpoints = [x2, x1]
    # else:
    #   print("??")
    #   breakpoints = [x1, x2]
      # if x1 > x2:
      #   print(" x1 > x2 uh?")
      #   breakpoints = [x2, 1.0]
      # else:
      #   print("x1 <= x2")
      #   breakpoints = [x1, x2]

      #find the breakpoints for y=1
    # return breakpoints
  def leftBreakpoint(self, beach):
    #return the left breakpoint of the adjacent beach
    if beach.focus.y is self.directrix.y:
      return beach.focus.y

    if self.focus.y is self.directrix.y:
      return self.focus.y



  def rightBreakpoint(self, beach):
    #return to right breakpoint of self
    return self.leftBreakpoint(beach)

  def old_arceqn(self, x):
    a = self.focus.x
    b = self.focus.y
    c = self.directrix.y
    # verty = b - (self.focus.dist2scan / 2.0)
    y = (1.0/(2.0*(b-c))) * ((x-a)*(x-a)) + (1.0/2.0)*(b+c)

    return y

  def arceqn(self, x):
    a = self.focus.x
    b = self.focus.y
    c = self.directrix.y
    verty = b - (self.focus.dist2scan / 2.0)
    y = (1.0/(2.0*(b-c))) * (((x-a)*(x-a)) + (b*b - c*c))

    return y

  def inv_arceqn(self, y=1.0):
    # y = y
    a = self.focus.x
    b = self.focus.y
    c = self.directrix.y
    try:
      x1 = a + math.sqrt(-1.0*(b-c)*(b+c - 2.0*y))
      x2 = a - math.sqrt(-1.0*(b-c)*(b+c - 2.0*y))
      if x1 > x2:
        return max(-1.0, x2), min(1.0, x1)
      else:
        return max(-1.0, x1), min(1.0, x2)

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
        i += .01
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

  def find_by_x(self, point):
    ''' given a point (presumable circle.low) and an beachfront, 
    return the arc directly above it'''
    cur = self.head
    while cur is not None:
      if point.x >= cur.breakl and point.x <= cur.breakr:
        return cur
      else:
        cur = cur.next

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
    
  def addCircle(self, n1, n2, n3):
    circle_events = []
    newest = min(n1.y, n2.y, n3.y)
    try:
      circle = Circle(n1.beach.focus, n2.beach.focus, n3.beach.focus)
        #make sure the circle's lowest point is below the scanline (i.e, where we just added the site)
        #note that this isnt quite correct (e.g think abt case where we removed arc & are recomputing)
      if (circle.low.y < newest) and (circle.low.y > -1.0) and (circle.r < 2.0):
        n1.circles.append(circle)
        n2.circles.append(circle)
        n3.circles.append(circle)
        circle_events.append(circle)
    except InvalidCircle as IC:
      print("Not a valid circle {}".format(IC.sites))
    return circle_events

  #TO DO: insert does not account for degenerate case where the new site
  # is inserted exactly at the intersection of the sites to the right and left
  def insert(self, beach):
    # print("inserting")
    circle_events = []
    bn = BeachNode(beach)
    #list is empty, insert the beach node
    if self.head is None:
      self.head = self.tail = bn
    #list is not empty, insert the beach node
    else:
      ptr = self.head
      # print("stats: ")
      # print(ptr.breakl)
      # print(ptr.breakr)
      # print(bn.x)

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
            # print("this is the node {}, bl = {}, br={} and  new site {}".format(ptr.x, ptr.breakl, ptr.breakr, bn.x))
            bn.breakl = bn.x
            bn.breakr = bn.x

            #make a new node to the right
            rbn = BeachNode(ptr.beach, bn, ptr.next, bn.breakr, ptr.breakr)
            ptr.breakr = bn.breakl
            bn.next = rbn
            bn.prev = ptr
            ptr.next = bn

            #add circle events
            #2 sites to the left
            if bn.prev and bn.prev.prev:
              # print("two sites to the left")
              circle_events.extend(self.addCircle(bn.prev.prev, bn.prev, bn))
            #we don't need to handle sites to left and right for bn

            #two sites to the right
            if bn.next and bn.next.next:
              # print("two sites to the right")
              circle_events.extend(self.addCircle(bn, bn.next, bn.next.next))

            # do the same for rbn
            # don't need to handle two sites to the left case
            #site to the left and right
            # if rbn.prev and rbn.next:
            #   print("two sites to the right")
            #   circle_events.extend(self.addCircle(rbn.prev, rbn, rbn.next))

            #two sites to the right
            if rbn.next and rbn.next.next:
              # print("two sites to the right")
              circle_events.extend(self.addCircle(rbn, rbn.next, rbn.next.next))

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
    # print("gotta remove this {}".format(ptr))
    # print("ptr.breakl {} breakr {} x {}".format(ptr.breakl, ptr.breakr, ptr.x))
    #find the ptr
    #TO DO: add circle event if necessary
    circle_events = []
    cur = self.head
    while cur is not None:
      if cur is ptr:
        if len(cur.circles) > 0:
          self.removeCircles(ptr)
          # print("arc is disappearing, but there are circle events involved")
          # print([c.c.y for c in ptr.circles])
        if cur.prev is not None:
          cur.prev.next = cur.next
          if cur.next:
            cur.next.prev = cur.prev
            if cur.next.next:
              circle_events.extend(self.addCircle(cur.prev, cur.next, cur.next.next))
            if cur.prev.prev:
              circle_events.extend(self.addCircle(cur.prev.prev, cur.prev, cur.next))
            return circle_events
        else:
          #remove the first node
          self.head = cur.next
          cur.next.prev = None
          #update circle events
          if cur.next and cur.next.next and cur.next.next.next:
            self.addCircle(cur.next, cur.next.next, cur.next.next.next)
          return circle_events
      cur = cur.next

  def printDBL(self):
    pts = []
    ptr = self.head
    while ptr is not None:
      pts.append(ptr.x)
      ptr = ptr.next
    print(pts)

  def update(self, ptr):
    if ptr is not None:
      # print("update")
      # self.printDBL()
      if (ptr.next is None) and (ptr is self.head):
        # print("ptr {}".format(ptr.x))
        ptr.breakl, ptr.breakr = ptr.beach.inv_arceqn()
        # print(ptr.breakl)
        # print(ptr.breakr)
      else:
      #update right breakpoint of ptr and left bkpt of ptr.next
        if ptr.next is not None:
          if ptr.prev is None:
            # print("ptr.prev is none: {}".format(ptr.x))
            ptr.breakl, tmp = ptr.beach.inv_arceqn()

          # ptr.breakr = ptr.beach.rightBreakpoint(ptr.next.beach)
          bkpts = ptr.beach.intersect(ptr.next.beach)
          if ptr.y > ptr.next.y:
            bpt = min(bkpts)
            ptr.breakr = bpt
            ptr.next.breakl = bpt
          else:
            bpt = max(bkpts)
            ptr.breakr = bpt
            ptr.next.breakl = bpt

          if(ptr.breakr < ptr.breakl) or (ptr.breakr == ptr.breakl == 1.0) or (ptr.breakr == ptr.breakl == -1.0):
            # print("we should be removing this")
            self.remove(ptr)
          # print("ptr.x {} bl:{} br:{}".format(ptr.x, ptr.breakl, ptr.breakr))
          self.update(ptr.next)
        else:
          tmp, ptr.breakr = ptr.beach.inv_arceqn()
          # print("last {} tmp: {} bl:{} br:{}".format(ptr.x, tmp, ptr.breakl, ptr.breakr))
          if(ptr.breakr < ptr.breakl) or (ptr.breakr == ptr.breakl == 1.0) or (ptr.breakr == ptr.breakl == -1.0):
            # print("we should be removing this...")
            self.remove(ptr)
          return

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



