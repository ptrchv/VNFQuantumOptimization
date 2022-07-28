# VNF Quantum Optimization
This repository contains the source code for the article "Virtual Network Function Embedding with Quantum Annealing" accepted at [QCE22 - IEEE International Conference on Quantum Computing and Engineering](https://qce.quantum.ieee.org/2022/)

## Formulation
Cost function for node and link operation:

![Cut examples](res/img/cost_function.png "Cut examples")

Constraint VNF allocation. Each VNF must be allocated exactly once:

![Cut examples](res/img/allocation.png "Cut examples")

Constraint on SFC continutiy:

![Cut examples](res/img/continuity.png "Cut examples")

Constraint on node resouce utilization:

![Cut examples](res/img/node_resources.png "Cut examples")

Constraint on link bandwidth utilization:

![Cut examples](res/img/bandwidth.png "Cut examples")

Constraint on SFC link induced delay:

![Cut examples](res/img/delay.png "Cut examples")


## Change formulas
Update the "formula.tex" file in "res/tex" and use the script "res/equation_render.py" to regenerate the images.


## External resources
https://pyvis.readthedocs.io/en/latest/index.html
https://www.yworks.com/products/yed


