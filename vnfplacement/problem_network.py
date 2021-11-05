import networkx as nx
import networkx as nx

class ProblemNetwork:
    def __init__(self, num_nodes, edge_prob, seed=None):
        self._pnet = nx.fast_gnp_random_graph(num_nodes, edge_prob, seed, directed=False)
        for n in self._pnet.nodes():
            nx.set_node_attributes(self._pnet, {n: {"server": None}})
        self._sfcs = []
    
    # TODO: add node and link informations, colors of server/entry_exit_points
    def draw(self):
        nx.draw(self._pnet, with_labels = True)
        
    def nodes(self):
        return self._pnet.nodes
    
    def links(self):
        return self._pnet.edges

    def sfcs(self):
        return {k:v[0] for k, v in enumerate(self._sfcs)}

    def are_linked(self, nodeID1, nodeID2):
        return nodeID2 in self._pnet[nodeID1].keys()

    def get_link(self, nodeID1, nodeID2):
        return self._pnet[nodeID1][nodeID2]

    def set_node_properties(self, nodeID, ptype, properties):
        # check if node is already entry/exit point
        if(self._pnet.nodes[nodeID]["server"] == False):
            raise ValueError("Server cannot be entry point")

        # make node server (unaltered if it already is)
        self._pnet.nodes[nodeID]["server"] = True

        # add node properties as cost and resource 
        atr = {nodeID : {ptype : properties}}
        nx.set_node_attributes(self._pnet, atr)

    def set_link_properties(self, edgeID, ptype, properties):
        nx.set_edge_attributes(self._pnet, {edgeID : {ptype : properties}})
        return self

    def add_sfc(self, sfc, startNodeID, endNodeID):
        #chek if entry/exit points are servers
        if(self._pnet.nodes[startNodeID]["server"] == True):
            raise ValueError("Server cannot be entry point")
        if(self._pnet.nodes[endNodeID]["server"] == True):
            raise ValueError("Server cannot be exit point")

        #make node entry/exit (unaltered if they are already)
        self._pnet.nodes[startNodeID]["server"] = False
        self._pnet.nodes[endNodeID]["server"] = False

        #add sfc and save entry and exit points
        self._sfcs.append((sfc, (startNodeID, endNodeID)))
        return self

    def is_used(self, nodeID):
        return self._pnet.nodes[nodeID]["server"] is not None

    def is_server(self, nodeID):
        return self._pnet.nodes[nodeID]["server"] == True

    def is_entry(self, nodeID):
        return self._pnet.nodes[nodeID]["server"] == False