#@ifjorissen 
#3.10.16
#red black tree

#constants
RED = "RED"
BLACK = "BLACK"
EPSILON = 1.0e-8

class LeafNode:
    def __init__(self, data = None):
        self.color = BLACK
        self = None

class Node:
    def __init__(self, data, color=RED, left=None, right=None, parent=None):
        # tree info
        self.color = color
        self.left = left
        self.right = right
        self.parent = parent

        #data
        self.data = data

    def __repr__(self):
        return "data:{}; color:{};".format(self.data, self.color)


    def __lt__(self, other):
        if self.data < other.data:
            return True
        else:
            return False

    def __gt__(self, other):
        if self.data > other.data:
            return True
        else:
            return False

    def __eq__(self, other):
        if self.data == other.data:
            return True
        else:
            return False


class RBTree:
    '''
    rules of the game:
    1. every node is either red or black
    2. the root is black
    3. every leaf node is black
    4. if a node is red, then both its children are black
    5. for each node, all (simple) paths from the node to leaves 
       contain the same number of black nodes
    '''

    def __init__(self, root=None, create_node=Node):
        '''
        initialize the empty tree with a single leaf node,
        satisfying the property that the root is black and the leaf is black
        '''
        self.create_node = create_node
        self.NIL = create_node(None, BLACK)

        if root:
            self.root = root
        else:
            self.root = self.NIL

    def _right_rotate(self, node):
        '''
              a                 b
            /   \             /   \
           b     c    ===>   e     a 
          / \                     / \
         e   f                   f   c

         [e,b,f,a,c]         [e,b,f,a,c]
        '''

        # print("right rotation")

        x = node.left  #b, in example
        node.left =  x.right  #set a's left child to f

        if x.right is not self.NIL:
            x.right.parent = node  #update f's parent to a

        x.parent = node.parent #update b's parent to whatever a's parent was

        if node.parent is self.NIL:  #case where the parent of node is self.NIL, indicating the root of the tree
            self.root = x
        elif node is node.parent.left:
            node.parent.left = x
        else:
            node.parent.right = x

        x.right = node #update b's right child to a
        node.parent = x #update a's parent to b

    def _left_rotate(self, node):
        '''
              a                 b
            /   \             /   \
           b     c    <===   e     a 
          / \                     / \
         e   f                   f   c

         [e,b,f,a,c]         [e,b,f,a,c]
        '''
        # print("left rotation")
        x = node.right
        node.right = x.left

        if x.left is not self.NIL:
            x.left.parent = node

        x.parent = node.parent

        if node.parent is self.NIL:
            self.root = x
        elif node is node.parent.left:
            node.parent.left = x
        else:
            node.parent.right = x

        x.left = node
        node.parent = x


    def _delete_fixup(self, sol_node):
        '''
        fixes the following 3 cases (called when the node removed was BLACK):
        1. the node moved (prob_node) was the root and a red child became the new root, violating property 2
        2. case where sol_node is red and so is its parent, violating property 4
        3. prob_node was moved in the tree, and might have caused a violation of property 5
        '''
        while sol_node is not self.root and sol_node.color is BLACK:
            if sol_node is sol_node.parent.left:
                sibling = sol_node.parent.right
                #case 1: sol_node's sibling is red
                if sibling.color is RED:
                    sibling.color = BLACK #push (extra) black down
                    sol_node.parent.color = RED
                    self._left_rotate(sol_node.parent)
                    sibling = sol_node.parent.right
                #case 2: make sure we don't violate property 2
                if sibling.left.color is BLACK and sibling.right.color is BLACK:
                    sibling.color = RED
                    sol_node = sol_node.parent
                #case 3: sol_node's sibling is black, and has a red left child and black right child
                else:
                    if sibling.right.color is BLACK:
                        sibling.left.color = BLACK
                        sibling.color = RED
                        self._right_rotate(sibling)
                        sibling = sol_node.parent.right

                    sibling.color = sol_node.parent.color
                    sol_node.parent.color = BLACK
                    sibling.right.color = BLACK
                    self._left_rotate(sol_node.parent)
                    sol_node = self.root
            else:
                sibling = sol_node.parent.left
                #case 1: sol_node's sibling is red
                if sibling.color is RED:
                    sibling.color = BLACK #push (extra) black down
                    sol_node.parent.color = RED
                    self._right_rotate(sol_node.parent)
                    sibling = sol_node.parent.left
                #case 2: make sure we don't violate property 2
                if sibling.left.color is BLACK and sibling.right.color is BLACK:
                    sibling.color = RED
                    sol_node = sol_node.parent
                #case 3: sol_node's sibling is black, and has a red left child and black right child
                else:
                    if sibling.left.color is BLACK:
                        sibling.right.color = BLACK
                        sibling.color = RED
                        self._left_rotate(sibling)
                        sibling = sol_node.parent.left
                #case 4: sol node's sibling is black and has a red right child
                    sibling.color = sol_node.parent.color
                    sol_node.parent.color = BLACK
                    sibling.left.color = BLACK
                    self._right_rotate(sol_node.parent)
                    sol_node = self.root
        sol_node.color = BLACK



    def _tree_min(self, node_a):
        '''
        given a node return the minimum node of that subtree
        '''
        while node_a.left is not self.NIL:
            node_a = node_a.left
        return node_a

    def _transplant(self, node_a, node_b):
        '''
        given nodes a and b, make b the parent of a's subtree
        '''
        if node_a.parent is self.NIL:
            self.root = node_b
        elif node_a is node_a.parent.left:
            node_a.parent.left = node_b
        else:
            node_a.parent.right = node_b
        node_b.parent = node_a.parent


    def delete(self, del_node):
        '''
        prob_node: maintains either the node removed or the node moved in the tree
        sol_node: the node which takes prob_node's place
        del_node: the node we removed from the tree
        '''
        prob_node = del_node #potentially problematic node, to be replaced by sol_node
        pn_col = prob_node.color

        print("delete::{}".format(del_node))

        #removing the last node in the tree
        if del_node is self.root and del_node.left is self.NIL and del_node.right is self.NIL:
            self.root = self.NIL
            print("removing the last node in the tree!")

        #(n)one child: move the subtree to the del_node.right to del_node
        elif del_node.left is self.NIL:
            sol_node = del_node.right #solution node ==> will assume prob_node's position
            self._transplant(del_node, del_node.right)

        #(n)one child: move the subtree to the del_node.left to del_node    
        elif del_node.right is self.NIL:

            sol_node = del_node.left
            self._transplant(del_node, del_node.left)

        #two children
        else:
            #get the minimum of the right subtree
            prob_node = self._tree_min(del_node.right)
            pn_col = prob_node.color
            sol_node = prob_node.right

            if prob_node.parent is del_node: 
                sol_node.parent = prob_node
            else:
                # transplant, detach, and (re)attach the right subtree of the node we're removing (del_node)
                self._transplant(prob_node, prob_node.right)
                prob_node.right = del_node.right
                prob_node.right.parent = prob_node
            #transpant, detach and (re)attach the left subtree of the node we're removing
            self._transplant(del_node, prob_node)
            prob_node.left = del_node.left
            prob_node.left.parent = prob_node
            prob_node.color = del_node.color

        #fixup if we removed a black node
        if pn_col is BLACK and not self.is_empty():
            self._delete_fixup(sol_node)

    def _insert_fixup(self, new_node):
        '''
        insertion can violate 2 properties:
        2. root node is no longer black ==> occurs when new_node is the root
        4. children of red nodes are no longer black ==> occurs when new_node's parent is red

        While loop:
        1. new_node is always red
        2. if new_node.parent is the root, it is black
        3. if the tree is in violation it violates one of 2 or 4.
        '''
        while new_node.parent.color is RED:
            if new_node.parent is new_node.parent.parent.left:
                r_uncle = new_node.parent.parent.right
                if r_uncle.color is RED:
                    new_node.parent.color = BLACK
                    r_uncle.color = BLACK
                    new_node.parent.parent.color = RED
                    new_node = new_node.parent.parent
                else:
                    if new_node is new_node.parent.right: 
                        new_node = new_node.parent
                        self._left_rotate(new_node)
                    new_node.parent.color = BLACK
                    new_node.parent.parent.color = RED
                    self._right_rotate(new_node.parent.parent)
            else:
                l_uncle = new_node.parent.parent.left
                if l_uncle.color is RED:
                    new_node.parent.color = BLACK
                    l_uncle.color = BLACK
                    new_node.parent.parent.color = RED
                    new_node = new_node.parent.parent
                else:
                    if new_node is new_node.parent.left:
                        new_node = new_node.parent
                        self._right_rotate(new_node)
                    new_node.parent.color = BLACK
                    new_node.parent.parent.color = RED
                    self._left_rotate(new_node.parent.parent)

        #make sure the root is black
        self.root.color = BLACK

    def insert(self, data, after=None, root_node=None):
        '''
        given a value, create a node and insert it as "usual"
        '''
        parent = self.NIL
        new_node = self.create_node(data, color=RED, left=self.NIL, right=self.NIL, parent=self.NIL, next=self.NIL, prev=self.NIL)
        # print("creating a new node with data type {} and node type: {}".format(type(data), type(new_node)))
        # print(new_node)
        if not root_node:
            cur = self.root
        else:
            cur = root_node

        if after and after is not self.NIL:
            # print("inserting new_node {} after: {}".format(new_node, after)) 
            new_node.prev = after
            new_node.next = after.next
            if after.next:
                after.next.prev = new_node
            after.next = new_node
            if after.right is not self.NIL:
                after = after.right
                while after.left is not self.NIL: 
                    after = after.left
                after.left = new_node
            else:
                after.right = new_node
            new_node.parent = after
        else:
            # find the right location for this node
            while cur is not self.NIL:
                parent = cur
                if new_node < cur:
                    cur = cur.left
                else:
                    cur = cur.right

            #case where we are at the root
            if parent is self.NIL:
                self.root = new_node

            #other cases where we aren't at the root and need figure out whether 
            #new_node is left or right child
            elif new_node < parent:
                parent.left = new_node
            else:
                parent.right = new_node
            new_node.parent = parent

        #now fix everything up & restore red black properties
        self._insert_fixup(new_node)
        return new_node

    def search(self, data, root_node=None):
        '''
        given a value try to return the node with that value
        '''
        if not root_node:
            root_node = self.root
        cur = root_node
        while cur is not self.NIL:
            if cur is data:
                return cur
            elif data < cur:
                cur = cur.left
            else:
                cur = cur.right
        return self.NIL

    def search_coarse_val(self, val, root_node=None):
        '''
        particular to the beachfront implementation, kind of
        given a value, return the internal node whose breakpoint is as close
        as possible (and less than) this value
        '''
        if self.is_empty():
            return self.NIL

        if not root_node:
            root_node = self.root

        if (root_node - val) > EPSILON:
            if root_node.left is not self.NIL:
                return self.search_val(val, root_node.left)
            else:
                return root_node

        elif (val - root_node.next) > EPSILON: 
            if root_node.right is not self.NIL:
                return self.search_val(val, root_node.right)
            else:
                return root_node
        else:
            return root_node



    def search_val(self, val, root_node=None):
        '''
        particular to the beachfront implementation, kind of
        given a value, return the internal node whose breakpoint is as close
        as possible (and less than) this value

        return the arc which will be the predecessor to this arc
        return the arc which will be the successor to this arc
        '''

        if self.is_empty():
            return self.NIL

        if not root_node:
            root_node = self.root

        cur = root_node
        parent = cur.parent

        while cur is not self.NIL:
            parent = cur
            if val < cur:
                cur = cur.left

            elif val > cur:
                cur = cur.right

        return parent




        # if val < root_node:
        #     if root_node.left is not self.NIL:
        #         return self.search_val(val, root_node.left)
        #     else:
        #         return root_node

        # elif val > root_node: 
        #     if root_node.right is not self.NIL:
        #         return self.search_val(val, root_node.right)
        #     else:
        #         return root_node
        # else:
        #     return root_node


    def remove(self, data, root_node=None):
        if not root_node:
            root_node = self.root

        del_node = self.search(data)
        if del_node:
            self.delete(del_node)
        else:
            print("Node with {} was not in tree".format(data))


    def check_rb(self, root_node=None):
        '''
        make sure this is a valid RB-tree
        '''
        if self.is_empty():
            return 0

        if not root_node:
            root_node = self.root

        elif root_node is self.NIL:
            return 1

        ln = root_node.left
        rn = root_node.right

        #make sure children aren't red if this node is red
        if root_node.color is RED:
            if (ln.color is RED) or (rn.color is RED):
                print("RED violation. node {}; node.left {}; node.right{}", root_node, ln, rn)
                return 0

        #recursive call to get the height of the subtrees
        lh = self.check_rb(ln)
        rh = self.check_rb(rn)

        #make sure this is a valid binary search (sub)tree
        if (ln is not self.NIL and ln > root_node) or (rn is not self.NIL and rn < root_node):
            print("Invalid binary search tree")
            return 0

        #make sure there hasn't been a black violation
        if (lh is not 0) and (rh is not 0) and (lh != rh):
            print("BLACK violation")
            return 0

        #get the blackheight of this subtree
        if (lh is not 0) and (rh is not 0):
            if root_node.color is RED:
                return lh
            else:
                return lh + 1
        else:
            return 0

    #for ease of use
    def left_sibling(self, left_node):
        pass

    def right_sibling(self, left_node):
        pass



    #presentation & info funcs
    def count_internal_nodes(self):
        pass

    def black_height(self):
        pass

    def inorder(self, root_node=None):
        if self.is_empty():
            return []

        if not root_node:
            root_node = self.root

        if root_node is self.NIL:
            return []
        else:
            l_tree = self.inorder(root_node.left)
            r_tree = self.inorder(root_node.right)

            return l_tree + [root_node] + r_tree 

    def internal_leaves(self, root_node=None):
        if self.is_empty():
            return []

        if not root_node:
            root_node = self.root

        if root_node.left is self.NIL and root_node.right is self.NIL:
            return [root_node]

        else:
            l_tree = self.internal_leaves(root_node.left)
            r_tree = self.internal_leaves(root_node.right)

            return l_tree + r_tree


    def level_order(self, root_node=None):
        if self.is_empty():
            return []

        if not root_node:
            root_node = self.root

        if root_node is self.NIL:
            return []

    def is_empty(self):
        if self.root is self.NIL:
            return True
        else:
            return False

    def postorder(self):
        pass

    def preorder(self):
        pass

    def __repr__(self):
        return "beachfront (inorder): {}".format(self.inorder())    