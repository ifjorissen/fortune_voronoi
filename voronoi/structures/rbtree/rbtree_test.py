
from rbtree import *


def test_rb():
  '''
  some crappy seat of the pants tests for this rb tree
  '''
  
  print("making tree")
  tree = RBTree()

  for i in range(1,10):
    tree.insert(i)

  order = tree.inorder()
  print(order)
  res = tree.check_rb()
  print("RB Height (invalid if 0): {}\n".format(res))


  tree.remove(1)
  order = tree.inorder()
  print(order)
  res = tree.check_rb()
  print("RB Height (invalid if 0): {}\n".format(res))

  tree.remove(5)
  order = tree.inorder()
  print(order)
  res = tree.check_rb()
  print("RB Height (invalid if 0): {}\n".format(res))

  tree.remove(9)
  order = tree.inorder()
  print(order)
  res = tree.check_rb()
  print("RB Height (invalid if 0): {}\n".format(res))

  tree.remove(6)
  order = tree.inorder()
  print(order)
  res = tree.check_rb()
  print("RB Height (invalid if 0): {}\n".format(res))

  tree.remove(3)
  order = tree.inorder()
  print(order)
  res = tree.check_rb()
  print("RB Height (invalid if 0): {}\n".format(res))

  tree.remove(4)
  order = tree.inorder()
  print(order)
  res = tree.check_rb()
  print("RB Height (invalid if 0): {}\n".format(res))

  tree.remove(2)
  order = tree.inorder()
  print(order)
  res = tree.check_rb()
  print("RB Height (invalid if 0): {}\n".format(res))


  tree.remove(7)
  order = tree.inorder()
  print(order)
  res = tree.check_rb()
  print("RB Height (invalid if 0): {}\n".format(res))


  tree.remove(8)
  order = tree.inorder()
  print(order)
  res = tree.check_rb()
  print("RB Height (invalid if 0): {}\n".format(res))

if __name__ == "__main__":
  test_rb()
