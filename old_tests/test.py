# %%
import dimod
from dimod import sampleset
import tabu
from vnfplacement.vnf import VNF
from vnfplacement.sfc import SFC
from vnfplacement.problem_network import ProblemNetwork
from vnfplacement.qubo_form import QuboFormulation
from vnfplacement.defines import NodeProperty, LinkProperty, PropertyType
import networkx as nx
import matplotlib
import matplotlib.pyplot as plt
import config
from dwave.cloud import Client
from dwave.system.samplers import DWaveSampler
from dwave.system.composites import EmbeddingComposite
from dwave.system.composites import FixedEmbeddingComposite
import dwave.inspector


# %% settings
init_seed = 333
graph_size = 8
edge_prob = 0.4
# %%
net = ProblemNetwork.from_random_gen(graph_size, edge_prob, init_seed)
net.draw()
# print(nx.adjacency_matrix(net.pnet))

#%% TEST VNF and SFC classes
# #requirements
# req1 = {NodeProperty.CPU : 3, NodeProperty.MEMORY : 3.5, NodeProperty.STORAGE : 11}
# req2 = {NodeProperty.CPU : 1, NodeProperty.MEMORY : 5, NodeProperty.STORAGE : 15}
# req3 = {NodeProperty.CPU : 2, NodeProperty.MEMORY : 12, NodeProperty.STORAGE : 60}

# # vnf
# vnf1 = VNF("FIREWALL", req1)
# vnf2 = VNF("IDS", req2)
# vnf3 = VNF("BUSINESS_LOGIC", req3)

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
req2 = {NodeProperty.MEMORY : 1}
req3 = {NodeProperty.MEMORY : 1}

# vnf
vnf1 = VNF("FIREWALL", req1)
vnf2 = VNF("IDS", req2)
vnf3 = VNF("BUSINESS_LOGIC", req3)

# sfc1
sfc = SFC("SIMPLE SFC")
sfc.set_properties(PropertyType.DRAWBACK, {LinkProperty.DELAY : 0.8})
sfc.set_properties(PropertyType.RESOURCE, {LinkProperty.BANDWIDTH: 1.2})
sfc = sfc.append_vnf(vnf1).append_vnf(vnf2).append_vnf(vnf3)#.append_vnf(vnf2)

# sfc2
sfc2 = SFC("SIMPLE SFC2")
sfc2.set_properties(PropertyType.DRAWBACK, {LinkProperty.DELAY : 0.8})
sfc2.set_properties(PropertyType.RESOURCE, {LinkProperty.BANDWIDTH: 1.2})
sfc2 = sfc2.append_vnf(vnf1).append_vnf(vnf2).append_vnf(vnf3).append_vnf(vnf2)
#print(sfc2)

# %%
# add node resources
node_res = {NodeProperty.MEMORY : 5}
node_costs = {NodeProperty.MEMORY : 1}
for n in list(net.nodes):
    net.set_node_properties(n, PropertyType.RESOURCE, node_res)
    net.set_node_properties(n, PropertyType.COST, node_costs)

## Manual node test #########
# node_res3 = {NodeProperty.MEMORY : 4}
# node_res1 = {NodeProperty.MEMORY : 1}
# net.set_node_properties(0, PropertyType.RESOURCE, node_res3)
# net.set_node_properties(0, PropertyType.COST, node_costs)
# net.set_node_properties(1, PropertyType.RESOURCE, node_res1)
# net.set_node_properties(1, PropertyType.COST, node_costs)
# net.set_node_properties(2, PropertyType.RESOURCE, node_res3)
# net.set_node_properties(2, PropertyType.COST, node_costs)
# net.set_node_properties(3, PropertyType.RESOURCE, node_res3)
# net.set_node_properties(3, PropertyType.COST, node_costs)
######################

## Manual link test #########
# net.set_link_properties((0,2), PropertyType.RESOURCE, {LinkProperty.BANDWIDTH : 1})
# net.set_link_properties((0,2), PropertyType.COST, {LinkProperty.BANDWIDTH : 1})
# net.set_link_properties((0,2), PropertyType.DRAWBACK, {LinkProperty.DELAY : 0.6})

# net.set_link_properties((1,2), PropertyType.RESOURCE, {LinkProperty.BANDWIDTH : 1})
# net.set_link_properties((1,2), PropertyType.COST, {LinkProperty.BANDWIDTH : 1})
# net.set_link_properties((1,2), PropertyType.DRAWBACK, {LinkProperty.DELAY : 0.4})

# net.set_link_properties((2,3), PropertyType.RESOURCE, {LinkProperty.BANDWIDTH : 1})
# net.set_link_properties((2,3), PropertyType.COST, {LinkProperty.BANDWIDTH : 1})
# net.set_link_properties((2,3), PropertyType.DRAWBACK, {LinkProperty.DELAY : 0.4})
#############################

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
# sampleset = dimod.ExactSolver().sample(qf.qubo)
# optimum = sampleset.first.sample


# #%%
# color_map = []
# chosen_node = []
# for var in optimum:
#     # print("var: {} set: {}".format(var,optimum[var]))
#     if optimum[var] == 1 and not "S" in var:
#         print(var)
#         nodei = qf._var_to_ids(var)[0][0]
#         nodef = qf._var_to_ids(var)[0][1]
#         chosen_node.append(nodei)
#         chosen_node.append(nodef)

# for node in net.nodes:
#     if node in chosen_node:
#         color_map.append('red')
#     else: 
#         color_map.append('cyan')

# nx.draw(net._pnet, node_color=color_map, with_labels=True)

# %%
#print variables at "1" in each solution
# sampleset = dimod.ExactSolver().sample(qf.qubo).lowest()
# samples = sampleset.samples()

client = Client.from_config(token=config.api_token)
print(client.get_solvers())
device = DWaveSampler(token = config.api_token)
print(device)
solver = EmbeddingComposite(device)
# solver = FixedEmbeddingComposite(device)
sampleset = solver.sample(qf.qubo, num_reads = 1000, embedding_parameters=dict(timeout=200), chain_strength=50)
print(sampleset)
#sampleset = dimod.ExactSolver().sample(qf.qubo)
inspector = dwave.inspector.show(sampleset)
samples = sampleset.samples()
#%%
counter = 0
threshold = 10
for best, energy in sampleset.data(fields=['sample','energy'], sorted_by='energy'):
    if counter < threshold:
        counter += 1
        cont = 0
        varList = []
        color_map = []
        chosen_node = []
        for var, val in best.items():
            if val == 1:
                if not qf.is_slack(var):   
                    varList.append(var)  
                    nodei = qf._var_to_ids(var)[0][0]
                    nodef = qf._var_to_ids(var)[0][1]
                    chosen_node.append(nodei)
                    chosen_node.append(nodef)
        for node in net.nodes:
            if node in chosen_node:
                color_map.append('red')
            else: 
                color_map.append('cyan')
        fig, ax = plt.subplots(1,1)
        ax.text(-1, -1, str(varList) + str(energy), fontsize=10)
        nx.draw(net._pnet, node_color=color_map, with_labels=True, ax = ax)    
        
    

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