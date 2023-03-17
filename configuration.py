# This file was created to help configure the fisrt steps of the program
# Also, this centralizes all the configuration

seq_dictionary =['A', 'T', 'C', 'G']
initial_seq_size = 25
seq_size_step = 25
unique_samples_per_size = 100
max_samples = 500
samples_per_execution = 3

# EXPERIMENTAL
type_of_random_sequences = 'all_random'
size_between_execution_sequences = 'equal'

# If you have a database of sequences to execute, set this to 'load_database'
execution_policy = 'load_database'#'seq_random_equal_size'
seq_database_path = "./sequences/test_seq"

# How much time to wait before finishing the process and retrying
timeout = 3

# How many times we should retry the command
tries_per_execution = 3
