import os
import unittest
import sequence_formatter
import execution_supervisor

class TestMethods(unittest.TestCase):

    def test_sequence_formtting(self):
        self.assertEqual( '>Sequence_1\nAAA\n>Sequence_2\nBBB\n', sequence_formatter.formatt_seq(["AAA", "BBB"], "fasta") )


    def test_tmp_file_creation(self):
        tmp_file_path = "/tmp/pastar_input_test"

        # Can it perform read and write?
        with execution_supervisor.TmpFile(tmp_file_path) as file:
            self.assertTrue(file.write_handle.writable())
            self.assertTrue(file.read_handle.readable())

            self.assertTrue(os.path.exists(tmp_file_path)) # Does it actually exist?

        # Checks if the tmp file was cleaned up
        self.assertFalse(os.path.exists(tmp_file_path))


    def test_clear_and_replace_file(self): 
        error = False
        old_info = "not the right input"
        new_info = "fasta input"
        tmp_file_path = "/tmp/pastar_input_test"

        with execution_supervisor.TmpFile(tmp_file_path) as file:
            for idx in range(3):
                # Write the info we DON'T want
                execution_supervisor.clear_and_replace(old_info, file.write_handle)

                # Replace it with what we want
                execution_supervisor.clear_and_replace(new_info, file.write_handle)

                # Check it
                file.read_handle.seek(0)
                file_content = file.read_handle.read()

                if file_content != new_info:
                    error = True

        self.assertFalse(error)

    def test_execute_program(self):
        command_result = execution_supervisor.execute_pastar(["/usr/bin/true"])
        self.assertEqual(command_result['exit_code'], 0)

    def test_execute_program_check_error_code(self):
        command_result = execution_supervisor.execute_pastar(["/usr/bin/false"])
        self.assertEqual(command_result['exit_code'], 1)

    def test_execute_program_check_output(self):
        output = "hello from my output!"
        command_result = execution_supervisor.execute_pastar(["/usr/bin/echo", output])

        # Echo adds more chars
        self.assertEqual(command_result['stdout'].replace('\'','').replace('b','').replace('\\n','').strip(), output)

    def test_execute_program_node_info(self):
        input = execution_supervisor.execute_pastar(["../PAStar/astar_msa/bin/msa_pastar", "-t", "24", "../PAStar/astar_msa/seqs/3/synthetic_easy.fasta"])['stdout']
        node_info = execution_supervisor.pastar_get_node_info(input)

        self.assertEqual(list(node_info.keys()), ['OpenList', 'ClosedList', 'Reopen', 'Total', 'Open Rewrite'])

    def test_execute_program_save_data(self):
        pass

    def test_random_sequence(self):
        pass


if __name__ == '__main__':
    unittest.main()