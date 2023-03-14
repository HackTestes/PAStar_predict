import os
import unittest
import sequence_formatter
import execution_supervisor
import random_sequence_generator

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
        #input = execution_supervisor.execute_pastar(["../PAStar/astar_msa/bin/msa_pastar", "-t", "24", "../PAStar/astar_msa/seqs/3/synthetic_easy.fasta"])['stdout']

        # This is to help the test run faster
        # The input was verified to guarantee correctness
        input = 'b\'Starting pairwise alignments... done!\\nPhase 1 - init heuristic: 00:00.004 s\\nPerforming search with Parallel A-Star (v1.1-48-gece4f08)\\nRunning PA-Star with: 24 threads, Full-Zorder hash, 12 shift.\\nPhase 2: PA-Star running time: 00:01.041 s\\nFinal Score: (231 416 363)\\tg - 26109 (h - 0 f - 26109)\\nSimilarity: 21.55%\\n\\nAAAAA-------------------------AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA-AAA-A---AAA----AAAAAA-------AA-AA--A-------AA-A-A------A-A-----A-A--AAA-A--A-A---A-A----AA-A-A-A------AA-AA-A----------A------A-VL-S--PA--DK--TN-VKAAWGKV--G-AHA-GE-Y--GAEA-L---ER-MFL-------S-FPT-TK---T-YF-----------------PH-----FD-LSH--GSAQVKG-HG-------KK-VADALTN--AVAHVDDMPNA-LSALSDLHAHKLRVDPVNF-KLLSHCLLVTLAAHLPAEFTPAVHASLDKFLASVSTVLTSKYR------\\nAAAAAPPPPPPPPPPPPPPPPPPPPPPPPPAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAPPPPPPPPEKSAVTALPPPPPPPPPPPPPPVHLTPEEKSAVTALWGKVNVDEVGGEALGRLLVVYPWTQRFFESFGDLSTPDAVMGNPKVKAHGKKVLGAFSDGLAHLDNLKGTFATLSELHCDKLHVDPENFRLLGNVLVCVLAHHFGKEFTPPVQAAYQKVVAGVANALAHKYHDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDPPPPPAAAAAAAAADDDDDAAADDDDAPPPPADDDAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA\\nDDDDDDDDDDDDDDDDDDDDDDDDDD----DDDDDDDDDDDDDDDDDDDDDDDDDDDDDPPPPPAAAAAAAAADDDDDAAADDDDAPPPPAD---DDAAAAAAA-AAAAAAAAAAAAAAAAAAA-A-AAA--AA-AAAAAAAAAAAAAAAAAAAAAAAAA-AAAAAAAAAAAAA-AAAAAAAAAAAAAAAAA----AAAVASA-PA--DK--TN-VKAAWGKV--G-AHA-GE-Y-AAAAAGLSDGEWQLVLNVWGKVEADIPGHGQEVLIRLFKGH--------------PETL-EKFDKFKHLKSEDEMKASED-L-----KKHGATVLTALGGILKKKGHHEAEIKPLAQSHATKHKI-PVKYLEFISECIIQVLQSKHPGDFGADAQGAMNKALELFRKDMASNYKELGFQG\\nPhase 3 - backtrace: 00:00.000 s\\nTotal nodes count:\\ntid 0\\tOpenList: 6154\\tClosedList: 156147\\tReopen: 112972\\tTotal: 275273\\t(Open Rewrite: 209121)\\ntid 1\\tOpenList: 7282\\tClosedList: 147782\\tReopen: 118378\\tTotal: 273442\\t(Open Rewrite: 206790)\\ntid 2\\tOpenList: 4351\\tClosedList: 164246\\tReopen: 100076\\tTotal: 268673\\t(Open Rewrite: 188405)\\ntid 3\\tOpenList: 2405\\tClosedList: 169479\\tReopen: 81660\\tTotal: 253544\\t(Open Rewrite: 180729)\\ntid 4\\tOpenList: 13738\\tClosedList: 153931\\tReopen: 88726\\tTotal: 256395\\t(Open Rewrite: 210261)\\ntid 5\\tOpenList: 15516\\tClosedList: 143007\\tReopen: 126583\\tTotal: 285106\\t(Open Rewrite: 207173)\\ntid 6\\tOpenList: 6223\\tClosedList: 155514\\tReopen: 128550\\tTotal: 290287\\t(Open Rewrite: 192958)\\ntid 7\\tOpenList: 5934\\tClosedList: 148754\\tReopen: 134697\\tTotal: 289385\\t(Open Rewrite: 192661)\\ntid 8\\tOpenList: 6579\\tClosedList: 150018\\tReopen: 151311\\tTotal: 307908\\t(Open Rewrite: 214062)\\ntid 9\\tOpenList: 7054\\tClosedList: 140730\\tReopen: 162032\\tTotal: 309816\\t(Open Rewrite: 189486)\\ntid 10\\tOpenList: 5991\\tClosedList: 152300\\tReopen: 129359\\tTotal: 287650\\t(Open Rewrite: 202935)\\ntid 11\\tOpenList: 2806\\tClosedList: 164284\\tReopen: 151472\\tTotal: 318562\\t(Open Rewrite: 184219)\\ntid 12\\tOpenList: 11326\\tClosedList: 148646\\tReopen: 117699\\tTotal: 277671\\t(Open Rewrite: 211667)\\ntid 13\\tOpenList: 11514\\tClosedList: 136167\\tReopen: 149258\\tTotal: 296939\\t(Open Rewrite: 196005)\\ntid 14\\tOpenList: 6896\\tClosedList: 148954\\tReopen: 127576\\tTotal: 283426\\t(Open Rewrite: 199988)\\ntid 15\\tOpenList: 6097\\tClosedList: 136981\\tReopen: 154024\\tTotal: 297102\\t(Open Rewrite: 179180)\\ntid 16\\tOpenList: 4048\\tClosedList: 118174\\tReopen: 190712\\tTotal: 312934\\t(Open Rewrite: 169983)\\ntid 17\\tOpenList: 1673\\tClosedList: 116270\\tReopen: 183714\\tTotal: 301657\\t(Open Rewrite: 122775)\\ntid 18\\tOpenList: 18234\\tClosedList: 107677\\tReopen: 173540\\tTotal: 299451\\t(Open Rewrite: 181963)\\ntid 19\\tOpenList: 10061\\tClosedList: 105781\\tReopen: 197194\\tTotal: 313036\\t(Open Rewrite: 176922)\\ntid 20\\tOpenList: 0\\tClosedList: 96881\\tReopen: 149661\\tTotal: 246542\\t(Open Rewrite: 136211)\\ntid 21\\tOpenList: 365\\tClosedList: 96393\\tReopen: 97821\\tTotal: 194579\\t(Open Rewrite: 129997)\\ntid 22\\tOpenList: 7782\\tClosedList: 115307\\tReopen: 218604\\tTotal: 341693\\t(Open Rewrite: 175135)\\ntid 23\\tOpenList: 7066\\tClosedList: 114724\\tReopen: 194019\\tTotal: 315809\\t(Open Rewrite: 193295)\\nSum\\tOpenList: 169095\\tClosedList: 3288147\\tReopen: 3439638\\tTotal: 6896880\\t(Open Rewrite: 4451921)\\n\''
        node_info = execution_supervisor.pastar_get_node_info(input)

        self.assertEqual(list(node_info.keys()), ['OpenList', 'ClosedList', 'Reopen', 'Total', 'Open Rewrite']) # Comapare the keys when you execute PAStar, since the node qtd can change
        self.assertEqual(node_info, {'OpenList': 169095, 'ClosedList': 3288147, 'Reopen': 3439638, 'Total': 6896880, 'Open Rewrite': 4451921}) # Pre-made input can check for type info as well

    def test_random_sequence(self):

        seq_dictionary =['A', 'T', 'C', 'G']
        initial_seq_size = 10
        seq_size_steps = 5
        uniques_samples_per_size = 10
        max_samples = 100

        sequences = random_sequence_generator.seq_random_gen(seq_dictionary, initial_seq_size, seq_size_steps, uniques_samples_per_size, max_samples)

        # Check total number of entries
        self.assertEqual(sum(len(bucket) for bucket in sequences), max_samples)

        # Check the amount of buckets
        self.assertEqual(max_samples / uniques_samples_per_size, len(sequences))

        # Verify bucket uniqueness
        for bucket in sequences:
            self.assertTrue( len(bucket) == len( set(bucket) ) )

        # Check bucket size (is the step right)
        target_bucket_size = initial_seq_size # It is a copy to avoid changes in the original
        for bucket in sequences:
            # To avoid many comparisons, just the first and last sequences are compared
            self.assertEqual( len(bucket[0]), target_bucket_size)
            self.assertEqual( len(bucket[ uniques_samples_per_size-1 ]), target_bucket_size)
            target_bucket_size += seq_size_steps

        # Are the characters correct
        dict_set: set = set(seq_dictionary)
        for bucket in sequences:
            # To avoid many comparisons, just the first sequence is compared
            for letter in bucket[0]:
                self.assertTrue( letter in dict_set)

    def test_policy_random(self):
        seq_dictionary =['A', 'T', 'C', 'G']
        initial_seq_size = 10
        seq_size_step = 5
        unique_samples_per_size = 2
        max_samples = 10

        random_sequence_generator.seq_random_execution_unit(seq_dictionary, initial_seq_size, seq_size_step, unique_samples_per_size, max_samples, 2, print)

        self.assertTrue(False)

    def test_execute_program_save_data(self):
        pass

if __name__ == '__main__':
    unittest.main()