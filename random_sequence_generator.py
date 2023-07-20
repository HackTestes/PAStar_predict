import random
import sys
import pandas as pd
import gzip
import configuration
import math
import itertools

def random_seq(seq_dictionary: [str], seq_size: int):
    random_sequence = ""

    # Create the random sequence
    for letter_idx in range(seq_size):
        random_sequence += seq_dictionary[random.SystemRandom().randrange(len(seq_dictionary))] # Get a random letter from the dictionary

    return random_sequence

# experimental
def random_seq_experimental(seq_dictionary: [str], seq_size: int):
    random_sequence = ""

    # Cehck for empty sequences
    if seq_size == 0:
        return random_sequence

    # Create the random sequence
    previous_letter_idx = None
    while len(random_sequence) < seq_size:
        letter_idx = random.SystemRandom().randrange(len(seq_dictionary))
        
        #random_sequence += seq_dictionary[letter_idx] * random.SystemRandom().randrange(seq_size)

        # Do not repeat any letters
        if letter_idx != previous_letter_idx:
            random_sequence += seq_dictionary[letter_idx] * int(seq_size/seq_size)#random.SystemRandom().randrange(int(seq_size/5)) # Get a random letter from the dictionary * letter_size -> if this value is equal to 1, it will generate harder sequences to solve

        previous_letter_idx = letter_idx

    return random_sequence[0:seq_size]

def random_seq_list(seq_dictionary: [str], seq_size: int, list_size: int):
    current_unique_samples = 0
    #unique_sequences_set: set = {''}
    unique_sequences_set = []
    unique_sequences_set.clear()

    # Small samples must have enough combinations to get the necessary amount of unique combinations or else, this becomes an infinite loop!-> TODO: This logic might need more work to avoid this problem
    while ( current_unique_samples < list_size):

        # Create the random sequence
        current_seq = random_seq(seq_dictionary, seq_size)

        # Verify uniqueness -> Not necessary since sequences can have 100% similarity
        #if( current_seq in unique_sequences_set ):
        #    continue

        # Add to the set
        #unique_sequences_set.add(current_seq)
        unique_sequences_set.append(current_seq)
        current_unique_samples += 1

    return list(unique_sequences_set)

# The idea of such function is to change a set of X cols (respecting a minimal simlarity), selecting the psosition randomly
# 
def stochastic_position_seq_list(seq_dictionary: [str], seq_size: int, list_size: int, equal_cols: int):

    sequences = []
    for seq in range(list_size):
        sequences.append([seq_dictionary[0]] * seq_size)

    available_positions = list(range(seq_size))

    for col in range(seq_size-equal_cols):

        # Col to be changed
        col_pos = available_positions.pop(random.SystemRandom().randrange(len(available_positions)))
        #print('DEBUG col_pos ', col_pos)

        # Select letters to change each sequence col
        for seq in sequences:
            seq[col_pos] = seq_dictionary[random.SystemRandom().randrange(len(seq_dictionary))]

            #print('DEBUG seq[col_pos] ', seq[col_pos])

    # Format arrays as strings
    result_sequences = []

    for seq in sequences:
        result_sequences.append(''.join(seq))

    return result_sequences


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

# Yes, this calculation is safe to use, because it only takes in consideration the columns
def calculate_min_cols_for_target_similarity(target_similarity_percentage, seq_size):
    return math.ceil(target_similarity_percentage / 100 * seq_size)

# Assume sequences of same size
#def get_lazy_similarity(sequences: [str]):
#    total_size = 0
#    matches = 0
#
#    # Get total size
#    for seq in sequences:
#        total_size += len(seq)
#
#    # Calculate lazy similarity ("lazy", because we don't do any alignment here)
#    for main_seq_idx in range(len(sequences)):
#
#        for compared_seq_idx in range(main_seq_idx+1, len(sequences)):
#
#            for letter_idx in range(len(sequences[main_seq_idx])):
#                if sequences[main_seq_idx][letter_idx] == sequences[compared_seq_idx][letter_idx]:
#                    matches += 1
#
#    similarity = (matches / total_size) * 100 # Percentage
#
#    return similarity

# Assume sequences of same size
def get_percentage_of_equal_cols(sequences: [str]):

    equal_cols = 0
    num_of_cols = len(sequences[0])

    for col_idx in range(num_of_cols):

        unequal_col = False

        for seq in sequences:
            if sequences[0][col_idx] != seq[col_idx]:
                unequal_col = True
                break

        if unequal_col == False:
            equal_cols += 1

    equal_cols_percentage = (equal_cols / num_of_cols) * 100

    return equal_cols_percentage


