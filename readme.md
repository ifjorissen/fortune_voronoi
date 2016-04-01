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
    * --OR-- set autoscale (check with `show xrange` or `show yrange`)
    * unset key
    * unset border
    * set output 'diagrams/<filename>'
    * note, stay just within these bounds so you can't see where the edge terminates
    * `plot 'results/edges.dat' with lines,\
      'results/del.dat' with lines dt 2,\
      'results/sites.dat' using 1:2 with points pointtype 11,\
      'results/vertices.dat' using 1:2 with points pointtype 5`

    * plot 'results/edges.dat' with lines,\
      'results/del_1done.dat' with lines dt 2,\
      'results/sites.dat' using 1:2 with points pointtype 11,\
      'results/vertices.dat' using 1:2 with points pointtype 5 

    * fortune intuition diagrams:
      * `plot 'diagrams/fortune_intuition/beach_0.76.dat' with lines dt 4,\
      'diagrams/fortune_intuition/scan_0.76.dat' with lines,\
      'diagrams/fortune_intuition/sites.dat' using 1:2 with points pointtype 11'

      * `plot 'results/beach_0.62.dat' with lines dt 4,\
      'results/scan_0.62.dat' with lines,\
      'results/sites.dat' using 1:2 with points pointtype 11`

      * `plot 'results/beach_0.47.dat' with lines dt 4,\
      'results/scan_0.47.dat' with lines,\
      'results/circles_0.47.dat' with lines dt 2,\
      'results/sites.dat' using 1:2 with points pointtype 11`

      * `plot 'results/beach_0.31.dat' with lines dt 4,\
      'results/scan_0.31.dat' with lines,\
      'results/circles_0.31.dat' with lines dt 2,\
      'results/vertices.dat' using 1:2 with points pointtype 5,\
      'results/sites.dat' using 1:2 with points pointtype 11`

      * `plot 'results/edges.dat' with lines,\
      'results/circles_0.31.dat' with lines dt 2,\
      'results/sites.dat' using 1:2 with points pointtype 11,\
      'results/vertices.dat' using 1:2 with points pointtype 5`



    * copy the results to a .tex file in the figs folder of ~/big_paper_latex/ 
    * chage the dotsize in the result to at least .2 (from 0.01)
    * save the raw output files just in case you need to remake them

### Point types:
3: Circle
4: Triangle

### Line Types:
dt 4: Long Dash