# %%
import networkx as nx
from enum import Enum
import dimod
import os
import textwrap

# %% settings
init_seed = 111
graph_size = 10
edge_prob = 0.5
switch_prob = 0.7

# %% Enums
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

# %% VNF and SFC
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

    def append_vnf(self, vnf):
        self.vnfs.append(vnf)
        return self

    def __str__(self):
        str_rep = f"{self.name}:{os.linesep}"
        for vnf in self.vnfs[:-1]:
            vnf_str = textwrap.indent(str(vnf), "\t")
            str_rep += f"{vnf_str}{os.linesep}"
        str_rep += textwrap.indent(str(self.vnfs[-1]), "\t")
        return str_rep

# %%random network
class RandomNetwork:
    def __init__(self, num_nodes, edge_prob, seed=None):
        self.pnet = nx.fast_gnp_random_graph(num_nodes, edge_prob, seed, directed=False)
        for n in self.pnet.nodes():
            nx.set_node_attributes(self.pnet, {n: {"server": None}})
        self.sfcs = []
        self.qubo = None
    
    #TODO: add node and link informations, colors of server/entry_exit_points
    def draw(self):
        nx.draw(self.pnet, with_labels = True)
        
    def nodes(self):
        return self.pnet.nodes
    
    def links(self):
        return self.pnet.edges

    def add_node_resources(self, nodeID, resources, costs):
        #check if node is entry/exit point
        if(self.pnet.nodes[nodeID]["server"] == False):
            raise ValueError("Server cannot be entry point")
        #make node server (unaltered if it already is)
        self.pnet.nodes[nodeID]["server"] = True
        nx.set_node_attributes(self.pnet, {nodeID : {"res" : resources, "cost": costs}})

    def add_link_resources(self, edgeID, bandwidth, delay):
        nx.set_edge_attributes(self.pnet, {edgeID : {"delay":delay, "bandwidth":bandwidth}})
        return self

    def add_sfc(self, sfc, startNodeID, endNodeID):
        #chek if entry/exit points are servers
        if(self.pnet.nodes[startNodeID]["server"] == True):
            raise ValueError("Server cannot be entry point")
        if(self.pnet.nodes[endNodeID]["server"] == True):
            raise ValueError("Server cannot be exit point")

        #make node entry/exit (unaltered if they are already)
        self.pnet.nodes[startNodeID]["server"] = False
        self.pnet.nodes[endNodeID]["server"] = False

        #add sfc and save entry and exit points
        self.sfcs.append((sfc, (startNodeID, endNodeID)))
        return self
    
    def get_qubo(self):
        bqm = dimod.BinaryQuadraticModel(dimod.BINARY)
        #create all variables
        for n, v in self.pnet.nodes.items():
            if(v["server"] is None):
                print(f"[WARNING]: Node {n} won't be considered")
                continue
            sID = 0
            for s in self.sfcs:
                fID = 0
                for f in s[0].vnfs:
                    bqm.add_variable(f"x_N{n}_C{sID}_F{fID}")
                    fID+=1
                sID+=1
        # print(bqm.variables)
        # bqm.fix_variable("x_N1_C0_F0", 1)
        # print(bqm.variables)

        #node cost
        for var in bqm.variables:       
            ids = self.var_to_ids(var)
            node, sfc, vnf = self.ids_to_objs(ids)
            # print(node, sfc, vnf)

            # skip in node is entry/exit point
            if(node["server"] == False):
                continue
            for k,v in vnf.requirements.items():
                pass
                


    def var_to_ids(self, var):
        return [int(id[1]) for id in var.split("_")[1:]]
    
    def ids_to_objs(self, ids):
        node = self.pnet.nodes[ids[0]]
        sfc = self.sfcs[ids[1]][0]
        vnf = sfc.vnfs[ids[2]]
        return node, sfc, vnf

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
sfc = SFC("MOBILE_API", 500, 3)
sfc = sfc.append_vnf(vnf1).append_vnf(vnf2).append_vnf(vnf3)
print(sfc)

# %%
# add node resources
node_res = {NodeResource.CPU : 4, NodeResource.MEMORY : 512, NodeResource.STORAGE : 5000}
node_costs = {NodeResource.CPU : 1, NodeResource.MEMORY : 1, NodeResource.STORAGE : 1}
for n in list(net.nodes())[:-3]:
    net.add_node_resources(n, node_res, node_costs)

# add link resources
for e in net.links():
    net.add_link_resources(e, 1.5, 0.2)

# print nodes and links
print("NODES:")
print(net.nodes().data())
print("LINKS:")
print(net.links().data())

#%%
# Add sfc to network
nodeIDs = list(net.nodes()) # only IDs
net = net.add_sfc(sfc, nodeIDs[-2], nodeIDs[-1])
print(net.nodes().data())

# %%
net.get_qubo()

