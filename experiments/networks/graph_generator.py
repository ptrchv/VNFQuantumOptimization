# %%
from pyvis.network import Network as net
import networkx as nx


def read_net_graphml(path):
    
    nxg = nx.read_graphml(path)

    cost_memory = nxg.graph["node_default"]["cost_memory"]
    cost_cpu = nxg.graph["node_default"]["cost_cpu"]
    resource_memory = nxg.graph["node_default"]["resource_memory"]
    resource_cpu = nxg.graph["node_default"]["resource_cpu"]

    cost_bandwidth = nxg.graph["edge_default"]["cost_bandwidth"]
    resource_bandwidth = nxg.graph["edge_default"]["resource_bandwidth"]
    drawback_delay = nxg.graph["edge_default"]["drawback_delay"]

    for node, data in nxg.nodes(data=True):
        if "cost_memory" not in data:
            data["cost_memory"] = cost_memory
        if "cost_cpu" not in data:
            data["cost_cpu"] = cost_cpu
        if "resource_memory" not in data:
            data["resource_memory"] = resource_memory
        if "resource_cpu" not in data:
            data["resource_cpu"] = resource_cpu


    for u, v, data in nxg.edges(data=True):
        if "cost_bandwidth" not in data:
            data["cost_bandwidth"] = cost_bandwidth
        if "resource_bandwidth" not in data:
            data["resource_bandwidth"] = resource_bandwidth
        if "drawback_delay" not in data:
            data["drawback_delay"] = drawback_delay

    return nxg

def main():
    g=net()

    topology = read_net_graphml("test.graphml")
    print(topology.edges(data="resource_bandwidth"))

    # drawing
    nx.draw(topology, with_labels = True)
    # g.from_nx(nxg)
    # g.show_buttons(filter_=['physics'])
    # g.show("example.html")


if __name__ == "__main__":
    main()








# %%
