import os
import subprocess
from collections import namedtuple



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
        pastar_output = subprocess.check_output(command)

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
    # Create OR load sequence database

    # Build input

    tmp_file = TmpFile("/tmp/pastar_input.fasta") # /tmp is expected to be a tmpfs mount

    #clear_and_replace("fasta_input", file)

    ## Execute PAStar and collect metrics from program's exit
    result = execute_pastar(["/usr/bin/cat", "/tmp/pastar_input.fasta"])


    # Node info (max)
    node_info = pastar_get_node_info(result['stdout'])

    # VmPeak and RSS might be added later


    # Save results in a specific format

if __name__ == '__main__':
    main()