import random
import sys
import pandas as pd
import gzip
import configuration
import math

## Letters that represent amino acids
#seq_dictionary =['A', 'T', 'C', 'G']
#
## Parameters
#current_seq_size = 50
#seq_size_steps = 5
#unique_samples_per_size = 100
#max_samples = 1000

def random_seq(seq_dictionary: [str], seq_size: int):
    random_sequence = ""

    # Create the random sequence
    for letter_idx in range(seq_size):
        random_sequence += seq_dictionary[random.SystemRandom().randrange(len(seq_dictionary))] # Get a random letter from the dictionary

    return random_sequence

def random_seq_list(seq_dictionary: [str], seq_size: int, list_size: int):
    current_unique_samples = 0
    unique_sequences_set: set = {''}
    unique_sequences_set.clear()

    # Small samples must have enough combinations to get the necessary amount of unique combinations or else, this becomes an infinite loop!
    while ( current_unique_samples < list_size): # TODO: This logic might need more work

        # Create the random sequence
        current_seq = random_seq(seq_dictionary, seq_size)

        # Verify uniqueness
        if( current_seq in unique_sequences_set ):
            continue

        # Add to the set
        unique_sequences_set.add(current_seq)
        current_unique_samples += 1

    return list(unique_sequences_set)

# THis will generate an entire list of random sequences, all unique
def seq_random_gen(seq_dictionary: [str], current_seq_size: int, seq_size_steps: int, unique_samples_per_size: int, max_samples: int):

    # Holds the final results
    sequences_list = []
    unique_sequences_set: set = {''}

    # Remainder must be 0
    if (max_samples%unique_samples_per_size != 0):
        raise Exception('Remainder must be 0 between max samples and unique seqences')

    # Calculate random samples util the max amount is reached
    for sample_bucket_idx in range( int(max_samples/unique_samples_per_size) ):
        sequences_list.append( random_seq_list(seq_dictionary, current_seq_size, unique_samples_per_size) )
        current_seq_size += seq_size_steps

    return sequences_list

# This will create a execution unit ->
# Input: sequences of same size
# Action: execute PAStar
#
# This should generate a small sequence list per execition
#def seq_random_execution_unit(seq_dictionary: [str], seq_size: int, seq_size_step: int, samples_per_size: int, max_samples: int, seq_per_execution: int, action ):
#
#    # This captures the exit of the "action", this is to help testing
#    debug_exit = []
#
#    # Remainder must be 0
#    if (max_samples%samples_per_size != 0):
#        raise Exception('Remainder must be 0 between max samples and unique seqences')
#
#    # Calculate random samples util the max amount is reached
#    for sample_bucket_idx in range( int(max_samples/samples_per_size) ):
#        for sample_idx in range( samples_per_size ):
#            action( random_seq_list(seq_dictionary, seq_size, seq_per_execution), debug_exit )
#
#        seq_size += seq_size_step
#
#    return debug_exit

# Generate multiple sequences of the same size with random letters from the dictionary (DNA, RNA...)
class ExecutionPolicy_EqualSizeSeq:

    def __init__(self, seq_dictionary: [str], seq_size: int, seq_size_step: int, samples_per_size: int, max_samples: int, seq_per_execution: int, current_sample_idx: int = 0):
        # Remainder must be 0
        if (max_samples%samples_per_size != 0):
            raise Exception('Remainder must be 0 between max samples and unique seqences')

        # Configuration
        self.dict = seq_dictionary
        self.seq_size = seq_size
        self.initial_size = seq_size
        self.size_step = seq_size_step
        self.samples_per_size = samples_per_size
        self.max_samples = max_samples
        self.seq_per_execution = seq_per_execution

        # Initial state
        self.current_sample = current_sample_idx

    def __iter__(self):
        return self

    def __next__(self):

        if (self.current_sample == self.max_samples):
            raise StopIteration

        # If we hit the step amount, increase the seq size
        #if (self.current_sample != 0 and self.current_sample % self.samples_per_size == 0):
        #    self.seq_size += self.size_step

        # Get the current multiplier
        current_step = math.floor((self.current_sample)/self.samples_per_size)
        if current_step != 0:
            self.seq_size = self.initial_size + current_step * self.size_step # Since there is addition, we must have an if

        self.current_sample += 1

        return (self.current_sample-1, random_seq_list(self.dict, self.seq_size, self.seq_per_execution))

class SequenceDatabase:
    def __init__(self, path: str, start_line: int):
        self.file_database = open(path, 'r', encoding='utf-8')
        self.start_line = start_line
        self.set_start_position()

    def get(self):
        line = self.file_database.readline()
        if len(line) != 0:
            return line
        else:
            return None

    def set_start_position(self):
        # Range in not inclusive -> got to the specified line
        for line_idx in range(0, self.start_line):
            self.file_database.readline()

        # We are now at the correct line in the file


# Load a database of sequences for execution
class ExecutionPolicy_IterDatabase:

    def __init__(self, seq_database_path: str, current_sample_idx: int = 0):

        self.seq_database = SequenceDatabase(seq_database_path, current_sample_idx)

        # Initial state
        self.current_sample = current_sample_idx

        print('Database loaded')

    def __iter__(self):
        return self

    def __next__(self):

        sample = self.seq_database.get()

        if (sample == None):
            raise StopIteration

        sample = sample.split("-")

        self.current_sample += 1

        return (self.current_sample-1, sample)


# Custom reader, so we can use depency injection when testing
def file_open(path: str):
    with open(path, 'r', encoding='utf-8') as file:
        list_of_sequences = file.read().split("\n")

        # Remove empty last cell
        if(len(list_of_sequences[-1]) == 0):
            list_of_sequences.pop()

        return list_of_sequences

def open_hdf_sequence_database(path: str):
    pd.read_hdf(path).Sequences.values

# Load a database of sequences for execution
class ExecutionPolicy_ReadyDatabase:

    def __init__(self, seq_database_path: str, database_reader = file_open, current_sample_idx: int = 0):

        self.seq_database = database_reader(seq_database_path)

        # Initial state
        self.current_sample = current_sample_idx

        print('Database loaded')

    def __iter__(self):
        return self

    def __next__(self):
        if (self.current_sample == len(self.seq_database)):
            raise StopIteration

        sample = self.seq_database[self.current_sample].split("-")

        self.current_sample += 1

        return (self.current_sample-1, sample)

# Select the right policy
def load_execution_policy(execution_policy: str, database_reader = file_open):

    match execution_policy:

        #case 'load_database':
        #    return ExecutionPolicy_ReadyDatabase(configuration.seq_database_path, database_reader, configuration.start_from_idx)
        case 'load_database':
            return ExecutionPolicy_IterDatabase(configuration.seq_database_path, configuration.start_from_idx)
        case 'seq_random_equal_size':
            return ExecutionPolicy_EqualSizeSeq(configuration.seq_dictionary, configuration.initial_seq_size, configuration.seq_size_step, configuration.unique_samples_per_size, configuration.max_samples, configuration.samples_per_execution, configuration.start_from_idx)
        case _:
            raise Exception('Invalid execution poilicy')
