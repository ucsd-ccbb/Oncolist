__author__ = 'guorongxu'

import os
import sys
import logging
import pandas as pd

def parse(root_raw_dir, root_expression_dir, tumor_type, release_year, release_month, release_day):
    mirna_file = root_raw_dir + "/" + tumor_type + "/gdac.broadinstitute.org_" + tumor_type \
                 + ".Merge_mirnaseq__illuminahiseq_mirnaseq__bcgsc_ca__Level_3__miR_gene_expression__data.Level_3."\
                 + release_year + release_month + release_day + "00.0.0/"+ tumor_type\
                 + ".mirnaseq__illuminahiseq_mirnaseq__bcgsc_ca__Level_3__miR_gene_expression__data.data.txt"
    output_file_name = root_expression_dir + "/" + tumor_type + "/mirna_matrix.txt"

    if not os.path.exists(os.path.dirname(output_file_name)):
        os.makedirs(os.path.dirname(output_file_name))

    filewriter = open(output_file_name, "a")

    ## Parsing the raw file and get the columns those are all tumors samples.
    labels = []
    sample_name_list = []
    mirna_table = pd.read_table(mirna_file)

    for index, sample_name in enumerate(list(mirna_table.columns.values)):

        if index == 0:
            labels.append(1)

        if index > 0 and index % 3 == 2:
            ## sample type with starting with 0 is tumor, otherwise normal.
            if sample_name[13:14] == "0":
                labels.append(1)
                sample_name_list.append(sample_name[:12])
            else:
                labels.append(0)
        elif index > 0 and not index % 3 == 2:
            labels.append(0)


    ## print out the expression matrix
    header = "miRNA_ID\t"
    for sample_name in sample_name_list:
        header = header + sample_name + "\t"

    filewriter.write(header[:-1] + "\n")

    rows = mirna_table[1:].values
    for row in rows:
        value_str = ""
        for index, value in enumerate(list(row)):
            if labels[index] == 1:
                value_str = value_str + str(value) + "\t"

        filewriter.write(value_str[:-1] + "\n")

    filewriter.close()

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