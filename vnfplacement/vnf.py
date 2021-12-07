import os

class VNF:
    def __init__(self, typeVNF, requirements):
        self._requirements = requirements
        self._typeVNF = typeVNF

    @property
    def requirements(self):
        return self._requirements

    @property
    def typeVNF(self):
        return self._typeVNF

    def __str__(self):
        str_rep = str(self._typeVNF) + os.linesep
        for k, v in self._requirements.items():
            str_rep += f"{k.name}: {v}{os.linesep}"
        return str_rep