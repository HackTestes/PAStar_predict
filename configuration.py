# This file was created to help configure the fisrt steps of the program
# Also, this centralizes all the configuration

seq_dictionary =['A', 'T', 'C', 'G']
initial_seq_size = 1000
seq_size_step = 100
unique_samples_per_size = 10
max_samples = 10*unique_samples_per_size
samples_per_execution = 3
start_from_idx = 0

max_size = initial_seq_size + ((max_samples/unique_samples_per_size-1) * seq_size_step)


# EXPERIMENTAL
type_of_random_sequences = 'all_random'
size_between_execution_sequences = 'equal'

# If you have a database of sequences to execute, set this to 'load_database'
# seq_random_equal_size
# load_database
execution_policy = 'load_database'
seq_database_name = f'SeqDatabase-MaxSize_{max_size}-Seq_{samples_per_execution}-SizeSample_{unique_samples_per_size}-Step_{seq_size_step}-Samples_{max_samples}'
seq_database_path = f"./sequences/{seq_database_name}"

# How much time to wait before finishing the process and retrying
timeout = 5
timeout_extension_step_size = 50
timeout_time_per_step = 2
failure_time_extension = 5

# How many times we should retry the command
tries_per_execution = 11

# Command
threads = '12'
command = ["../astar_msa/bin/msa_pastar", "-t", threads]

# Results
write_to_file_without_asking = True
result_file_name = f'SeqResults-{seq_database_name}-threads_{threads}.hdf'
result_path = f'./data/{result_file_name}'

# Fractured execution
restore_execution = True
restore_from_path = result_path
append_results = True

# At every X executions, save the results
save_results_frequency = 1