import os
import subprocess
import math
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
        pastar_output = subprocess.check_output(command, shell=False, timeout=10)

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

    seq_dictionary =['A', 'T', 'C', 'G']
    initial_seq_size = 10
    seq_size_step = 2
    unique_samples_per_size = 1000
    max_samples = 10000
    samples_per_execution = 3

    # Create OR load sequence database
    for test_input in random_sequence_generator.ExecutionPolicy_EqualSizeSeq(seq_dictionary, initial_seq_size, seq_size_step, unique_samples_per_size, max_samples, samples_per_execution):

        # Build input
        tmp_file_path = "/tmp/pastar_input.fasta"

        with TmpFile(tmp_file_path) as tmp_file:
            clear_and_replace(sequence_formatter.formatt_seq(test_input, "fasta"), tmp_file.write_handle)

            ## Execute PAStar and collect metrics from program's exit
            try:
                result = execute_pastar(["../PAStar/astar_msa/bin/msa_pastar", "-t", "24", tmp_file_path])

            except subprocess.TimeoutExpired as e:
                print(f"Result: {result['stdout']} \n Error: Timeout: \n Input: {test_input}")

            # Node info (max)
            node_info = pastar_get_node_info(result['stdout'])

            worst_case = len(test_input[0]) ** len(test_input)
            ratio = math.ceil((node_info['Total']/worst_case)*100)
            print(f"Nodes searched: { node_info['Total'] } -- Worst case {worst_case} -- Ratio {ratio}% -- Input: {test_input} -- Exit code: {result['exit_code']}")

            # VmPeak and RSS might be added later

            # Save results in a specific format -> might use pickle or feather

if __name__ == '__main__':
    main()