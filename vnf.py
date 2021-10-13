# %%
import networkx as nx
import random
from enum import Enum
import dimod

init_seed = 111
graph_size = 7
edge_prob = 0.5
switch_prob = 0.7

color_switch = "yellow"
color_server = "orange"

# %%
# generate graph


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

class NodeResources:
    CPU = 1
    MEMORY = 1
    STORAGE = 1

class VNF:
    def _init_(self):
        self.requirements = {}
    def add_requirement(self, resource, requirement):
        self.requirements[resource] = requirement

class SFC:
    def _init_(self, entry_point, exit_point, bandwidth, delay):
        self.entry_point = entry_point
        self.exit_point = exit_point
        self.bandwidth = bandwidth
        self.delay = delay
        self.vnfs = []

    def add_function(self, vnf):
        self.vnfs.append(vnf)

def rand_init(self, rand_size, points):
        self.vnfs = random.choices(list(VNF), rand_size)
        self.entry_point = random.choice(points)
        self.exit_point = random.choice(points)

class RandomNetwork:
    def _init_(self, seed):
        self.pnet = nx.fast_gnp_random_graph(graph_size, seed, directed=False)
    def draw(self):
        nx.draw(self.pnet, with_labels = True)












# %%
