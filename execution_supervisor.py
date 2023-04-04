import os
import subprocess
import math
import pandas as pd
import configuration
import sequence_formatter
import random_sequence_generator


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
        pastar_output = subprocess.check_output(command, shell=False, timeout=current_timeout)

    except subprocess.TimeoutExpired:
        #if (len(pastar_output) == 0):
        error_code = 1
        print(f'Timeout Error')

    # Error code
    except subprocess.CalledProcessError as e:
        # Change in case of errors
        error_code = e.returncode

    return {'stdout': str(pastar_output), 'exit_code': error_code}

def pastar_get_node_info(pastar_output: str):
    output = pastar_output.replace("(", '').replace(")", '')

    # Input comes with LETTERS as \\t and \\n, insted of the byte long representation
    output = output.split("\\n")
    output = output[ len(output)-2 ].split("\\t")
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


def ask_for_confirmation(bypass: bool):
    if bypass != True:
        confirmation = input("Do you want to write to the file?\n")
        return confirmation == 'y'

    return True

def update_timeout(tries):
    if(tries > 1):
        configuration.timeout += configuration.failure_time_extension

def main():

    print(f'Seq-> Max size: {configuration.max_size} \tBuckets: {(configuration.max_samples/configuration.unique_samples_per_size)} \tNumber of sequences: {configuration.samples_per_execution} \tSamples per step: {configuration.unique_samples_per_size}\n')
    print(f'Command:{configuration.command} \nDatabase: {configuration.seq_database_name} \nResults file: {configuration.result_path}\n')
    print(f'Execution policy: {configuration.execution_policy}')

    confirmation = input("\nDo you want to continue(y)?\n")

    if(confirmation != "y"):
        quit()

    results = pd.DataFrame(dict(Nodes= [], Seq_qtd=[], Seq_size=[], Execution_time=[], Heuristic_time=[], Similarity=[], Score=[], Misc=[]))
    seq_input = []

    # Create OR load sequence database
    LoopGenerator = random_sequence_generator.load_execution_policy(configuration.execution_policy)

    # Loop over the database and execute the command
    for test_input in LoopGenerator:

        # Build input
        tmp_file_path = "/tmp/pastar_input.fasta"
        tries: int = 0
        exit_code:int = 1

        with TmpFile(tmp_file_path) as tmp_file:
            clear_and_replace(sequence_formatter.formatt_seq(test_input, "fasta"), tmp_file.write_handle)

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
            misc = pastar_get_misc(result['stdout'])

            # This is just to visualize the execution
            worst_case = len(test_input[0]) ** len(test_input)
            ratio = (node_info/worst_case)*100
            print(f"Nodes searched: { node_info } \tExecution time: {exec_time} \tInput size: {len(test_input[0])} \tSeq qtd: {len(test_input)} \tExit code: {result['exit_code']} \tTries: {tries}")

            results = pd.concat([ results, pd.DataFrame(dict(Nodes=[node_info], Seq_qtd=[len(test_input)], Seq_size=[len(test_input[0])], Execution_time=[exec_time], Heuristic_time=[heuristic_time], Similarity=[similarity], Score=[score], Misc=[misc])) ], ignore_index=True)
            seq_input.append('-'.join(test_input))
            # VmPeak and RSS might be added later

    # Save results in a specific format -> might use pickle or feather
    print(results)

    if(ask_for_confirmation(configuration.write_to_file_without_asking)):
        results.to_feather(configuration.result_path)
        print('RESULTS SAVED!')

        # Do NOT overwrite the original database
        if(configuration.execution_policy != 'load_database'):
            with open(configuration.seq_database_path, 'w') as file:
                file.write( '\n'.join(seq_input) )
                print('DATABASE SAVED!')

if __name__ == '__main__':
    main()