# This file was created to help configure the fisrt steps of the program
# Also, this centralizes all the configuration

seq_dictionary =['A', 'T', 'C', 'G']
initial_seq_size = 50
seq_size_step = 50
unique_samples_per_size = 40
max_samples = 400
samples_per_execution = 5

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
tries_per_execution = 10

# Command
threads = '1'
command = ["../PAStar/astar_msa/bin/msa_pastar", "-t", threads]

# Results
write_to_file_without_asking = True
result_path = f'./data/SeqResults-{seq_database_name}-threads_{threads}.feather'