import os
import resource
import subprocess
import math
import pandas as pd
import configuration
import sequence_formatter
import random_sequence_generator
import restore_execution


# This class exists to perform automatic cleanup using the 'with' keyword
class TmpFile:
    def __init__(self, tmp_path):
        self.path = tmp_path
        self.write_handle = open(tmp_path, "w")
        self.read_handle = open(tmp_path, "r", encoding='utf-8')

    def __enter__(self):
        return self

    # Close handles and remove the file
    def __exit__(self, *args):
        self.write_handle.close()
        self.read_handle.close()
        os.remove(self.path)

    def read_file(self):
        # Make sure to start at file beginning
        self.read_handle.seek(0)
        file_contents = self.read_handle.read()

        # Return to the original position, so subsequent reads don't return incorrect results
        self.read_handle.seek(0)

        return file_contents


# Truncate file and write the new input
def clear_and_replace(new_input: str, file_handle):
    file_handle.truncate(0) # Rezise to 0
    file_handle.seek(0) # Change the pointer to the beginnig - not doing this causes weird behaviour
    file_handle.write(new_input)
    file_handle.flush() # Garantees that the file will have it at read


def execute_pastar(command: [str], seq_size=0):
    # Assume at first that the execution was successful
    error_code: int = 0
    pastar_output = ''

    current_timeout = configuration.timeout + (configuration.timeout_time_per_step * math.floor(seq_size / configuration.timeout_extension_step_size))

    try:
        pastar_output = subprocess.check_output(command, shell=False, timeout=current_timeout, stderr=subprocess.STDOUT)

    except subprocess.TimeoutExpired:
        #if (len(pastar_output) == 0):
        error_code = 1
        print(f'Timeout Error')

    # Error code
    except subprocess.CalledProcessError as e:
        # Change in case of errors
        error_code = e.returncode
        print('ERROR\n', e.stdout)

    return {'stdout': str(pastar_output), 'exit_code': error_code}

def get_bin_time_MaxRSS(pastar_output: str):
    return pastar_output.replace("(", "").replace(")", "").split("\\n")[-2]

def pastar_get_node_info(pastar_output: str):
    output = pastar_output.replace("(", '').replace(")", '')

    # Input comes with LETTERS as \\t and \\n, insted of the byte long representation
    output = output.split("\\n")
    output = output[ len(output)-3 ].split("\\t")
    output.pop(0)

    node_info: dict = {}

    # Get each field in that line
    for info in output:
        key_value = info.split(": ")
        node_info.update( {key_value[0]: int(key_value[1])} )

    return node_info

def pastar_get_execution_time(pastar_output: str):
    output = pastar_output.replace("(", '').replace(")", '')

    # Input comes with LETTERS as \\t and \\n, insted of the byte long representation
    output = output.split("\\n")
    output = output[ 4 ].split(": ")[2].replace(" ", "")

    return output

def pastar_get_execution_time_heuristic(pastar_output: str):
    output = pastar_output.replace("(", '').replace(")", '')

    # Input comes with LETTERS as \\t and \\n, insted of the byte long representation
    output = output.split("\\n")
    output = output[ 1 ].split(": ")[1].replace(" ", "")

    return output

def pastar_get_seq_similarity(pastar_output: str):

    output = pastar_output.replace("(", '').replace(")", '')

    # Input comes with LETTERS as \\t and \\n, insted of the byte long representation
    output = output.split("\\n")
    output = output[ 6 ].split(": ")[1].replace(" ", "")

    return output

def pastar_get_version(pastar_output: str):

    output = pastar_output.replace("(", '').replace(")", '')

    # Input comes with LETTERS as \\t and \\n, insted of the byte long representation
    output = output.split("\\n")
    output = output[ 2 ].split(" ")[-1].replace("(", "").replace(")", "")

    return output

def pastar_get_score(pastar_output: str):

    output = pastar_output.replace("(", '').replace(")", '')

    # Input comes with LETTERS as \\t and \\n, insted of the byte long representation
    output = output.split("\\n")
    output = output[ 5 ].split(": ")[1].split("\\t")[0].replace("(", "").replace(")", "")

    return output

