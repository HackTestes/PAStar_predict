import pandas as pd
import configuration

def get_dict_from_file_name(file_name):
    file_tuple_list = list(map(lambda x: tuple(x.split("_")), file_name[0:-8].split('-')))
    file_dict = dict(filter(lambda x: True if len(x) == 2 else False, file_tuple_list))

    return file_dict

# This function alters global variables, take extra care
def restore_execution():
    incomplete_results = pd.read_hdf(configuration.restore_from_path)

    file_properties = get_dict_from_file_name(configuration.result_file_name)

    # Restore the current index
    configuration.start_from_idx = len(incomplete_results)

    # Restore initial size
    configuration.initial_seq_size = int(incomplete_results.Seq_size.iloc[0])

    # Restore samples per size
    configuration.unique_samples_per_size = int(file_properties['SizeSample'])

    # Restore size step
    configuration.seq_size_step = int(file_properties['Step'])

    # Restore sequences per execution
    configuration.samples_per_execution = int(incomplete_results.Seq_qtd.iloc[0])

    # Restore max samples
    configuration.max_samples = int(file_properties['Samples'])

    print(f'Idx: {configuration.start_from_idx} \t InitialSeqSize: {configuration.initial_seq_size} \t SeqSizeStep: {configuration.seq_size_step} \t SamplesPerSize: {configuration.unique_samples_per_size} \t Seq: {configuration.samples_per_execution} \t MaxSamples: {configuration.max_samples} \t ')