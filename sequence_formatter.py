
def formatt_seq(sequences: [str], format: str):

    match format:
        case "fasta":

            fasta_seq = ''

            for idx, sequence in enumerate(sequences):
                fasta_seq += f">Sequence_{idx+1}\n"
                fasta_seq += f"{sequence}\n"

            return fasta_seq

        case _:
            raise Exception("Invalid sequence format")
