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


def execute_pastar(command: [str]):
    # Assume at first that the execution was successful
    error_code: int = 0
    pastar_output = ''

    try:
        pastar_output = subprocess.check_output(command, shell=False, timeout=configuration.timeout)

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

    for info in output:
        key_value = info.split(": ")
        node_info.update( {key_value[0]: int(key_value[1])} )

    return node_info

def main():

    results = pd.DataFrame(dict(Nodes= [], Seq_qtd=[], Seq_size=[]))
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
            while(exit_code != 0 or tries < configuration.tries_per_execution):
                # Execute PAStar and collect metrics from program's exit
                result = execute_pastar(["../PAStar/astar_msa/bin/msa_pastar", "-t", "24", tmp_file_path])
                exit_code = result['exit_code']
                tries += 1
            
            # There is no need to store faulty executions
            if(exit_code != 0):
                continue

            # Node info (max)
            node_info = pastar_get_node_info(result['stdout'])

            # THis is just to visualize the execution
            worst_case = len(test_input[0]) ** len(test_input)
            ratio = (node_info['Total']/worst_case)*100
            print(f"Nodes searched: { node_info['Total'] } \tWorst case {worst_case} \tRatio {'{:.4f}'.format(ratio)}% \tInput size: {len(test_input[0])} \tSeq qtd: {len(test_input)} \tExit code: {result['exit_code']}")

            results = pd.concat([ results, pd.DataFrame(dict(Nodes=[node_info['Total']], Seq_qtd=[len(test_input)], Seq_size=[len(test_input[0])])) ], ignore_index=True)
            seq_input.append('-'.join(test_input))
            # VmPeak and RSS might be added later

    # Save results in a specific format -> might use pickle or feather
    print(results)

    confirmation = input("Do you want to write to the file?\n")

    if(confirmation == "y"):
        results.to_feather("./data/seq.feather")

        # Do NOT overwrite the original database
        if(configuration.execution_policy != 'load_database'):
            with open(configuration.seq_database_path, 'w') as file:
                file.write( '\n'.join(seq_input) )

if __name__ == '__main__':
    main()