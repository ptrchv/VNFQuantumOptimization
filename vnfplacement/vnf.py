import os

class VNF:
    def __init__(self, name, requirements):
        self._requirements = requirements
        self._name = name
    
    @property
    def name(self):
        return self._name

    @property
    def requirements(self):
        return self._requirements

    def __str__(self):
        str_rep = str(self._name) + os.linesep
        for k, v in self._requirements.items():
            str_rep += f"{k.name}: {v}{os.linesep}"
        return str_rep