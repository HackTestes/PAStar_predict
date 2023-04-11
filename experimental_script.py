import os
import subprocess
import math
import pandas as pd
import configuration
import sequence_formatter
import random_sequence_generator


results = pd.read_hdf('./data/SeqResults-SeqDatabase-MaxSize_1900.0-Seq_3-SizeSample_10-Step_100-Samples_100-threads_24.hdf')
results.index = range(len(results))
print(results)

results = pd.read_hdf('./data/SeqResults-SeqDatabase-MaxSize_1900.0-Seq_3-SizeSample_10-Step_100-Samples_100-threads_12.hdf')
results.index = range(len(results))
print(results)

sequences_path = './data/SeqDatabase-MaxSize_1900.0-Seq_3-SizeSample_10-Step_100-Samples_100'

with open(configuration.seq_database_path, 'r', encoding='utf-8') as file:
    for i, line in enumerate(file):
        print("{0}: {1}".format(i,len(line.split('-'))))