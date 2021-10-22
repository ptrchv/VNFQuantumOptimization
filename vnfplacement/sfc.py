import textwrap
import os

class SFC:
    def __init__(self, name):
        self.name = name
        self.vnfs = []
        self.properties = {}

    def set_properties(self, type, properties):
        self.properties[type] = properties

    def append_vnf(self, vnf):
        self.vnfs.append(vnf)
        return self

    def __str__(self):
        #name
        str_rep = f"{self.name}:{os.linesep}"
        # vnfs
        for vnf in self.vnfs:
            vnf_str = textwrap.indent(str(vnf), "\t")
            str_rep += f"{vnf_str}{os.linesep}"
        #properties
        for k, properties in self.properties.items():
            for p,v in properties.items():
                str_rep += textwrap.indent(f"{str(p)} {v}{os.linesep}", "\t")
        return str_rep