import yaml
from vnfplacement.problem_network import ProblemNetwork
from vnfplacement.qubo_form import QuboFormulation
from vnfplacement.sfc import SFC
from vnfplacement.vnf import VNF
from vnfplacement.defines import NodeProperty, LinkProperty, PropertyType, QuboExpression
import networkx as nx
import copy

class YamlLoader:
    def __init__(self, fconf, fnet):
        # yaml conf
        self._cnf = None

        # loaded objects
        self._vnfs = {}
        self._sfcs = {}
        self._networks = {}
        self._discretization = {}

        # load the conf file
        self._load_config(fconf, fnet)
    
    @property
    def cnf(self):
        return self._cnf

    @property
    def vnfs(self):
        return self._vnfs

    @property
    def sfcs(self):
        return self._sfcs
    
    @property
    def networks(self):
        return self._networks

    @property
    def discretization(self):
        return self._discretization

    # loads configuration file
    def _load_config(self, path, fnet):
        with open(path) as stream:
            self._cnf = yaml.safe_load(stream)
        self._load_discretization()
        self._create_vnfs()
        self._create_sfcs()
        self._load_networks(fnet)
    
    # load discretization from resource file
    def _load_discretization(self):
        for res, val in self._cnf['discretization']['node'].items():
            self._discretization[NodeProperty(res)] =  val
        for res, val in self._cnf['discretization']['link'].items():
            self._discretization[LinkProperty(res)] =  val


    # creates vnfs from file definition
    def _create_vnfs(self):
        for v in self._cnf['vnfs']:
            reqs = {}
            for attr, val in v.items():
                if attr == 'name':
                    name = val
                else:
                    reqs[NodeProperty(attr)] = val
            self._vnfs[name] = VNF(name, reqs)

    # creates sfcs from file definition
    def _create_sfcs(self):        
        for c in self._cnf['sfcs']:
            # save name
            sfc = SFC(c['name'])
            for v in c['vnfs']:
                sfc.append_vnf(self._vnfs[v])
            # add properties to s 
            pkeys = c.keys() - ["name", "vnfs"]            
            for pk in pkeys:
                ptype = PropertyType(pk)
                properties = {}
                for attr, val in c[pk].items():
                    properties[LinkProperty(attr)] = val
                sfc.set_properties(ptype, properties)
            self._sfcs[sfc.name] = sfc
    
    # load graphs from file
    def _load_networks(self, fnet):
        for c in self._cnf['networks']:
            name = c["name"]
            net = nx.read_gpickle(f'{fnet}/{c["file"]}')
            self._networks[name] = ProblemNetwork(net)


    # generate test from fle
    def build_test(self, ftest):
        with open(ftest) as stream:
            test_dict = yaml.safe_load(stream)

        # create full problem network deepcopying elements
        net = copy.deepcopy(self._networks[test_dict['network']])
        for c in test_dict['sfcs']:
            sfc = copy.deepcopy(self._sfcs[c])
            net.add_sfc(sfc)

        # read qubo settings
        disabled = []
        for term in test_dict['disabled']:
            disabled.append(QuboExpression(term))
        lagrange = {}
        for k, v in test_dict['lagrange'].items():
            lagrange[QuboExpression(k)] = v

        # generated qubo
        qf = QuboFormulation(net, disabled, lagrange, self._discretization)
        return net, qf

def main():
    loader = YamlLoader(
        fconf = "./experiments/conf.yaml",
        fnet = "./experiments/networks"
    )
    # print(loader.cnf)    
    # print(loader.vnfs)
    # print(loader.sfcs)
    # print(loader.networks)
    # print(loader.discretization)

    loader.build_test("./experiments/tests/test1.yaml")

   

if __name__ == "__main__":
    main()



