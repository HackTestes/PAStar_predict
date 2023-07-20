import pandas as pd
import configuration

def get_dict_from_file_name(file_name):
    file_tuple_list = list(map(lambda x: tuple(x.split("_")), file_name[0:-8].split('-')))
    file_dict = dict(filter(lambda x: True if len(x) == 2 else False, file_tuple_list))

    return file_dict

# Not optimized code - Yeah, it's the slowest approach
# It just reads line by line and stores the last one
# Simple, but slow
# Alternative: https://stackoverflow.com/questions/46258499/how-to-read-the-last-line-of-a-file-in-python 
def get_last_sequence_set(file_path):
    last_sequence = ''
    tmp_line = ''

    with open(file_path, 'r', encoding='utf-8') as file_database:

        while True:
            tmp_line = file_database.readline().replace('\n','')

            if len(tmp_line) != 0:
                last_sequence = tmp_line

            else:
                break

    return last_sequence.split('-')

# This function alters global variables from file name and contents, take extra care
def restore_execution():
    incomplete_results = pd.read_hdf(configuration.restore_from_path)

    file_properties = get_dict_from_file_name(configuration.result_file_name)

    # Restore executions per sample 
    configuration.executions_per_sample = int(file_properties['Execs'])

    # Restore the current index (sample and execution)
    configuration.start_from_idx = int(len(incomplete_results)/configuration.executions_per_sample) # Current sample

    configuration.start_from_execution_idx = len(incomplete_results) - (configuration.start_from_idx * configuration.executions_per_sample) # How many executions were done on this sample

    if configuration.start_from_execution_idx != 0:
        configuration.last_sequence_set = get_last_sequence_set(configuration.seq_database_path)

    # Original
    #configuration.start_from_idx = len(incomplete_results)

    # Restore initial size
    configuration.initial_seq_size = int(incomplete_results.Seq_size.iloc[0])

    # Restore samples per size
    configuration.unique_samples_per_size = int(file_properties['SizeSample'])

    # Restore size step
    configuration.seq_size_step = int(file_properties['Step'])

    # Restore sequences per execution
    configuration.samples_per_execution = int(incomplete_results.Seq_qtd.iloc[0])

    # Restore max samples
    configuration.max_samples = int(file_properties['Samples']) # TODO test -1

    print(f'Idx: {configuration.start_from_idx} \t InitialSeqSize: {configuration.initial_seq_size} \t SeqSizeStep: {configuration.seq_size_step} \t SamplesPerSize: {configuration.unique_samples_per_size} \t Seq: {configuration.samples_per_execution} \t MaxSamples: {configuration.max_samples} \t ')