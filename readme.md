## Voronoi Diagram w/ Fortune's algorithm

Isabella Jorissen 
Updated: 10.15.15

### Setup:
  * Make a virtual env
    * `mkdir <env folder>`
    * pyvenv <env folder>
    * activate it with `source <env folder>/bin/activate`

  * Install requirements with `pip install -r requirements.txt`

### Usage:
  * If you want to see the voronoi generation on the fly: `python view.py`
    * Click to add points
    * Spacebar to start the scan
    * 'c' to hide the circles
    * 'b' to hide the beachfront & scanline
    * 'd' to hide the delaunay triangulation
  * Use the sample file (sites.txt):
    * `python no_view.py`


### Making Diagrams
  * open gnuplot: `gnuplot`
  * set the terminal: `set terminal pstricks`
  * remove tics: `unset xtic && unset ytic`
  * ranges:
    * set the xrange: `set xrange([xmin_from_data]:[x_max_from_data])`
    * set the yrange: `set yrange([ymin_from_data]:[y_max_from_data])`
    * note, stay just within these bounds so you can't see where the edge terminates
    * `plot 'results/edges.dat' with lines, 'results/sites.dat' using 1:2 with points, 'results/vertices.dat' using 1:2 with points`
    * copy the results to a .tex file in the figs folder of ~/big_paper_latex/ 
    * chage the dotsize in the result to at least .2 (from 0.01)
    * save the raw output files just in case you need to remake them

