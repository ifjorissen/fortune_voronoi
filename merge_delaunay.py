from voronoi.voronoi import Voronoi
from voronoi.delaunay import Delaunay

def main():
    v = Voronoi(view=False, id_prefix="L")
    v.read('d1_sites.txt')
    v.precompute()
    v.validateDCEL()
    v.outputVoronoi()

    v2 = Voronoi(view=False, id_prefix="R")
    v2.read('d2_sites.txt')
    v2.precompute()
    v2.validateDCEL()
    v2.outputVoronoi()

    d1 = v.delaunay
    d2 = v2.delaunay

    Delaunay.merge_triangulations(d1, d2)


if __name__ == "__main__":
    main()