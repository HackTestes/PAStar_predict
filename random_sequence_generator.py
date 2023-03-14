import random
import sys

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
def seq_random_execution_unit(seq_dictionary: [str], seq_size: int, seq_size_step: int, samples_per_size: int, max_samples: int, seq_per_execution: int, action ):

    # Remainder must be 0
    if (max_samples%samples_per_size != 0):
        raise Exception('Remainder must be 0 between max samples and unique seqences')

    # Calculate random samples util the max amount is reached
    for sample_bucket_idx in range( int(max_samples/samples_per_size) ):
        for sample_idx in range( samples_per_size ):
            action( random_seq_list(seq_dictionary, seq_size, seq_per_execution) )

        seq_size += seq_size_step