import yaml
from vnfplacement.problem_network import ProblemNetwork
from vnfplacement.sfc import SFC
from vnfplacement.vnf import VNF
from vnfplacement.defines import NodeProperty, LinkProperty, PropertyType

class YamlLoader:
    def __init__(self, fpath):
        self._load_file(fpath)
        self._parse_file()

    def _load_file(self, path):
        with open(path) as stream:
            self._cnf = yaml.safe_load(stream)

    def _parse_file(self):
        pass

    @property
    def cnf(self):
        return self._cnf
    


