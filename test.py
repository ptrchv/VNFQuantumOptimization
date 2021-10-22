# %%
from vnfplacement.vnf import VNF
from vnfplacement.sfc import SFC
from vnfplacement.random_network import RandomNetwork
from vnfplacement.defines import TypeVNF, NodeProperty, LinkProperty, PropertyType

# %% settings
init_seed = 111
graph_size = 10
edge_prob = 0.5
switch_prob = 0.7

# %%
net = RandomNetwork(graph_size, edge_prob, init_seed)
net.draw()
# print(nx.adjacency_matrix(net.pnet))

#%% TEST VNF and SFC classes
#requirements
req1 = {NodeProperty.CPU : 3, NodeProperty.MEMORY : 3.5, NodeProperty.STORAGE : 11}
req2 = {NodeProperty.CPU : 1, NodeProperty.MEMORY : 5, NodeProperty.STORAGE : 15}
req3 = {NodeProperty.CPU : 2, NodeProperty.MEMORY : 12, NodeProperty.STORAGE : 60}

# vnf
vnf1 = VNF(TypeVNF.FIREWALL, req1)
vnf2 = VNF(TypeVNF.IDS, req2)
vnf3 = VNF(TypeVNF.BUSINESS_LOGIC, req3)

# sfc
sfc = SFC("MOBILE_API")
sfc.set_properties(PropertyType.DRAWBACK, {LinkProperty.DELAY : 3})
sfc.set_properties(PropertyType.RESOURCE, {LinkProperty.BANDWIDTH: 0.5})
sfc = sfc.append_vnf(vnf1).append_vnf(vnf2).append_vnf(vnf3)
print(sfc)

# %%
# add node resources
node_res = {NodeProperty.CPU : 4, NodeProperty.MEMORY : 512, NodeProperty.STORAGE : 5000}
node_costs = {NodeProperty.CPU : 1, NodeProperty.MEMORY : 1, NodeProperty.STORAGE : 1}
for n in list(net.nodes())[:-3]:
    net.set_node_properties(n, PropertyType.RESOURCE, node_res)
    net.set_node_properties(n, PropertyType.COST, node_costs)

# add link resources
link_res = {LinkProperty.BANDWIDTH : 1.5, LinkProperty.DELAY : 0.2}
link_cost = {LinkProperty.BANDWIDTH : 1}
for e in net.links():
    net.set_link_properties(e, PropertyType.RESOURCE, link_res)
    net.set_link_properties(e, PropertyType.COST, link_cost)

# print nodes and links
# print("NODES:")
# print(net.nodes().data())
# print("LINKS:")
# print(net.links().data())

#%%
# Add sfc to network
nodeIDs = list(net.nodes()) # only IDs
net = net.add_sfc(sfc, nodeIDs[-2], nodeIDs[-1])
#print(net.nodes().data())

# %%
net.get_qubo()


# %%

# %%

# %%

# %%
