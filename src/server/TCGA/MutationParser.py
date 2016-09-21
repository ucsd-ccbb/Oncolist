__author__ = 'guorongxu'

import re
import os
import sys
import logging
import MatrixPrinter

## Parsing mutation files and return a dictionary of ID and name.
def parse(root_raw_dir, root_expression_dir, tumor_type, release_year, release_month, release_day):
    mutation_file_folder = root_raw_dir + "/" + tumor_type + "/gdac.broadinstitute.org_"\
                           + tumor_type +".Mutation_Packager_Oncotated_Calls.Level_3."\
                           +release_year + release_month + release_day + "00.0.0/"
    output_file_name = root_expression_dir + "/" + tumor_type + "/mutation_matrix.txt"

    if not os.path.exists(os.path.dirname(output_file_name)):
        os.makedirs(os.path.dirname(output_file_name))

    sample_list = {}
    sample_name_list = {}
    gene_name_list = {}

    for sample_file in os.listdir(mutation_file_folder):
        if sample_file.endswith(".maf.txt"):
            gene_list = {}

            mutation_file = mutation_file_folder + sample_file
            sample_file_short = sample_file[0:sample_file.rindex("-")]
            if sample_file_short not in sample_name_list:
                sample_name_list.update({sample_file_short: sample_file_short})

            index_num = 164
            with open(mutation_file) as fp:
                lines = fp.readlines()
                for line in lines:
                    if not line.startswith("#"):
                        if not line.startswith("Hugo_Symbol"):
                            fields = re.split(r'\t', line)

                            ## Add the gene name into the gene name list
                            if fields[0] not in gene_name_list:
                                gene_name_list.update({fields[0]: fields[0]})

                            ## Add the gene name and score to the gene list.
                            ## If gene has multipe score, give the score of the highest scoring mutation.
                            if fields[0] not in gene_list:
                                gene_list.update({fields[0]: get_score(fields[index_num])})
                            else:
                                score = gene_list.get(fields[0])
                                if score < get_score(fields[index_num]):
                                    gene_list.update({fields[0]: get_score(fields[index_num])})
                        else:
                            index_num = get_index_num(line)
            sample_list.update({sample_file_short: gene_list})

            fp.closed

    MatrixPrinter.print_matrix(output_file_name, sample_list, sample_name_list, gene_name_list)

## To get the column index from the mutation files
## The index number of i_Ensembl_so_term is different in different tumor type
def get_index_num(header_line):
    fields = re.split(r'\t', header_line)
    for index, elem in enumerate(fields):
        if elem == "i_Ensembl_so_term":
            return index

    return 164

def get_score(variant_classification):

    if variant_classification == "":
        return 1
    elif variant_classification == "intergenic_variant":
        return 3
    elif variant_classification == "feature_truncation":
        return 3
    elif variant_classification == "regulatory_region_variant":
        return 3
    elif variant_classification == "feature_elongation":
        return 3
    elif variant_classification == "regulatory_region_amplification":
        return 3
    elif variant_classification == "regulatory_region_ablation":
        return 4
    elif variant_classification == "TF_binding_site_variant":
        return 3
    elif variant_classification == "TFBS_amplification":
        return 3
    elif variant_classification == "TFBS_ablation":
        return 3
    elif variant_classification == "downstream_gene_variant":
        return 3
    elif variant_classification == "upstream_gene_variant":
        return 3
    elif variant_classification == "non_coding_transcript_variant":
        return 3
    elif variant_classification == "NMD_transcript_variant":
        return 3
    elif variant_classification == "intron_variant":
        return 3
    elif variant_classification == "non_coding_transcript_exon_variant":
        return 3
    elif variant_classification == "3_prime_UTR_variant":
        return 3
    elif variant_classification == "5_prime_UTR_variant":
        return 3
    elif variant_classification == "mature_miRNA_variant":
        return 3
    elif variant_classification == "coding_sequence_variant":
        return 3
    elif variant_classification == "synonymous_variant":
        return 2
    elif variant_classification == "stop_retained_variant":
        return 2
    elif variant_classification == "incomplete_terminal_codon_variant":
        return 2
    elif variant_classification == "splice_region_variant":
        return 2
    elif variant_classification == "protein_altering_variant":
        return 4
    elif variant_classification == "missense_variant":
        return 4
    elif variant_classification == "missense":
        return 4
    elif variant_classification == "inframe_deletion":
        return 4
    elif variant_classification == "inframe_insertion":
        return 4
    elif variant_classification == "transcript_amplification":
        return 5
    elif variant_classification == "start_lost":
        return 5
    elif variant_classification == "initiator_codon_variant":
        return 5
    elif variant_classification == "stop_lost":
        return 5
    elif variant_classification == "frameshift_variant":
        return 5
    elif variant_classification == "stop_gained":
        return 5
    elif variant_classification == "splice_donor_variant":
        return 5
    elif variant_classification == "splice_acceptor_variant":
        return 5
    elif variant_classification == "transcript_ablation":
        return 5
    else:
        print variant_classification + " is missing..."
## Main entry
if __name__ == "__main__":

    logging.basicConfig(filename='search_engine.log',level=logging.DEBUG)

    root_raw_dir = sys.argv[1]
    root_expression_dir = sys.argv[2]
    tumor_type = sys.argv[3]
    release_year = sys.argv[4]
    release_month = sys.argv[5]
    release_day = sys.argv[6]

    logging.info("Root raw dir: " + root_raw_dir)
    logging.info("Root expression dir: " + root_expression_dir)
    logging.info("Tumor type: " + tumor_type)
    logging.info("Release year: " + release_year)
    logging.info("Release month: " + release_month)
    logging.info("Release day: " + release_day)

    parse(root_raw_dir, root_expression_dir, tumor_type, release_year, release_month, release_day)