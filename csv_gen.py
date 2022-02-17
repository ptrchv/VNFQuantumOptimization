#%%
import os
import glob
import pandas as pd
os.chdir("/Users/ignaziopedone/VNFQuantumOptimization/results")

extension = 'csv'
all_filenames = [i for i in glob.glob('*.{}'.format(extension))]
print(all_filenames)

with open('final.csv', 'w') as outfile:
    for file in all_filenames:
        with open(file,'r') as infile:
            outfile.write(infile.read())