def merge_sequence_part(num_letters: int, sequence_parts_array):

    # Error check
    if num_letters <= 0:
        raise Exception('Merge: letters must be higher than 0 to merge sequences')

    # Start a counter for each part 
    counter = [0] * len(sequence_parts_array)
    selector_idx = 1
    merged_sequence = ''
    total_seq_size = 0

    # Calculate seq size from its parts
    for part in sequence_parts_array:
        total_seq_size += len(part)

    invert_switch = lambda X : 1 if X == 0 else 0 

    # Merge sequences
    for letter_set in range(0, math.ceil(total_seq_size / num_letters) + 1): # +1 is to get the remaining parts when we get non divisible num_letters

        # Switch part selection
        #if selector_idx == 0:
        #    selector_idx = 1
        #else:
        #    selector_idx = 0

        selector_idx = invert_switch(selector_idx)
        current_counter = counter[selector_idx]

        #print(f'DEBUG: Iter:{letter_set} -> ({sequence_parts_array[selector_idx][current_counter: ]})')
        
        # Check size of the array, is there enough letters left?
        if current_counter + num_letters >= len(sequence_parts_array[selector_idx]):
            # Grab just what is left
            merged_sequence += sequence_parts_array[selector_idx][current_counter: ]

            # Since we got everything from the other part, we can also get the rest of the other part
            selector_idx = invert_switch(selector_idx)
            current_counter = counter[selector_idx]
            merged_sequence += sequence_parts_array[selector_idx][current_counter: ]

            # We won't need another iteration after getting everything
            break

        merged_sequence += sequence_parts_array[selector_idx][current_counter : current_counter+num_letters]
        counter[selector_idx] += num_letters


    return merged_sequence

def select_merge_method(merge_method, sequence_parts, num_letters = 1):
    match merge_method:
        case 'add':
            return sequence_parts[0] + sequence_parts[1]

        case 'mix':
            return merge_sequence_part(num_letters, sequence_parts)

        case _:
            raise Exception('Invalid merge method')


def aggregate_list_generation(seq_dictionary: [str], seq_size: int, list_size: int, minimal_similarity_percentage: int = 0, seq_start = 'random', seq_end = 'random', merge_method = 'add', num_letters = 1):
 
    equal_cols = calculate_min_cols_for_target_similarity(minimal_similarity_percentage, seq_size)
    final_sequences = []
    base_sequences = None

    # Select how the start of the sequences will be generated
    match seq_start:

        case 'equal':
            base_sequences = [[seq_dictionary[0]] * equal_cols] * list_size # DANGER: all arrays might share the same memory

        # Alba's method
        case 'stochastic_pos':

            # generate sequences here
            final_sequences = stochastic_position_seq_list(seq_dictionary, seq_size, list_size, equal_cols)

            return final_sequences

        case 'random':
            base_sequences = random_seq_list(seq_dictionary, equal_cols, 1) * list_size # This will be the base sequence

        case _:
            raise Exception('Invalid start sequence pattern')


    # Select how the end of the sequence will be generated
    match seq_end:

        case 'none':
            pass

        case 'random':
            random_list_end = random_seq_list(seq_dictionary, seq_size - equal_cols, list_size)

            for idx, seq in enumerate(base_sequences):
                final_sequences.append( select_merge_method(merge_method, [seq, random_list_end[idx]], num_letters) )

        case 'most_different':
            most_different_list_end = most_different_list(seq_dictionary, seq_size - equal_cols, list_size)

            for idx, seq in enumerate(base_sequences):
                final_sequences.append( select_merge_method(merge_method, [seq, most_different_list_end[idx]], num_letters) )

        case _:
            raise Exception('Invalid end sequence pattern')

    return final_sequences


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


