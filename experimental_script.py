import os
import resource
import subprocess
import math
import pandas as pd
import configuration
import sequence_formatter
import random_sequence_generator


results = pd.read_hdf('./data/SeqResults-SeqDatabase-MaxSize_2500-Seq_3-SizeSample_1-Step_500-Samples_4-Execs_3-threads_24.hdf')
results.index = range(len(results))
print(results)

sequences_path = './sequences/SeqDatabase-MaxSize_2500-Seq_3-SizeSample_1-Step_500-Samples_4-Execs_3.seq'

with open(configuration.seq_database_path, 'r', encoding='utf-8') as file:
    for i, line in enumerate(file):
        print("{0}: {1}".format(i,len(line.split('-'))))

#for idx in range(1, 10):
#    print(idx)
#    subprocess.check_output([f'cat /dev/zero | head -c {idx}G | tail'], shell=True) # https://unix.stackexchange.com/questions/99334/how-to-fill-90-of-the-free-memory
#
#    print(resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss)