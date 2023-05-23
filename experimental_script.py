import os
import resource
import subprocess
import math
import pandas as pd
import configuration
import sequence_formatter
import random_sequence_generator
import numpy as np


#results = pd.read_hdf('./data/SeqResults-SeqDatabase-MaxSize_25000-Seq_5-SizeSample_1-Step_250-Samples_100-Execs_5-threads_8-WSCAD.hdf')
#results.index = range(len(results))
#print(results)
#
#sequences_path = './data/SeqResults-SeqDatabase-MaxSize_25000-Seq_5-SizeSample_1-Step_250-Samples_100-Execs_5-threads_1-WSCAD.hdf'
#
#with open(configuration.seq_database_path, 'r', encoding='utf-8') as file:
#    for i, line in enumerate(file):
#        print("{0}: {1}".format(i,len(line.split('-'))))

#for idx in range(1, 10):
#    print(idx)
#    subprocess.check_output([f'cat /dev/zero | head -c {idx}G | tail'], shell=True) # https://unix.stackexchange.com/questions/99334/how-to-fill-90-of-the-free-memory
#
#    print(resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss)


hist = np.histogram([93.5, 99.7, 93.3, 93.4, 94.3, 94.7, 94.1], density=False, bins=100, range=(0, 100))

print(len(hist[0]), len(hist[1]), hist, sep='\n')