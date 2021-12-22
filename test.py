# %%
import dimod
import tabu
from vnfplacement.vnf import VNF
from vnfplacement.sfc import SFC
from vnfplacement.problem_network import ProblemNetwork
from vnfplacement.qubo_form import QuboFormulation
from vnfplacement.defines import TypeVNF, NodeProperty, LinkProperty, PropertyType
import networkx as nx
import matplotlib
import matplotlib.pyplot as plt





# %% settings
init_seed = 111
graph_size = 4
edge_prob = 0.7
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
req1 = {NodeProperty.MEMORY : 3}
req2 = {NodeProperty.MEMORY : 3}
req3 = {NodeProperty.MEMORY : 3}

# vnf
vnf1 = VNF(TypeVNF.FIREWALL, req1)
vnf2 = VNF(TypeVNF.IDS, req2)
vnf3 = VNF(TypeVNF.BUSINESS_LOGIC, req3)

# sfc1
sfc = SFC("SIMPLE SFC")
sfc.set_properties(PropertyType.DRAWBACK, {LinkProperty.DELAY : 1.2})
sfc.set_properties(PropertyType.RESOURCE, {LinkProperty.BANDWIDTH: 1.2})
sfc = sfc.append_vnf(vnf1).append_vnf(vnf2).append_vnf(vnf3)#.append_vnf(vnf2)

# sfc2
sfc2 = SFC("SIMPLE SFC2")
sfc2.set_properties(PropertyType.DRAWBACK, {LinkProperty.DELAY : 1.2})
sfc2.set_properties(PropertyType.RESOURCE, {LinkProperty.BANDWIDTH: 1.2})
sfc2 = sfc2.append_vnf(vnf1).append_vnf(vnf2).append_vnf(vnf3).append_vnf(vnf2)
#print(sfc2)

# %%
# add node resources
node_res = {NodeProperty.MEMORY : 1}
node_costs = {NodeProperty.MEMORY : 1}
for n in list(net.nodes):
    net.set_node_properties(n, PropertyType.RESOURCE, node_res)
    net.set_node_properties(n, PropertyType.COST, node_costs)

# add link resources
for e in net.links:
    net.set_link_properties(e, PropertyType.RESOURCE, {LinkProperty.BANDWIDTH : 1})
    net.set_link_properties(e, PropertyType.COST, {LinkProperty.BANDWIDTH : 1})
    net.set_link_properties(e, PropertyType.DRAWBACK, {LinkProperty.DELAY : 0.2})

#%%
#print nodes and links
# print("NODES:")
# print(net.nodes.data())
# print("LINKS:")
# print(net.links.data())

#%%
# Add sfc to network
net = net.add_sfc(sfc)
# net = net.add_sfc(sfc2)
#net = net.add_sfc(sfc)

# %%
discretization = {
    LinkProperty.BANDWIDTH : 0.2,
    LinkProperty.DELAY : 0.2,
    NodeProperty.CPU : 1,
    NodeProperty.MEMORY : 1,
    NodeProperty.STORAGE : 128
}
qf = QuboFormulation(discretization)
qf.generate_qubo(net)
#print(qf.qubo.variables)
print("Number of variables:",len(qf.qubo.variables))

# # %%
# solver = dimod.ExactSolver()
# #solver = tabu.TabuSampler()
# # device = DWaveSampler()
# # solver = EmbeddingComposite(device)
# result = solver.sample(qf.qubo)
# print(result.lowest())

#sampleset = tabu.TabuSampler().sample(qf.qubo)
sampleset = dimod.ExactSolver().sample(qf.qubo)
optimum = sampleset.first.sample


#%%
color_map = []
chosen_node = []
for var in optimum:
    # print("var: {} set: {}".format(var,optimum[var]))
    if optimum[var] == 1 and not "S" in var:
        print(var)
        nodei = qf._var_to_ids(var)[0][0]
        nodef = qf._var_to_ids(var)[0][1]
        chosen_node.append(nodei)
        chosen_node.append(nodef)

for node in net.nodes:
    if node in chosen_node:
        color_map.append('red')
    else: 
        color_map.append('cyan')

nx.draw(net._pnet, node_color=color_map, with_labels=True)

# %%
#print variables at "1" in each solution
# sampleset = dimod.ExactSolver().sample(qf.qubo).lowest()
# samples = sampleset.samples()
# for best in samples[:15]:
#     cont = 0
#     varList = []
#     color_map = []
#     chosen_node = []
#     for var, val in best.items():
#         if val == 1:
#             varList.append(var)
#             nodei = qf._var_to_ids(var)[0][0]
#             nodef = qf._var_to_ids(var)[0][1]
#             chosen_node.append(nodei)
#             chosen_node.append(nodef)
#     for node in net.nodes:
#         if node in chosen_node:
#             color_map.append('red')
#         else: 
#             color_map.append('cyan')
#     fig, ax = plt.subplots(1,1)
#     ax.text(-1, -1, str(varList), fontsize=10)
#     nx.draw(net._pnet, node_color=color_map, with_labels=True, ax = ax)    
        
    

# %%
# "allocation constraint" violation for 1 chain problem
# print("Allocation violations:")
# sampleset = result.lowest()
# samples = sampleset.samples()
# for best in samples:
#     cont = 0
#     varList = []
#     for var, val in best.items():
#         if val == 1:
#             varList.append(var)
#     if len(varList) != 2:
#         print(varList)
# %%