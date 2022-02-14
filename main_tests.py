# %%
from random import sample
import dimod
import csv
from dimod import sampleset
from experiments.visualization import ProblemVisualization
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
from datetime import datetime
import yaml
from experiments.network_loader import NetworkLoader
from test_loader import YamlLoader
import os



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

def tabu_solver(qf, reads):
    solver = tabu.TabuSampler()
    start_time = time.time()
    sampleset = solver.sample(qf.qubo, num_reads=reads)
    exec_time = time.time() - start_time
    optimum = sampleset.first.sample
    return sampleset, optimum, exec_time

def qa_solver(qf, reads, chain_str, timeout_emb, anneal_time):
    client = Client.from_config(token=config.api_token)
    print(client.get_solvers())
    device = DWaveSampler(token = config.api_token)
    print(device)
    solver = EmbeddingComposite(device)
    sampleset = solver.sample(qf.qubo, num_reads=reads, embedding_parameters=dict(timeout=timeout_emb), chain_strength=chain_str, annealing_time=anneal_time)
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

def prettify_legend(qf, vars):
    var_list = []
    sfc_dict = {}
    final_results = ""
    for var in vars:
        var_list.append(qf._var_to_ids(var))
    var_list.sort(key=lambda x: (x[1], x[2][0]))
    for elem in var_list:
        if str(elem[1]) not in sfc_dict:
            sfc_dict[str(elem[1])] = [elem]
        else:
            sfc_dict[str(elem[1])].append(elem)
    for sfc in sfc_dict:
        final_results += "S"+str(sfc)+": "
        curr = 0
        for elem in sfc_dict[sfc]:
            if curr != elem[2][0]:
                final_results += "ERR VNFs Continuity "
                break
            curr = elem[2][1]
            final_results += "("+str(elem[0][0])+"-"+str(elem[0][1])+") "
    return final_results

        
def nx_view_bests(qf, net, sampleset, threshold, filepath, fileinfo):
    if not os.path.exists(filepath):
        os.mkdir(filepath)
    ProblemVisualization.render_net(net, filepath+"net_res.html")
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
            ax.text(-1, -1, prettify_legend(qf, varList) + " E: " +str(round(energy,4)), fontsize=10)
            nx.draw(net._pnet, node_color=color_map, with_labels=True, ax = ax)
            plt.savefig(filepath+fileinfo+"_sample_"+str(counter)+".png", dpi=150, bbox_inches='tight') 

def auto_test_classic_solver(seed, conn, min_nodes, min_sfc, min_vnf, max_nodes, max_sfc, max_vnf, num_read, filepath):
    for i in range(min_nodes, max_nodes):
        for j in range(min_sfc, max_sfc):
            for k in range(min_vnf, max_vnf):
                
                net, quboex, end_form = qubo_random_gen(seed,i,conn,j,k)
                print("QUBO formulation time: "+str(end_form)+"s"+" ")
                
                sampleset_tabu, optimum_tabu, time_tabu = tabu_solver(quboex,num_read)
                print("Tabu time: "+str(time_tabu)+"s"+" ")
                nx_view_bests(quboex, net, sampleset_tabu, 2, filepath,"nodes_"+str(i)+"_s_"+str(j)+"_v_"+str(k)+"_tabu")
                write_tabu_results("auto", "auto_gen", "auto_secaas", quboex, end_form, num_read, time_tabu, sampleset_tabu, "results/auto.csv",i,len(net.links),j,k)
                
                sampleset_sa, optimum_sa, time_sa = tabu_solver(quboex,num_read)
                print("SA annealing time: "+str(time_sa)+"s"+"\n")
                nx_view_bests(quboex, net, sampleset_sa, 2, filepath, "nodes_"+str(i)+"_s_"+str(j)+"_v_"+str(k)+"_sa")
                write_sa_results("auto", "auto_gen", "auto_secaas", quboex, end_form, num_read, time_sa, sampleset_sa, "results/auto.csv",i,len(net.links),j,k)

