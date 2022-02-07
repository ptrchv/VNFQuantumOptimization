# %%
import dimod
from dimod import sampleset
import tabu
import neal
import time
import numpy
import scipy
from vnfplacement.vnf import VNF
from vnfplacement.sfc import SFC
from vnfplacement.problem_network import ProblemNetwork
from vnfplacement.qubo_form import QuboFormulation
from vnfplacement.defines import NodeProperty, LinkProperty, PropertyType, QuboExpression
import networkx as nx
import matplotlib
import matplotlib.pyplot as plt
import config
from dwave.cloud import Client
from dwave.system.samplers import DWaveSampler
from dwave.system.composites import EmbeddingComposite
from dwave.system.composites import FixedEmbeddingComposite
import dwave.inspector



def qubo_random_gen(init_seed, graph_size, edge_prob, num_sfcs, num_vnfs): 
    #random network topology generation
    net = ProblemNetwork.from_random_gen(graph_size, edge_prob, init_seed)
    net.draw()
    start_form = time.time()
    #adding VNFs and SFCs
    for i in range(num_sfcs):
        sfc = SFC("generic_secaas_"+str(i))
        sfc.set_properties(PropertyType.DRAWBACK, {LinkProperty.DELAY : 1.0})
        sfc.set_properties(PropertyType.RESOURCE, {LinkProperty.BANDWIDTH: 1.0})
        for j in range(num_vnfs):
            sfc = sfc.append_vnf(VNF("firewall", {NodeProperty.MEMORY : 2, NodeProperty.CPU : 2}))
        net.add_sfc(sfc)
    
    #adding net properties
    for n in list(net.nodes):
        net.set_node_properties(n, PropertyType.RESOURCE, {NodeProperty.MEMORY : 3, NodeProperty.CPU : 3})
        net.set_node_properties(n, PropertyType.COST, {NodeProperty.MEMORY : 1, NodeProperty.CPU : 1})
    for l in net.links:
        net.set_link_properties(l, PropertyType.RESOURCE, {LinkProperty.BANDWIDTH : 1})
        net.set_link_properties(l, PropertyType.COST, {LinkProperty.BANDWIDTH : 1})
        net.set_link_properties(l, PropertyType.DRAWBACK, {LinkProperty.DELAY : 0.2})

    # qubo formulation details
    discretization = {
        LinkProperty.BANDWIDTH : 1,
        LinkProperty.DELAY : 1,
        NodeProperty.CPU : 1,
        NodeProperty.MEMORY : 1,
        NodeProperty.STORAGE : 50
    }

    lagranges = {
        QuboExpression.LINK_RES: 2,
        QuboExpression.LINK_DRAW: 2,
        QuboExpression.NODE_RES: 2,
        QuboExpression.ALLOCATION: 20,
        QuboExpression.CONTINUITY: 20
    }

    disabled = [QuboExpression.NODE_COST, QuboExpression.LINK_COST]

    # generating QUBO formulation
    qf = QuboFormulation(net, disabled, lagranges, discretization)
    end_form = time.time() - start_form
    return net, qf, end_form

def sa_solver(qf, reads):
    solver = neal.SimulatedAnnealingSampler()
    start_time = time.time()
    sampleset = solver.sample(qf.qubo, num_reads=reads)
    exec_time = time.time() - start_time
    optimum = sampleset.first.sample

    return sampleset, optimum, exec_time

def tabu_solver(qf):
    solver = tabu.TabuSampler()
    start_time = time.time()
    sampleset = solver.sample(qf.qubo)
    exec_time = time.time() - start_time
    optimum = sampleset.first.sample
    return sampleset, optimum, exec_time

def qa_solver(qf, reads, chain_str, timeout_emb):
    client = Client.from_config(token=config.api_token)
    print(client.get_solvers())
    device = DWaveSampler(token = config.api_token)
    print(device)
    solver = EmbeddingComposite(device)
    sampleset = solver.sample(qf.qubo, num_reads=reads, embedding_parameters=dict(timeout=timeout_emb), chain_strength=chain_str)
    optimum = sampleset.first.sample
    dwave.inspector.show(sampleset)

    return sampleset, optimum, -1

def nx_view_first(qf, net, optimum):
    color_map = []
    chosen_node = []
    for var in optimum:
        # print("var: {} set: {}".format(var,optimum[var]))
        if optimum[var] == 1 and not "S" in var:
            print(var)
            nodei = qf._var_to_ids(var)[0][0]
            nodef = qf._var_to_ids(var)[0][1]
            chosen_node.append(nodei)
            chosen_node.append(nodef)
    for node in net.nodes:
        if node in chosen_node:
            color_map.append('red')
        else: 
            color_map.append('cyan')

    nx.draw(net._pnet, node_color=color_map, with_labels=True)

def nx_view_bests(qf, net, sampleset, threshold):
    counter = 0
    for best, energy in sampleset.data(fields=['sample','energy'], sorted_by='energy'):
        if counter < threshold:
            counter += 1
            varList = []
            color_map = []
            chosen_node = []
            for var, val in best.items():
                if val == 1:
                    if not qf.is_slack(var):   
                        varList.append(var)  
                        nodei = qf._var_to_ids(var)[0][0]
                        nodef = qf._var_to_ids(var)[0][1]
                        chosen_node.append(nodei)
                        chosen_node.append(nodef)
            for node in net.nodes:
                if node in chosen_node:
                    color_map.append('red')
                else: 
                    color_map.append('cyan')
            fig, ax = plt.subplots(1,1)
            ax.text(-1, -1, str(varList) + str(energy), fontsize=10)
            nx.draw(net._pnet, node_color=color_map, with_labels=True, ax = ax) 

# %%

net, quboex, end_form = qubo_random_gen(333,7,0.4,1,3)
print("Vars: "+str(len(quboex.qubo.variables))+" Nodes: "+str(len(net.nodes))+" Edges: "+str(len(net.links)))
print("QUBO formulation time: "+str(end_form)+"s")
sampleset, optimum, time = qa_solver(quboex, 10, 100, 200)
print("SA annealing time: "+str(time)+"s")
nx_view_bests(quboex, net, sampleset, 5)