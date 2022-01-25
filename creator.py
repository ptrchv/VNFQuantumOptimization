# %%
from vnfplacement.problem_network import ProblemNetwork
from vnfplacement.defines import NodeProperty, PropertyType
import networkx as nx


# %% settings
init_seed = 333
graph_size = 8
edge_prob = 0.4
# %%
net = ProblemNetwork.from_random_gen(graph_size, edge_prob, init_seed)


node_res = {NodeProperty.MEMORY : 5}
node_costs = {NodeProperty.MEMORY : 1}
for n in list(net.nodes):
    net.set_node_properties(n, PropertyType.RESOURCE, node_res)
    net.set_node_properties(n, PropertyType.COST, node_costs)

net.draw()
# %%


nx.write_gpickle(net._pnet, "test.gpickle")
net_copy = nx.read_gpickle("test.gpickle")

print(net._pnet.nodes())
print(net_copy.nodes())
#net_copy.nodes()
# %%

# %%