def write_results(data, qpu_data, filepath):

    data_list = [
        datetime.now(), 
        data['test_name'],
        data['topology'],
        data['sfc'],
        data['nodes'],
        data['links'],
        data['sfc_num'],
        data['vnf_num'],
        data['solver'],
        data['qubo_vars_num'],
        qpu_data['target_var_num'],
        data['tabu_time'],
        data['sa_time'],
        (qpu_data['qpu_access_time'] + qpu_data['total_post_processing_time']),
        qpu_data['qpu_access_time'],
        qpu_data['qpu_programming_time'],
        qpu_data['qpu_sampling_time'],
        qpu_data['total_post_processing_time'],
        qpu_data['chain_strength'],
        data['lowest_energy'],
        data['qubo_form_time'],
        qpu_data['qpu_anneal_time_per_sample'],
        data['num_reads'],
        qpu_data['problem_id'],
    ]

    with open(filepath, 'a') as f:
        writer = csv.writer(f)
        writer.writerow(data_list)
        
def template_test():
    net, quboex, end_form = qubo_random_gen(333,10,0.4,3,5)
    print("Vars: "+str(len(quboex.qubo.variables))+" Nodes: "+str(len(net.nodes))+" Edges: "+str(len(net.links)))
    print("QUBO formulation time: "+str(end_form)+"s")
    sampleset, optimum, time = sa_solver(quboex, 100)
    print("SA annealing time: "+str(time)+"s")
    nx_view_bests(quboex, net, sampleset, 5, "example", "")    

def extract_qpu_data(sampleset):
# Those info are retrived given a specific sampleset:
    # qpu_sampling_time
    # qpu_anneal_time_per_sample
    # qpu_readout_time_per_sample
    # qpu_access_time
    # qpu_access_overhead_time
    # qpu_programming_time
    # qpu_delay_time_per_sample
    # post_processing_overhead_time
    # total_post_processing_time
    # problem_id
    # embedding_timeout
    # chain_strength
    # chain_break_method
    # target_var_num

    qpu_data = {}

    for param in sampleset.info['timing']:
        qpu_data[param] = sampleset.info['timing'][param]

    qpu_data['problem_id'] = sampleset.info['problem_id']
    qpu_data['embedding_timeout'] = sampleset.info['embedding_context']['embedding_parameters']['timeout']
    qpu_data['chain_strength'] = sampleset.info['embedding_context']['chain_strength']
    qpu_data['chain_break_method'] = sampleset.info['embedding_context']['chain_break_method']

    qpu_data['target_var_num'] = 0
    for info in sampleset.info['embedding_context']['embedding']:
        qpu_data['target_var_num'] += len(sampleset.info['embedding_context']['embedding'][info])

    return qpu_data
    
def write_qa_results(test_name, topology, sfc_name, qf, qf_time, num_reads, sampleset, filepath, nodes, edges, sfc_num, vnf_num):
    gen_data = {
        'test_name': test_name,
        'topology': topology,
        'sfc': sfc_name,
        'solver': 'qa',
        'qubo_vars_num': len(qf.qubo.variables),
        'tabu_time': '-',
        'sa_time': '-',
        'lowest_energy': sampleset.first.energy,
        'qubo_form_time': qf_time,
        'num_reads': num_reads,
        'nodes': nodes,
        'links': edges,
        'sfc_num': sfc_num,
        'vnf_num': vnf_num
    }

    q_data = extract_qpu_data(sampleset)

    write_results(gen_data, q_data, filepath)

