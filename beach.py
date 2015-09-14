import math

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
      x2 = ((math.sqrt((-b*c+b*j+c*c - c*j)*(a*a - 2*a*h + b*b - 2*b*j + h*h + j*j))) + a*c-a*j + b*h - c*h)/(b-j)
      print("breakpoints")
      if x1 > x2:
        return [max(-1.0, x2), min(1.0, x1)]
      else:
        return [max(-1.0, x1), min(1.0, x2)]
    except:
      print("error, but we'll keep going")
      return [a, a]

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
        return x2, x1
      else:
        return x1, x2

    except:
      return [a, a]


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
  def __init__(self, beach, right=None, left=None, breakl=None, breakr=None):
    self.beach = beach
    self.x = beach.focus.x
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

  def insert(self, beach):
    print("inserting")
    bn = BeachNode(beach)
    #list is empty, insert the beach node
    if self.head is None:
      self.head = self.tail = bn
    #list is not empty, insert the beach node
    else:
      ptr = self.head
      print("stats: ")
      print(ptr.breakl)
      print(ptr.breakr)
      print(bn.x)

      #this is the leftmost breakpoint
      if bn.x <= ptr.breakl:
        # bkpts = bn.beach.intersect(ptr.beach)
        # bn.breakl, tmp = bn.beach.inv_arceqn()
        # bn.breakr = bkpts[1]
        # ptr.breakl = bkpts[1]

        #set the new breakpoints
        bn.breakr = bn.x
        bn.breakl = bn.x
        ptr.breakl = bn.x

        #update the links
        bn.next = ptr
        ptr.prev = bn
        self.head = bn
      else:
        while ptr is not None:
          # if ptr.next is not None:
          #site is to the right of the left breakpoint and left of right breakpoint
            if (ptr.breakl <= bn.x) and (ptr.breakr >= bn.x):
              print("this is the node")
              bn.breakl = bn.x
              bn.breakr = bn.x

              #make a new node to the right
              rbn = BeachNode(ptr.beach, ptr.next, bn, bn.breakr, ptr.breakr)
              ptr.breakr = bn.breakl
              bn.next = rbn
              bn.prev = ptr
              ptr.next = bn

              # bkpts = bn.beach.intersect(ptr.beach)
              # bn.breakl = bkpts[0]
              # bn.breakr = bkpts[1]
              #simplest case, bn.breakr < ptr.breakr, and same for breakl
              # if bn.breakl >= ptr.breakl:
              #   bn.next = ptr.next
              #   bn.prev = ptr
              #   ptr.next = bn
              #   if bn.breakr < ptr.breakr:
              #     rbn = BeachNode(ptr.beach, bn.next, bn, bn.breakr, ptr.breakr)
              #     bn.next = rbn
              #     ptr.breakr = bn.breakl
              #     if rbn.next is not None:
              #       rbn.next.prev = rbn
              #     else:
              #       self.tail = rbn
              #   else:
              #     ptr.breakr = bn.breakl
              #     if bn.next is not None:
              #       bn.next.prev = bn
              #     else:
              #       self.tail = bn
              # else:
              #   print("wth")
            else:
              if ptr.next is None:
                ptr.next = bn
                bn.prev = ptr
                bn.breakr = bn.x
                bn.breakl = bn.x
                # bkpts = ptr.beach.intersect(bn.beach)
                # ptr.breakr = bkpts[1]
                # bn.breakl = bkpts[1]
                self.tail = bn

              else:
                ptr = ptr.next

          #this is the rightmost breakpoint
          # else:
          #   ptr.next = bn
          #   bn.prev = ptr
          #   bn.breakr = bn.x
          #   bn.breakl = bn.x
          #   # bkpts = ptr.beach.intersect(bn.beach)
          #   # ptr.breakr = bkpts[1]
          #   # bn.breakl = bkpts[1]
          #   self.tail = bn
          #   return



  def remove(self, ptr):
    print("gotta remove this {}".format(ptr))
    #find the ptr
    cur = self.head
    while cur is not None:
      if cur is ptr:
        if cur.prev is not None:
          cur.prev.next = cur.next
          cur.next.prev = cur.prev
        else:
          self.head = cur.next
          cur.next.prev = None
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
      print("update")
      self.printDBL()
      # print(ptr.x)
      # print(ptr.breakl)
      # print(ptr.breakr)
      if (ptr.next is None) and (ptr is self.head):
        print("lonely {}".format(ptr.x))
        ptr.breakl, ptr.breakr = ptr.beach.inv_arceqn()
      else:
      #update right breakpoint of ptr and left bkpt of ptr.next
        if ptr.next is not None:
          print("something next {}".format(ptr.x))
          if ptr.prev is None:
            ptr.breakl, tmp = ptr.beach.inv_arceqn()

          bkpts = ptr.beach.intersect(ptr.next.beach)
          #THESE CONDITIONS ARE WRONG, BUT CLOSE
          if ptr.breakr < ptr.x:    
            ptr.breakr = bkpts[0]
            ptr.next.breakl = bkpts[0]
          else:
            ptr.breakr = bkpts[1]
            ptr.next.breakl = bkpts[1]
          # if ptr.next.breakl > ptr.next.breakr:
          #   self.remove(ptr)
          self.update(ptr.next)
        else:
          print("nothing next {}".format(ptr.x))
          tmp, ptr.breakr = ptr.beach.inv_arceqn()
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