# DEPRECATED
# Generate sequences with 100% similarity
#class ExecutionPolicy_MaxSimilarity:
#
#    def __init__(self, seq_dictionary: [str], seq_size: int, seq_size_step: int, samples_per_size: int, max_samples: int, seq_per_execution: int, current_sample_idx: int = 0):
#        # Remainder must be 0
#        if (max_samples%samples_per_size != 0):
#            raise Exception('Remainder must be 0 between max samples and unique seqences')
#
#        # Configuration
#        self.dict = seq_dictionary
#        self.seq_size = seq_size
#        self.initial_size = seq_size
#        self.size_step = seq_size_step
#        self.samples_per_size = samples_per_size
#        self.max_samples = max_samples
#        self.seq_per_execution = seq_per_execution
#
#        # Initial state
#        self.current_sample = current_sample_idx
#
#    def __iter__(self):
#        return self
#
#    def __next__(self):
#
#        if (self.current_sample == self.max_samples):
#            raise StopIteration
#
#        # Get the current multiplier
#        current_step = math.floor((self.current_sample)/self.samples_per_size)
#        if current_step != 0:
#            self.seq_size = self.initial_size + current_step * self.size_step # Since there is addition, we must have an if
#
#        self.current_sample += 1
#
#        equal_sequences = random_seq_list(self.dict, self.seq_size, 1) * self.seq_per_execution
#
#        return (self.current_sample-1, equal_sequences)

# Generate multiple sequences of the same size with random letters from the dictionary (DNA, RNA...)
class ExecutionPolicy_EqualSizeSeq:

    def __init__(self, seq_dictionary: [str], seq_size: int, seq_size_step: int, samples_per_size: int, max_samples: int, seq_per_execution: int, execs_per_sample: int, start_sample_idx: int = 0, start_execution_idx: int = 0, target_similarity = 0, seq_start = 'random', seq_end = 'random', merge_method = 'add', num_letters = 1):
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
        self.target_similarity = target_similarity
        self.sequence_start_pattern = seq_start
        self.sequence_end_pattern = seq_end
        self.merge_method = merge_method
        self.num_letters = num_letters

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

            self.sample = aggregate_list_generation(self.dict, self.seq_size, self.seq_per_execution, self.target_similarity, self.sequence_start_pattern, self.sequence_end_pattern, self.merge_method, self.num_letters)

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

    # This is in case we need to restore an old sequence set
    def select_start_sequence(self):
        sample = None

        # You can safely generate a new one
        if configuration.last_sequence_set == None:
            sample = aggregate_list_generation(self.dict, self.seq_size, self.seq_per_execution, self.target_similarity, self.sequence_start_pattern, self.sequence_end_pattern, self.merge_method, self.num_letters)

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

    def __init__(self, seq_database_path: str, execs_per_sample: int, start_sample_idx: int = 0, start_execution_idx: int = 0, max_samples: int = 0):

        self.seq_database = SequenceDatabase(seq_database_path, start_sample_idx)
        self.executions_per_sample = execs_per_sample

        # Initial state
        self.current_sample = start_sample_idx
        self.num_of_executions = start_execution_idx

        # Store results for the same sample
        self.sample = self.seq_database.get()

        self.max_samples = max_samples

        print('Database loaded')

    def __iter__(self):
        return self

    def __next__(self):

        # Get the results for the next sample
        if self.num_of_executions == self.executions_per_sample:
            self.current_sample += 1
            self.num_of_executions = 0
            self.sample = self.seq_database.get()

        if (self.sample == None or (self.current_sample > self.max_samples and self.num_of_executions == 0)):
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
            return ExecutionPolicy_IterDatabase(seq_database_path = configuration.seq_database_path,
                                                execs_per_sample = configuration.executions_per_sample,
                                                start_sample_idx = configuration.start_from_idx,
                                                start_execution_idx = configuration.start_from_execution_idx,
                                                max_samples = configuration.max_samples)
        case 'seq_random_equal_size':
            return ExecutionPolicy_EqualSizeSeq(seq_dictionary = configuration.seq_dictionary,
                                                seq_size = configuration.initial_seq_size,
                                                seq_size_step = configuration.seq_size_step,
                                                samples_per_size = configuration.unique_samples_per_size,
                                                max_samples = configuration.max_samples,
                                                seq_per_execution = configuration.samples_per_execution,
                                                execs_per_sample = configuration.executions_per_sample,
                                                start_sample_idx = configuration.start_from_idx,
                                                start_execution_idx = configuration.start_from_execution_idx,
                                                target_similarity = configuration.minimal_similarity_percentage,
                                                seq_start = configuration.sequence_start_pattern,
                                                seq_end = configuration.sequence_end_pattern,
                                                merge_method = configuration.merge_method,
                                                num_letters = configuration.num_letters)
        case _:
            raise Exception('Invalid execution poilicy')
