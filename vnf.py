# %%
import networkx as nx
import random
from enum import Enum
import dimod
import os
import textwrap

from networkx.algorithms.components.connected import node_connected_component

init_seed = 111
graph_size = 7
edge_prob = 0.5
switch_prob = 0.7

color_switch = "yellow"
color_server = "orange"

# %%
#make node swith or server with probability prob
def node_class_rand(net, prob):
    for n in net.nodes:
        if (random.random() < prob):
            nx.set_node_attributes(net, {n:{"type":"switch", "color":"yellow"}})
        else:
            nx.set_node_attributes(net, {n:{"type":"server", "color":"orange"}})   
    return net

#draw graph using color property of nodes
def draw_with_colors(net):
    cmap = list(nx.get_node_attributes(net, "color").values())
    nx.draw(net, node_color = cmap, with_labels = True)

# %%
# problem classes
class TypeVNF(Enum):
    FIREWALL = 1
    NAT = 2
    IDS = 3
    PROXY = 4
    BUSINESS_LOGIC = 5

class NodeResource(Enum):
    CPU = 1         #num_cpu
    MEMORY = 2      #GB
    STORAGE = 3     #GB

class VNF:
    def __init__(self, typeVNF, requirements):
        self.requirements = requirements
        self.typeVNF = typeVNF
    def __str__(self):
        str_rep = str(self.typeVNF) + os.linesep
        for k, v in self.requirements.items():
            str_rep += f"{k.name}: {v}{os.linesep}"
        return str_rep

class SFC:
    def __init__(self, name, bandwidth, delay):
        self.name = name
        self.bandwidth = bandwidth  #GiB/s
        self.delay = delay          #ms
        self.vnfs = []

    def add_vnf(self, vnf):
        self.vnfs.append(vnf)
        return self

    def __str__(self):
        str_rep = f"{self.name}:{os.linesep}"
        for vnf in self.vnfs[:-1]:
            vnf_str = textwrap.indent(str(vnf), "\t")
            str_rep += f"{vnf_str}{os.linesep}"
        str_rep += textwrap.indent(str(self.vnfs[-1]), "\t")
        return str_rep

def rand_init(self, rand_size, points):
        self.vnfs = random.choices(list(VNF), rand_size)
        self.entry_point = random.choice(points)
        self.exit_point = random.choice(points)

class RandomNetwork:
    def __init__(self, num_nodes, edge_prob, seed=None):
        self.pnet = nx.fast_gnp_random_graph(num_nodes, edge_prob, seed, directed=False)
        self.qubo = None
    
    def draw(self):
        nx.draw(self.pnet, with_labels = True)
        
    def get_graph(self):
        return self.pnet

    def add_node_resources(self, nodeId, resources):
        for k,v in resources:
            nx.add_node_attributes(self.pnet, {nodeId : {k : v.name}})

    def add_link_resources(self, nodeId1, nodeId2, bandwidth, delay):
        #nx.set_node_attributes(sepnet)
        self.pnet
    
    def get_qubo(self, update = True):
        if not update:
            return self.qubo
        return None

# %%
net = RandomNetwork(graph_size, edge_prob, init_seed)
net.draw()
#print(nx.adjacency_matrix(net.pnet))

#%% TEST VNF and SFC classes
#requirements
req1 = {NodeResource.CPU : 3, NodeResource.MEMORY : 3.5, NodeResource.STORAGE : 11}
req2 = {NodeResource.CPU : 1, NodeResource.MEMORY : 5, NodeResource.STORAGE : 15}
req3 = {NodeResource.CPU : 2, NodeResource.MEMORY : 12, NodeResource.STORAGE : 60}
#vnf
vnf1 = VNF(TypeVNF.FIREWALL, req1)
vnf2 = VNF(TypeVNF.IDS, req2)
vnf3 = VNF(TypeVNF.BUSINESS_LOGIC, req3)
#sfc
sfc = SFC("MOBILE_API",500, 3)
sfc.add_vnf(vnf1).add_vnf(vnf2).add_vnf(vnf3)

print(sfc)

