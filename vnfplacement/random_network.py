import networkx as nx
import networkx as nx
import dimod
from vnfplacement.defines import TypeVNF, NodeProperty, LinkProperty, PropertyType

class RandomNetwork:
    def __init__(self, num_nodes, edge_prob, seed=None):
        self.pnet = nx.fast_gnp_random_graph(num_nodes, edge_prob, seed, directed=False)
        for n in self.pnet.nodes():
            nx.set_node_attributes(self.pnet, {n: {"server": None}})
        self.sfcs = []
        self.qubo = None
    
    # TODO: add node and link informations, colors of server/entry_exit_points
    def draw(self):
        nx.draw(self.pnet, with_labels = True)
        
    def nodes(self):
        return self.pnet.nodes
    
    def links(self):
        return self.pnet.edges

    def set_node_properties(self, nodeID, ptype, properties):
        # check if node is already entry/exit point
        if(self.pnet.nodes[nodeID]["server"] == False):
            raise ValueError("Server cannot be entry point")

        # make node server (unaltered if it already is)
        self.pnet.nodes[nodeID]["server"] = True

        # add node properties as cost and resource 
        atr = {nodeID : {ptype : properties}}
        nx.set_node_attributes(self.pnet, atr)

    def set_link_properties(self, edgeID, ptype, properties):
        nx.set_edge_attributes(self.pnet, {edgeID : {ptype : properties}})
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
            if v["server"] is None:
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

        # node cost
        for var in bqm.variables:
            ids = self.var_to_ids(var)
            node, sfc, vnf = self.ids_to_objs(ids)

            # skip in node is entry/exit point
            if node["server"] == False or node["server"] is None:
                continue

            # add terms
            for k, resQt in vnf.requirements.items():
                resCost = node[PropertyType.COST][k]
                bqm.add_linear(var, resCost * resQt)

        # link cost
        for var1 in bqm.variables:
            for var2 in bqm.variables:
                ids1 = self.var_to_ids(var1)
                ids2 = self.var_to_ids(var2)

                #different nodes, same chain, consecutive
                if ids1[0] == ids2[0]:
                    continue
                if ids1[1] != ids2[1]:
                    continue
                if ids1[2] != ids2[2] + 1:
                    continue

            node, sfc, vnf = self.ids_to_objs(ids)
            # print(node, sfc, vnf)

        #     # skip in node is entry/exit point
        #     if node["server"] == False or node["server"] is None:
        #         continue
        #     for k, resQt in vnf.requirements.items():
        #         resCost = node[PropertyType.COST][k]
        #         bqm.add_linear(var, resCost * resQt)
        # print(bqm)
                

    def var_to_ids(self, var):
        return [int(id[1]) for id in var.split("_")[1:]]
    
    def ids_to_objs(self, ids):
        node = self.pnet.nodes[ids[0]]
        sfc = self.sfcs[ids[1]][0]
        vnf = sfc.vnfs[ids[2]]
        return node, sfc, vnf