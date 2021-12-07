# %%
import dimod
from vnfplacement.vnf import VNF
from vnfplacement.sfc import SFC
from vnfplacement.problem_network import ProblemNetwork
from vnfplacement.qubo_form import QuboFormulation
from vnfplacement.defines import TypeVNF, NodeProperty, LinkProperty, PropertyType

# %% settings
init_seed = 111
graph_size = 4
edge_prob = 1

# %%
net = ProblemNetwork(graph_size, edge_prob, init_seed)
net.draw()
# print(nx.adjacency_matrix(net.pnet))

#%% TEST VNF and SFC classes
# #requirements
# req1 = {NodeProperty.CPU : 3, NodeProperty.MEMORY : 3.5, NodeProperty.STORAGE : 11}
# req2 = {NodeProperty.CPU : 1, NodeProperty.MEMORY : 5, NodeProperty.STORAGE : 15}
# req3 = {NodeProperty.CPU : 2, NodeProperty.MEMORY : 12, NodeProperty.STORAGE : 60}

# # vnf
# vnf1 = VNF(TypeVNF.FIREWALL, req1)
# vnf2 = VNF(TypeVNF.IDS, req2)
# vnf3 = VNF(TypeVNF.BUSINESS_LOGIC, req3)

# # sfc
# sfc = SFC("MOBILE_API")
# sfc.set_properties(PropertyType.DRAWBACK, {LinkProperty.DELAY : 3})
# sfc.set_properties(PropertyType.RESOURCE, {LinkProperty.BANDWIDTH: 0.5})
# sfc = sfc.append_vnf(vnf1).append_vnf(vnf2).append_vnf(vnf3)
# print(sfc)

# %%
# # add node resources
# node_res = {NodeProperty.CPU : 4, NodeProperty.MEMORY : 512, NodeProperty.STORAGE : 5000}
# node_costs = {NodeProperty.CPU : 1, NodeProperty.MEMORY : 1, NodeProperty.STORAGE : 1}
# for n in list(net.nodes):
#     net.set_node_properties(n, PropertyType.RESOURCE, node_res)
#     net.set_node_properties(n, PropertyType.COST, node_costs)

# # add link resources
# for e in net.links:
#     net.set_link_properties(e, PropertyType.RESOURCE, {LinkProperty.BANDWIDTH : 1.5})
#     net.set_link_properties(e, PropertyType.COST, {LinkProperty.BANDWIDTH : 1})
#     net.set_link_properties(e, PropertyType.DRAWBACK, {LinkProperty.DELAY : 0.2})

#%% TEST VNF and SFC classes
#requirements
req1 = {NodeProperty.MEMORY : 1}
req2 = {NodeProperty.MEMORY : 2}
req3 = {NodeProperty.MEMORY : 3}

# vnf
vnf1 = VNF(TypeVNF.FIREWALL, req1)
vnf2 = VNF(TypeVNF.IDS, req2)
vnf3 = VNF(TypeVNF.BUSINESS_LOGIC, req3)

# sfc
sfc = SFC("SIMPLE SFC")
sfc.set_properties(PropertyType.DRAWBACK, {LinkProperty.DELAY : 1})
sfc.set_properties(PropertyType.RESOURCE, {LinkProperty.BANDWIDTH: 0.5})
sfc = sfc.append_vnf(vnf1).append_vnf(vnf2).append_vnf(vnf3)
print(sfc)

# %%
# add node resources
node_res = {NodeProperty.MEMORY : 3}
node_costs = {NodeProperty.MEMORY : 1}
for n in list(net.nodes):
    net.set_node_properties(n, PropertyType.RESOURCE, node_res)
    net.set_node_properties(n, PropertyType.COST, node_costs)

# add link resources
for e in net.links:
    net.set_link_properties(e, PropertyType.RESOURCE, {LinkProperty.BANDWIDTH : 1})
    net.set_link_properties(e, PropertyType.COST, {LinkProperty.BANDWIDTH : 1})
    net.set_link_properties(e, PropertyType.DRAWBACK, {LinkProperty.DELAY : 0.1})

#%%
#print nodes and links
# print("NODES:")
# print(net.nodes.data())
# print("LINKS:")
# print(net.links.data())

#%%
# Add sfc to network
net = net.add_sfc(sfc)

# %%
discretization = {
    LinkProperty.BANDWIDTH : 0.2,
    LinkProperty.DELAY : 0.1,
    NodeProperty.CPU : 1,
    NodeProperty.MEMORY : 4,
    NodeProperty.STORAGE : 128
}
qf = QuboFormulation(discretization)
qf.generate_qubo(net)

# %%
# solver = dimod.ExactSolver()
# # device = DWaveSampler()
# # solver = EmbeddingComposite(device)
# result = solver.sample(qf.qubo, num_reads = 20)
# print(result.lowest())


# %%

# %%
