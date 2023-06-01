import os
import resource
import subprocess
import math
import pandas as pd
import configuration
import sequence_formatter
import random_sequence_generator
import numpy as np


results_1 = pd.read_hdf('./data/SeqResults-SeqDatabase-MaxSize_2500-Seq_5-SizeSample_1-Step_500-Samples_5-Execs_3-threads_1-Trim_3-Alba.hdf')
results_1_new = pd.read_hdf('./data/SeqResults-SeqDatabase-MaxSize_2500-Seq_5-SizeSample_1-Step_500-Samples_5-Execs_3-threads_1-Trim_3-Alba-NewData.hdf')

results_8 = pd.read_hdf('./data/SeqResults-SeqDatabase-MaxSize_2500-Seq_5-SizeSample_1-Step_500-Samples_5-Execs_3-threads_8-Trim_3-Alba.hdf')
results_8_new = pd.read_hdf('./data/SeqResults-SeqDatabase-MaxSize_2500-Seq_5-SizeSample_1-Step_500-Samples_5-Execs_3-threads_8-Trim_3-Alba-NewData.hdf')

results_16 = pd.read_hdf('./data/SeqResults-SeqDatabase-MaxSize_2500-Seq_5-SizeSample_1-Step_500-Samples_5-Execs_3-threads_16-Trim_3-Alba.hdf')
results_16_new = pd.read_hdf('./data/SeqResults-SeqDatabase-MaxSize_2500-Seq_5-SizeSample_1-Step_500-Samples_5-Execs_3-threads_16-Trim_3-Alba-NewData.hdf')



print(results_1.loc[results_1['Seq_size'] == 1000])
print(results_1_new.loc[results_1_new['Seq_size'] == 1000])

print(results_8.loc[results_8['Seq_size'] == 1000])
print(results_8_new.loc[results_8_new['Seq_size'] == 1000])

print(results_16.loc[results_16['Seq_size'] == 1000])
print(results_16_new.loc[results_16_new['Seq_size'] == 1000])

#sequences_path = './data/SeqResults-SeqDatabase-MaxSize_25000-Seq_5-SizeSample_1-Step_250-Samples_100-Execs_5-threads_1-WSCAD.hdf'

#with open(configuration.seq_database_path, 'r', encoding='utf-8') as file:
#    for i, line in enumerate(file):
#        print("{0}: {1}".format(i,len(line.split('-'))))

#for idx in range(1, 10):
#    print(idx)
#    subprocess.check_output([f'cat /dev/zero | head -c {idx}G | tail'], shell=True) # https://unix.stackexchange.com/questions/99334/how-to-fill-90-of-the-free-memory
#
#    print(resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss)



