import random
import sys
import pandas as pd
import gzip
import configuration
import math

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

    # Small samples must have enough combinations to get the necessary amount of unique combinations or else, this becomes an infinite loop!-> TODO: This logic might need more work to avoid this problem
    while ( current_unique_samples < list_size):

        # Create the random sequence
        current_seq = random_seq(seq_dictionary, seq_size)

        # Verify uniqueness
        if( current_seq in unique_sequences_set ):
            continue

        # Add to the set
        unique_sequences_set.add(current_seq)
        current_unique_samples += 1

    return list(unique_sequences_set)

def most_different_list(seq_dictionary: [str], seq_size: int, list_size: int):
    sequences = []
    tmp_dictionary = seq_dictionary.copy()

    for seq in range(0, list_size):

        # The tmp dict is empty, restore all elements
        # This is needed for lists bigger than the dictionary (yeah, this is bound to repeat some letters) 
        if len(tmp_dictionary) == 0:
            tmp_dictionary = seq_dictionary.copy()

        # Select a random letter from the dictionary
        letter_idx = random.SystemRandom().randrange(len(tmp_dictionary))
        letter = tmp_dictionary[letter_idx]

        # Create a sequence with just this letter
        sequences.append( letter*seq_size )

        # Remove this letterm from tmp, so in the next time we will pick a different one
        tmp_dictionary.pop(letter_idx)

    return sequences



# Not necessary
def calculate_combinations(number_of_elements_in_setN, number_of_elements_in_the_combnation_set):
    # Combination formula
    combinations = (math.factorial(number_of_elements_in_setN)) / ( math.factorial(number_of_elements_in_the_combnation_set) * math.factorial(number_of_elements_in_setN - number_of_elements_in_the_combnation_set) )

    return combinations

# Not necessary
# Get how much a column is worth in similarity
# num_cols is the same thing as the size of the sequences
def calculate_col_similarity_value(num_cols, combinations):
    total = num_cols * combinations
    similarity_of_col = combinations / total

    return similarity_of_col

# Yes, this calculatio is safe to use, because it only takes in consideration the columns
def calculate_min_cols_for_target_similarity(target_similarity_percentage, seq_size):
    return math.ceil(target_similarity_percentage / 100 * seq_size)

# DEPRECATED
## This will generate an entire list of random sequences, all unique
#def seq_random_gen(seq_dictionary: [str], current_seq_size: int, seq_size_steps: int, unique_samples_per_size: int, max_samples: int):
#
#    # Holds the final results
#    sequences_list = []
#    unique_sequences_set: set = {''}
#
#    # Remainder must be 0
#    if (max_samples%unique_samples_per_size != 0):
#        raise Exception('Remainder must be 0 between max samples and unique seqences')
#
#    # Calculate random samples util the max amount is reached
#    for sample_bucket_idx in range( int(max_samples/unique_samples_per_size) ):
#        sequences_list.append( random_seq_list(seq_dictionary, current_seq_size, unique_samples_per_size) )
#        current_seq_size += seq_size_steps
#
#    return sequences_list


# Geberate sequences with 100% similarity
class ExecutionPolicy_MaxSimilarity:

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

        # Get the current multiplier
        current_step = math.floor((self.current_sample)/self.samples_per_size)
        if current_step != 0:
            self.seq_size = self.initial_size + current_step * self.size_step # Since there is addition, we must have an if

        self.current_sample += 1

        equal_sequences = random_seq_list(self.dict, self.seq_size, 1) * self.seq_per_execution

        return (self.current_sample-1, equal_sequences)

# Generate multiple sequences of the same size with random letters from the dictionary (DNA, RNA...)
class ExecutionPolicy_EqualSizeSeq:

    def __init__(self, seq_dictionary: [str], seq_size: int, seq_size_step: int, samples_per_size: int, max_samples: int, seq_per_execution: int, execs_per_sample: int, start_sample_idx: int = 0, start_execution_idx: int = 0):
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
        self.executions_per_sample = execs_per_sample

        # Initial state
        self.current_sample = start_sample_idx
        self.num_of_executions = start_execution_idx

        # Store the responses
        self.update_seq_size()
        self.sample = self.select_start_sequence()

    def __iter__(self):
        return self

    def __next__(self):

        self.update_seq_size()

        # All the executions were done, compute a new sample
        if self.num_of_executions == self.executions_per_sample:
            self.current_sample += 1
            self.num_of_executions = 0
            self.update_seq_size()

            self.sample = random_seq_list(self.dict, self.seq_size, self.seq_per_execution)

        if (self.current_sample == self.max_samples):
            raise StopIteration

        self.num_of_executions += 1

        return (self.current_sample, self.num_of_executions, self.sample)

    def update_seq_size(self):
        # Get the current multiplier
        current_step = math.floor((self.current_sample)/self.samples_per_size)

        # Calculate the new sequence size based on the sample idx, initial size and the step
        if current_step != 0:
            self.seq_size = self.initial_size + current_step * self.size_step # Since there is addition, we must have an if

    # THis is in case we need to restore an old sequence set
    def select_start_sequence(self):
        sample = None

        # You can safely generate a new one
        if configuration.last_sequence_set == None:
            sample = random_seq_list(self.dict, self.seq_size, self.seq_per_execution)

        # There is a sequence to restore from
        else:
            sample = configuration.last_sequence_set

        return sample

