from experiments.loader import YamlLoader, YamlLoader


loader = YamlLoader("./experiments/data.yaml")
print(loader.cnf)
print(type(loader.cnf))