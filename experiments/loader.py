import yaml
from vnfplacement.problem_network import ProblemNetwork
from vnfplacement.sfc import SFC
from vnfplacement.vnf import VNF
from vnfplacement.defines import NodeProperty, LinkProperty, PropertyType

# TODO: use pickle to save graphs

class YamlLoader:
    def __init__(self, fpath):
        # yaml conf
        self._cnf = None

        # loaded objects
        self._vnfs = {}
        self._sfcs = {}
        self._networks = {}

        # load the conf file
        self._load_config(fpath)
    
    @property
    def cnf(self):
        return self._cnf

    @property
    def vnfs(self):
        return self._vnfs

    @property
    def sfcs(self):
        return self._sfcs    

    # loads configuration file
    def _load_config(self, path):
        with open(path) as stream:
            self._cnf = yaml.safe_load(stream)
        self._create_vnfs()
        self._create_sfcs()

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
    


def main():
    loader = YamlLoader("./experiments/data.yaml")
    #print(loader.cnf)    
    print(loader.vnfs)
    print(loader.sfcs)
   

if __name__ == "__main__":
    main()



