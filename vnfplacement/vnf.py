import os

class VNF:
    def __init__(self, typeVNF, requirements):
        self.requirements = requirements
        self.typeVNF = typeVNF
    def __str__(self):
        str_rep = str(self.typeVNF) + os.linesep
        for k, v in self.requirements.items():
            str_rep += f"{k.name}: {v}{os.linesep}"
        return str_rep