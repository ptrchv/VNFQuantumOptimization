# %%
# adapted from:
# https://github.com/dwave-examples/maximum-cut.git

# %%
# imports
from collections import defaultdict
from dimod.binary.binary_quadratic_model import Binary
from dwave.cloud import Client
from dwave.system.samplers import DWaveSampler
from dwave.system.composites import EmbeddingComposite
from matplotlib import pyplot as plt
import dimod
import numpy as np

import config
import networkx as nx

# %%
client = Client.from_config(token=config.api_token)
print(client.get_solvers())

# %%
# Create empty graph
G = nx.Graph()

# Add edges to the graph (also adds nodes)
G.add_edges_from([(1,2),(1,3),(2,4),(3,4),(3,5),(4,5)])

#draw graph
nx.draw(G, with_labels = True)

# %%
# create QUBO from dictionary
h_dict = defaultdict(float)
j_dict = defaultdict(float)

for i, j in G.edges:
    # label variables
    label_h1 = f"x_{i}"
    label_h2 = f"x_{j}"

    # dictionary
    h_dict[label_h1] += -1
    h_dict[label_h2] += -1
    j_dict[(label_h1, label_h2)] += 2

# create binary model
bqm_dict = dimod.BinaryQuadraticModel(h_dict, j_dict, 0.0, dimod.BINARY)

# %%
# crate qubo from numpy
n_nodes = G.number_of_nodes()
qubo_np = np.zeros((n_nodes, n_nodes))
for i, j in G.edges:
    qubo_np[i-1, i-1] += -1
    qubo_np[j-1, j-1] += -1
    qubo_np[i-1, j-1] += 1
    qubo_np[j-1, i-1] += 1
bqm_np= dimod.BinaryQuadraticModel(qubo_np, dimod.BINARY)
var_map = {i:f"x_{i}" for i in range(n_nodes)}
bqm_np = bqm_np.relabel_variables(var_map)

# %%
# create QUBO directly with BinaryQuadraticModel
bqm = dimod.BinaryQuadraticModel(dimod.BINARY)
for i, j in G.edges:
    #label variables
    label_h1 = f"x_{i}"
    label_h2 = f"x_{j}"
    bqm.add_linear(label_h1, -1)
    bqm.add_linear(label_h2, -1)
    bqm.add_quadratic(label_h1, label_h2, 2)

# %%
#print models to check equality
print(h_dict, j_dict)
print(bqm_np)
print(bqm)
print(bqm.to_qubo())

# %%
# find solution
solver = dimod.ExactSolver()
# device = DWaveSampler()
# solver = EmbeddingComposite(device)
result = solver.sample(bqm, num_reads = 20)
result


# %%
sol = result.first.sample
cmap = []
for n in G.nodes:
    if(sol[f"x_{n}"] == 1):
        cmap.append("yellow")
    else:
        cmap.append("orange")    
nx.draw(G, node_color = cmap, with_labels = True)

# %%
