from voronoi.voronoi import Voronoi

def main():
  v = Voronoi(view=False)
  v.read('sites.txt')
  v.precompute()
  v.validateDCEL()
  v.outputVoronoi()

if __name__ == "__main__": main()