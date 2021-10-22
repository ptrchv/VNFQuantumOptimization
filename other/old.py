import random
import networkx as nx

color_switch = "yellow"
color_server = "orange"

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