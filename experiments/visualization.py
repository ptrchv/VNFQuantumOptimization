#%%

from lib2to3.pytree import Node
import os

from vnfplacement.problem_network import ProblemNetwork
os.chdir('/home/pietro/Documents/PhD/VNFQuantumOptimization/')


#%%
from experiments.network_loader import NetworkLoader
from pyvis.network import Network as PyvisNetwork
from vnfplacement.defines import PropertyType, NodeProperty, LinkProperty
import copy
import networkx as nx

class ProblemVisualization:

    @classmethod
    def render_net(cls, prob_net, fname):
        # create vis network as copy of original network
        vis_net = PyvisNetwork()

        # add node labels
        for node_id, data in prob_net.net.nodes(data = True):
            label = "id: {}".format(node_id)
            for ptype, attr in data.items():
                # skip properties not in define
                try:                    
                    ptype = PropertyType(ptype)
                except ValueError:
                    continue
                # add node property and value to label
                for nodep, val in attr.items():
                    nodep = NodeProperty(nodep)
                    label += "<br> {}_{}: {}".format(ptype.value, nodep.value, val)
            # add node with label to pyvis net
            vis_net.add_node(node_id, title = label)

        # add edge labels
        for nid_1, nid_2, data in prob_net.net.edges(data = True):
            label = "id: ({}, {})".format(nid_1, nid_2)
            for ptype, attr in data.items():
                # skip properties not in define
                try:                    
                    ptype = PropertyType(ptype)
                except ValueError:
                    continue
                # add edge property and value to label
                for nodep, val in attr.items():
                    nodep = LinkProperty(nodep)
                    label += "<br> {}_{}: {}".format(ptype.value, nodep.value, val)
            # add edge with label to pyvis net
            vis_net.add_edge(nid_1, nid_2, title = label)
        
        # render network and save html file
        vis_net.show_buttons(filter_=['physics'])
        vis_net.show(fname)


#%%
def main():
    net = NetworkLoader.from_graphml("./experiments/networks/graphml/net00_small_conn_4_6.graphml")
    # net.draw()
    ProblemVisualization.render_net(net, "example.html")

if __name__ == "__main__":
    main()

# %%
