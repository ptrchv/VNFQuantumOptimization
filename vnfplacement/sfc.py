import textwrap
import os

class SFC:
    def __init__(self, name):
        self.name = name
        self._vnfs = []
        self._properties = {}

    @property
    def vnfs(self):
        return {k:v for k,v in enumerate(self._vnfs)}

    def set_properties(self, type, properties):
        self._properties[type] = properties

    def append_vnf(self, vnf):
        self._vnfs.append(vnf)
        return self
    
    def get_properties(self, ptype):
        if ptype in self._properties.keys():
            return self._properties[ptype]
        return dict()

    def __len__(self):
        return len(self._vnfs)

    def __str__(self):
        #name
        str_rep = f"{self.name}:{os.linesep}"
        # vnfs
        for vnf in self._vnfs:
            vnf_str = textwrap.indent(str(vnf), "\t")
            str_rep += f"{vnf_str}{os.linesep}"
        #properties
        for k, properties in self._properties.items():
            for p,v in properties.items():
                str_rep += textwrap.indent(f"{str(p)} {v}{os.linesep}", "\t")
        return str_rep