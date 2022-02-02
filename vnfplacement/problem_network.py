import networkx as nx
import networkx as nx

class ProblemNetwork:
    def __init__(self, net, sfcs = None):
        # setup attributes
        self._pnet = net
        self._sfcs = sfcs if sfcs else []

        # check if node is configured
        for n in self._pnet.nodes():
            if not "used" in self._pnet.nodes[n]:
                nx.set_node_attributes(self._pnet, {n: {"used": False}})
    
    # randomly generate graph
    @classmethod
    def from_random_gen(cls, num_nodes, edge_prob, seed = None):
        pnet = nx.fast_gnp_random_graph(num_nodes, edge_prob, seed, directed=False)
        return cls(pnet)
        
    
    # TODO: add node and link informations, colors of server/entry_exit_points
    def draw(self):
        nx.draw(self._pnet, with_labels = True)
    
    @property
    def nodes(self):
        return self._pnet.nodes
    
    @property
    def links(self):
        return self._pnet.edges

    @property
    def net(self):
        return self._pnet

    @property
    def sfcs(self):
        return {k:v for k,v in enumerate(self._sfcs)}

    def are_linked(self, nodeID1, nodeID2):
        return nodeID2 in self._pnet[nodeID1].keys()

    def get_link(self, nodeID1, nodeID2):
        return self._pnet[nodeID1][nodeID2]

    def set_node_properties(self, nodeID, ptype, properties):
        # mark node as used
        self._pnet.nodes[nodeID]["used"] = True

        # add node properties as cost and resource 
        atr = {nodeID : {ptype : properties}}
        nx.set_node_attributes(self._pnet, atr)

    def set_link_properties(self, edgeID, ptype, properties):
        nx.set_edge_attributes(self._pnet, {edgeID : {ptype : properties}})
        return self

    def add_sfc(self, sfc, startNodeID = None, endNodeID = None):
        #add sfc and save entry and exit points
        self._sfcs.append(sfc)
        return self

    def is_used(self, nodeID):
        return self._pnet.nodes[nodeID]["used"]