def write_tabu_results(test_name, topology, sfc_name, qf, qf_time, num_reads, ex_time, sampleset, filepath, nodes, edges, sfc_num, vnf_num):
    gen_data = {
        'test_name': test_name,
        'topology': topology,
        'sfc': sfc_name,
        'solver': 'tabu',
        'qubo_vars_num': len(qf.qubo.variables),
        'tabu_time': ex_time,
        'sa_time': '-',
        'lowest_energy': sampleset.first.energy,
        'qubo_form_time': qf_time,
        'num_reads': num_reads,
        'nodes': nodes,
        'links': edges,
        'sfc_num': sfc_num,
        'vnf_num': vnf_num
    }

    q_data = {
        'target_var_num': '-',
        'qpu_access_time': '-',
        'total_post_processing_time': '-',
        'qpu_programming_time': '-',
        'qpu_sampling_time': '-',
        'total_post_processing_time': '-',
        'chain_strength': '-',
        'qpu_anneal_time_per_sample': '-',
        'problem_id': '-'
    }

    write_results(gen_data, q_data, filepath)

def write_sa_results(test_name, topology, sfc_name, qf, qf_time, num_reads, ex_time, sampleset, filepath, nodes, edges, sfc_num, vnf_num):
    gen_data = {
        'test_name': test_name,
        'topology': topology,
        'sfc': sfc_name,
        'solver': 'sa',
        'qubo_vars_num': len(qf.qubo.variables),
        'tabu_time': '-',
        'sa_time': ex_time,
        'lowest_energy': sampleset.first.energy,
        'qubo_form_time': qf_time,
        'num_reads': num_reads,
        'nodes': nodes,
        'links': edges,
        'sfc_num': sfc_num,
        'vnf_num': vnf_num
    }

    q_data = {
        'target_var_num': '-',
        'qpu_access_time': '-',
        'total_post_processing_time': '-',
        'qpu_programming_time': '-',
        'qpu_sampling_time': '-',
        'total_post_processing_time': '-',
        'chain_strength': '-',
        'qpu_anneal_time_per_sample': '-',
        'problem_id': '-'
    }

    write_results(gen_data, q_data, filepath)
    
def test_from_file(test_name, topology, sfc_name, num_reads, result_csv, sfc_num, vnf_num, sample_path, chain_strength, emb_timeout, solver, num_samples, anneal_time):
    loader = YamlLoader(
        fconf = "experiments/conf.yaml",
        fnet = "experiments/networks/graphml"
    )
    
    net, quboex, end_form = loader.build_test("experiments/tests/"+test_name+".yaml")

    print("Test name: "+test_name)
    print("Vars: "+str(len(quboex.qubo.variables))+" Nodes: "+str(len(net.nodes))+" Edges: "+str(len(net.links)))
    print("QUBO formulation time: "+str(end_form)+"s"+" ")

    if solver == 'qa':
        sampleset, optimum, time = qa_solver(quboex, num_reads, chain_strength, emb_timeout, anneal_time)
        write_qa_results(test_name,topology,sfc_name,quboex,end_form,num_reads, sampleset, result_csv, len(net.nodes), len(net.links),sfc_num,vnf_num)

    if solver == 'sa':
        sampleset, optimum, time = sa_solver(quboex, num_reads)
        write_sa_results(test_name,topology,sfc_name,quboex,end_form,num_reads, time, sampleset, result_csv, len(net.nodes), len(net.links),sfc_num,vnf_num)

    if solver == 'tabu':
        sampleset, optimum, time = tabu_solver(quboex, num_reads)
        write_tabu_results(test_name,topology,sfc_name,quboex,end_form,num_reads, time, sampleset, result_csv, len(net.nodes), len(net.links),sfc_num,vnf_num)

    nx_view_bests(quboex, net, sampleset, num_samples, sample_path, solver+"_r"+str(num_reads)+"_cs"+str(chain_strength)+"_at"+str(anneal_time))



# %%

t_name = "test0"

test_from_file(
    t_name,"net0", sfc_name="simple_secaas", num_reads=1000, result_csv="results/"+t_name+".csv", sfc_num=1, vnf_num=2, sample_path="results/"+t_name+"/",chain_strength=100,emb_timeout=200,solver="sa", num_samples=3, anneal_time=20
)


# auto_test_classic_solver(
#     seed=333,conn=0.4,min_nodes=18,
#     min_sfc=5,min_vnf=3,max_nodes=19,max_sfc=6,max_vnf=4,num_read=10,filepath="results/auto/"
# )