def pastar_get_misc(pastar_output: str):

    output = pastar_output.replace("(", '').replace(")", '')

    # Input comes with LETTERS as \\t and \\n, insted of the byte long representation
    output = output.split("\\n")
    output = output[ 5 ].split(": ")[1].split("\\t")[1].replace("(", "").replace(")", "")

    return output

def pastar_get_g_score(pastar_output: str):
    output = pastar_output.replace("(", '').replace(")", '')

    # Input comes with LETTERS as \\t and \\n, insted of the byte long representation
    output = output.split("\\n")
    output = output[ 5 ].split(": ")[1].split("\\t")[1].replace(" - ", ':').split(' ') # Get each value separated by :
    output = output[0].split(":")[1] # Select g and get the value

    return output

def ask_for_confirmation(bypass: bool):
    if bypass != True:
        confirmation = input("Do you want to write to the file?\n")
        return confirmation == 'y'

    return True

def update_timeout(tries):
    if(tries > 1):
        configuration.timeout += configuration.failure_time_extension

def main():

    print(f'Seq-> Max size: {configuration.max_size} \tSamples:{configuration.max_samples} \tBuckets: {(configuration.max_samples/configuration.unique_samples_per_size)} \tNumber of sequences: {configuration.samples_per_execution} \tSamples per size: {configuration.unique_samples_per_size}\n')
    print(f'Command:{configuration.command} \nDatabase path: {configuration.seq_database_path} \nResults path: {configuration.result_path}\n')
    print(f'Execution policy: {configuration.execution_policy}')
    print(f'Restore execution: {configuration.restore_execution}')
    print(f'Write to files without asking: {configuration.write_to_file_without_asking}')
    print(f'Append results: {configuration.append_results}')

    confirmation = input("\nDo you want to continue(y)?\n")

    if(confirmation != "y"):
        quit()

    results = pd.DataFrame(dict(Nodes= [], MaxRSS=[], Seq_qtd=[], Seq_size=[], Execution_time=[], Heuristic_time=[], Similarity=[], Score=[], G_score=[]))
    seq_input = []

    # Restore execution before loading the excution policies
    if configuration.restore_execution == True:
        restore_execution.restore_execution()

    else:
        # Start with new results, so you need to delete the old one
        if os.path.exists(configuration.result_path) and configuration.write_to_file_without_asking == True:
            raise Exception('Results already exist!')
            print('PREVIOUS RESULTS DELETED!')

        # Start with a new seq database, so you need to delete the old one
        if os.path.exists(configuration.seq_database_path) and configuration.execution_policy != 'load_database' and configuration.write_to_file_without_asking == True:
            raise Exception('Sequence database already exist!')

    # Create OR load sequence database
    LoopGenerator = random_sequence_generator.load_execution_policy(configuration.execution_policy)

    tmp_file_path = "/tmp/pastar_input.fasta"
    with TmpFile(tmp_file_path) as tmp_file:

        previous_sample_idx = None

        # Loop over the database and execute the command
        for (current_sample, current_execution, test_input) in LoopGenerator:

            print(f"Current sample: {current_sample} / {configuration.max_samples} \tCurrent execution: {current_execution}")

            # Trim the test input in case we are just interested in some sequences
            test_input = test_input[0:configuration.samples_per_execution]

            # Build input
            #tmp_file_path = "/tmp/pastar_input.fasta"
            tries: int = 0
            exit_code:int = 1

            #with TmpFile(tmp_file_path) as tmp_file:
            clear_and_replace(sequence_formatter.formatt_seq(test_input, "fasta"), tmp_file.write_handle)

            print(f'File size: {os.stat(tmp_file_path).st_size}')
            if configuration.show_file:
                print(f'Squence Tmp File:\n--------------------------\n\n{tmp_file.read_file()}\n\n--------------------------\n')

            # Debug
            if configuration.show_sequences == True:
                print(f'Sequences: {test_input}')

            # Keep trying in case of erros until you hit the limit
            while(exit_code != 0 and tries < configuration.tries_per_execution):
                # Execute PAStar and collect metrics from program's exit
                result = execute_pastar(configuration.command+[tmp_file_path], len(test_input[0]))
                exit_code = result['exit_code']
                tries += 1
                update_timeout(tries)

            # There is no need to store faulty executions
            if(exit_code != 0):
                print('FAILED EXECUTION')
                continue

            # Max RSS -> maximum amount of physical memory used
            # This ideia might help: https://stackoverflow.com/questions/743955/memory-usage-of-a-child-process (using 2 forks before measuring the MaxRSS, but GNU time solves the problem)
            max_rss = int(get_bin_time_MaxRSS(result['stdout']))#resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss

            # Node info (max)
            node_info = pastar_get_node_info(result['stdout'])['Total']

            # Score
            score = pastar_get_score(result['stdout'])

            # Execution time
            exec_time = pastar_get_execution_time(result['stdout'])

            # Heuristic time
            heuristic_time = pastar_get_execution_time_heuristic(result['stdout'])

            # Similarity
            similarity = pastar_get_seq_similarity(result['stdout'])

            # Misc (I don1t know the meaning of this)
            g_score = pastar_get_g_score(result['stdout'])

            print(f"Nodes searched: { node_info } \tMaxRSS: {max_rss} \tG: {g_score} \tSimilarity: {similarity} \tExecution time: {[heuristic_time, exec_time]} \tInput size: {len(test_input[0])} \tSeq qtd: {len(test_input)} \tExit code: {result['exit_code']} \tTries: {tries}")

            results = pd.concat([ results, pd.DataFrame(dict(SampleID=[current_sample], Nodes=[node_info], MaxRSS=[max_rss], Seq_qtd=[len(test_input)], Seq_size=[len(test_input[0])], Execution_time=[exec_time], Heuristic_time=[heuristic_time], Similarity=[similarity], Score=[score], G_score=[g_score])) ], ignore_index=True)
            seq_input.append('-'.join(test_input))

            # Save results in the disk and clear what is in memory (append)
            if configuration.append_results == True and configuration.write_to_file_without_asking == True: # and (executions % save_results_frequency == 0)
                results.to_hdf(configuration.result_path, 'Exec_results', complevel=9, append=True, format='table', index=False, min_itemsize=75)
                results.drop(results.index, inplace=True)
                print('RESULTS SAVED!')

                # Do NOT write in the original database
                if(configuration.execution_policy != 'load_database' and previous_sample_idx != current_sample and current_execution == 1):
                    with open(configuration.seq_database_path, 'a') as file: # TODO -> Maybe this file open can be placed before to avoid multiple closes

                        # Join will not add the \n if there is only one input (1 set of 3 sequences for instance)
                        if len(seq_input) != 1:
                            file.write( '\n'.join(seq_input) )
                        else:
                            file.write(seq_input[0] + "\n")

                        seq_input.clear()
                        print('SEQUENCE DATABASE SAVED!')

            # This avoids building up inputs from other executions
            if previous_sample_idx == current_sample:
                seq_input.clear()

            previous_sample_idx = current_sample
            print("\n\n")



    # Save results in a specific format
    print('\n\n', results, sep='')

# This should be removed or updated (append is always superior though)
# Careful with the sequence update, since multiple executions might 
    if(ask_for_confirmation(configuration.write_to_file_without_asking) and configuration.append_results == False):
        results.to_hdf(configuration.result_path, 'Exec_results', complevel=9, format='table', index=False, min_itemsize=75)
        print('RESULTS SAVED!')

#        # Do NOT overwrite the original database
#        if(configuration.execution_policy != 'load_database'):
#            with open(configuration.seq_database_path, 'w') as file:
#                file.write( '\n'.join(seq_input) )
#                print('SEQUENCE DATABASE SAVED!')

if __name__ == '__main__':
    main()