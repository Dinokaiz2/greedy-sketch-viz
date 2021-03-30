# persim-webviz

## Sketches

Given a k-point persistence diagram as input, we generate k sketches of the
diagram. We add one point of the original diagram in each incremental sketch
using the greedy permutation.

![001](https://user-images.githubusercontent.com/41081293/113051813-66b05c80-9174-11eb-8484-98314882c5b5.jpg)

Consider a persistence diagram, D, with six points, {a,b,c,d,e,f}, and the
diagonal, o. An input of D will generate the seven sketches, D<sub>0</sub> to
D<sub>6</sub>, as output. The ordering {o,a,d,e,b,f,c} is a greedy permutation.
The diagonal is added in the first sketch. The number near every point, x, in
D<sub>i</sub> highlights the multiplicity of points in D that are mapped to x
in D<sub>i</sub>.

## Voronoi Diagram of a Persistence Diagram

![002](https://user-images.githubusercontent.com/41081293/113041507-0adfd680-9168-11eb-88cb-95a334ceac1a.jpg)

This is a Voronoi diagram of a sample persistence diagram using the
L<sub>inf</sub> metric and treating the entire diagonal as a single point. Such
Voronoi diagrams will be calculated for every sketch.
