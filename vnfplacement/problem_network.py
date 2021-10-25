import networkx as nx
import networkx as nx

class ProblemNetwork:
    def __init__(self, num_nodes, edge_prob, seed=None):
        self.pnet = nx.fast_gnp_random_graph(num_nodes, edge_prob, seed, directed=False)
        for n in self.pnet.nodes():
            nx.set_node_attributes(self.pnet, {n: {"server": None}})
        self.sfcs = []
        self.detatched = {}
        self.qubo = None
    
    # TODO: add node and link informations, colors of server/entry_exit_points
    def draw(self):
        nx.draw(self.pnet, with_labels = True)
        
    def nodes(self):
        return self.pnet.nodes
    
    def links(self):
        return self.pnet.edges

    def are_linked(self, nodeID1, nodeID2):
        return nodeID2 in self.pnet[nodeID1].keys()

    def get_link(self, nodeID1, nodeID2):
        return self.pnet[nodeID1][nodeID2]

    def set_detatched_properties(self, ptype, properties):
        self.detatched[ptype] = properties

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
    
    def ids_to_objs(self, ids):
        node = self.pnet.nodes[ids[0]]
        sfc = self.sfcs[ids[1]][0]
        vnf = sfc.vnfs[ids[2]]
        return node, sfc, vnf

    def is_used(self, nodeID):
        return self.pnet.nodes[nodeID]["server"] is not None

    def is_server(self, nodeID):
        return self.pnet.nodes[nodeID]["server"] == True

    def is_entry(self, nodeID):
        return self.pnet.nodes[nodeID]["server"] == False