class SequenceDatabase:
    def __init__(self, path: str, start_line: int):
        self.file_database = open(path, 'r', encoding='utf-8')
        self.start_line = start_line
        self.set_start_position()

    def get(self):
        line = self.file_database.readline().replace('\n','') # Readline also returns \n, so it needs to be removed
        if len(line) != 0:
            return line
        else:
            return None

    def set_start_position(self):
        # Range in is not inclusive -> go to the specified line
        for line_idx in range(0, self.start_line):
            self.file_database.readline()

        # We are now at the correct line in the file


# Load a database of sequences for execution
class ExecutionPolicy_IterDatabase:

    def __init__(self, seq_database_path: str, execs_per_sample: int, start_sample_idx: int = 0, start_execution_idx: int = 0):

        self.seq_database = SequenceDatabase(seq_database_path, start_sample_idx)
        self.executions_per_sample = execs_per_sample

        # Initial state
        self.current_sample = start_sample_idx
        self.num_of_executions = start_execution_idx

        # Store results for the same sample
        self.sample = self.seq_database.get()

        print('Database loaded')

    def __iter__(self):
        return self

    def __next__(self):

        # Get the results for the next sample
        if self.num_of_executions == self.executions_per_sample:
            self.current_sample += 1
            self.num_of_executions = 0
            self.sample = self.seq_database.get()

        if (self.sample == None):
            raise StopIteration

        self.num_of_executions += 1
        sample = self.sample.split("-")

        return (self.current_sample, self.num_of_executions, sample)


# Custom reader, so we can use depency injection when testing
def file_open(path: str):
    with open(path, 'r', encoding='utf-8') as file:
        list_of_sequences = file.read().split("\n")

        # Remove empty last cell
        if(len(list_of_sequences[-1]) == 0):
            list_of_sequences.pop()

        return list_of_sequences

# DEPRECATED POLICY!

#def open_hdf_sequence_database(path: str):
#    pd.read_hdf(path).Sequences.values
#
## Load a database of sequences for execution
#class ExecutionPolicy_ReadyDatabase:
#
#    def __init__(self, seq_database_path: str, database_reader = file_open, current_sample_idx: int = 0):
#
#        self.seq_database = database_reader(seq_database_path)
#
#        # Initial state
#        self.current_sample = current_sample_idx
#
#        print('Database loaded')
#
#    def __iter__(self):
#        return self
#
#    def __next__(self):
#        if (self.current_sample == len(self.seq_database)):
#            raise StopIteration
#
#        sample = self.seq_database[self.current_sample].split("-")
#
#        self.current_sample += 1
#
#        return (self.current_sample-1, sample)

# Select the right policy
def load_execution_policy(execution_policy: str, database_reader = file_open):

    match execution_policy:
        case 'load_database':
            return ExecutionPolicy_IterDatabase(configuration.seq_database_path, configuration.executions_per_sample, configuration.start_from_idx, configuration.start_from_execution_idx)
        case 'seq_random_equal_size':
            return ExecutionPolicy_EqualSizeSeq(configuration.seq_dictionary, configuration.initial_seq_size, configuration.seq_size_step, configuration.unique_samples_per_size, configuration.max_samples, configuration.samples_per_execution, configuration.executions_per_sample, configuration.start_from_idx, configuration.start_from_execution_idx)
        case 'seq_max_similarity_equal_size':
            return ExecutionPolicy_MaxSimilarity(configuration.seq_dictionary, configuration.initial_seq_size, configuration.seq_size_step, configuration.unique_samples_per_size, configuration.max_samples, configuration.samples_per_execution, configuration.executions_per_sample, configuration.start_from_idx)
        case _:
            raise Exception('Invalid execution poilicy')
