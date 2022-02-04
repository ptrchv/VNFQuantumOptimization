# %%
from pyvis.network import Network as net
import networkx as nx
from vnfplacement.defines import PropertyType, NodeProperty, LinkProperty
from vnfplacement.problem_network import ProblemNetwork
import copy

# node name to integer (removes "n")
class NetworkLoader:
    def node_id(name):
        return int(name.replace("n",""))

    @classmethod
    def from_graphml(cls, path):
        # open graph file
        nxg = nx.read_graphml(path)

        # create new network with same node and edges
        net = nx.Graph()
        for n in nxg.nodes():
            net.add_node(cls.node_id(n))
        for n1, n2 in nxg.edges():
            net.add_edge(cls.node_id(n1), cls.node_id(n2))
        
        net = ProblemNetwork(net)

        # load default node properties
        default_node = {}
        for name, val in nxg.graph["node_default"].items():
            str_list = name.split("_")
            if len(str_list) != 2:
                continue
            ptype = PropertyType(str_list[0])
            nprop = NodeProperty(str_list[1])
            if not ptype in default_node:
                default_node[ptype] = {}
            default_node[ptype][nprop] = val

        # load default link properties
        default_link = {}
        for name, val in nxg.graph["edge_default"].items():
            str_list = name.split("_")
            if len(str_list) != 2:
                continue
            ptype = PropertyType(str_list[0])
            nprop = LinkProperty(str_list[1])
            if not ptype in default_link:
                default_link[ptype] = {}
            default_link[ptype][nprop] = val

        # read and add specific node properties
        for node, data in nxg.nodes(data=True):
            node_properties = copy.deepcopy(default_node)
            nid = cls.node_id(node)
            for name, val in data.items():
                str_list = name.split("_")
                if len(str_list) != 2:
                    continue
                ptype = PropertyType(str_list[0])
                nprop = NodeProperty(str_list[1])
                node_properties[ptype][nprop] = val
            for ptype, properties in node_properties.items():
                net.set_node_properties(nid, ptype, properties)        

        # read and add specific edge properties
        for n1, n2, data in nxg.edges(data=True):
            edge_properties = copy.deepcopy(default_link)
            eid = (cls.node_id(n1), cls.node_id(n2))
            for name, val in data.items():
                str_list = name.split("_")
                if len(str_list) != 2:
                    continue
                ptype = PropertyType(str_list[0])
                nprop = LinkProperty(str_list[1])
                edge_properties[ptype][nprop] = val
            for ptype, properties in edge_properties.items():
                net.set_link_properties(eid, ptype, properties)

        return net

def main():
    # read graph file
    net = NetworkLoader.from_graphml("./experiments/networks/graphml/net05_medium_cluster_15_24.graphml")
    print("---------NODES---------")    
    print(net.net.nodes(data = True))
    print("---------EDGES---------")
    print(net.net.edges(data = True))


if __name__ == "__main__":
    main()


# %%
