import random
import sys

# Letters that represent amino acids
seq_dictionary =['A', 'U', 'C', 'G']

# Parameters
current_seq_size = 50
seq_size_steps = 5
uniques_samples_per_size = 100
max_samples = 1000

# Holds the final results
unique_sequences_set = {''}
unique_sequences_set.clear()


# Remainder must be 0
if (max_samples%uniques_samples_per_size != 0):
    sys.exit('Remainder must be 0 between max samples and unique seqences')

print(f"Bucket quantity: {max_samples/uniques_samples_per_size} -- Bucket size: {uniques_samples_per_size}")
print(f"Max amount of samples: {max_samples}")
print(f"Seq size step: {seq_size_steps} -- Max seq size: { (max_samples/uniques_samples_per_size * seq_size_steps) + (current_seq_size - seq_size_steps) } \n\n")


# Calculate random samples util the max amount is reached
for sample_bucket_idx in range( int(max_samples/uniques_samples_per_size) ):

    # Get samples per size
    current_bucket_uniques_samples = 0

    # Small samples must have enough combinations to get the necessary amount of unique combinations or else, this becomes an infinite loop!
    while ( current_bucket_uniques_samples < uniques_samples_per_size):
        current_seq = ""

        # Create the random sequence
        for letter_idx in range(current_seq_size):
            current_seq += seq_dictionary[random.SystemRandom().randrange(len(seq_dictionary))] # Get a random letter from the dictionary

        # Verify uniqueness
        if( current_seq in unique_sequences_set ):
            continue

        # Add to the set
        unique_sequences_set.add(current_seq)
        current_bucket_uniques_samples += 1
        print(f"Current_seq: {current_seq}")

    current_seq_size += seq_size_steps
        


print( len(unique_sequences_set) )