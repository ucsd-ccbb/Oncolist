__author__ = 'guorongxu'

import os
import sys
import logging
import pandas as pd

def parse(root_raw_dir, root_expression_dir, tumor_type, release_year, release_month, release_day):

    rnaseq_file = root_raw_dir + "/" + tumor_type + "/gdac.broadinstitute.org_" + tumor_type \
                  + ".Merge_rnaseqv2__illuminahiseq_rnaseqv2__unc_edu__Level_3__RSEM_genes_normalized__data.Level_3."\
                  + release_year + release_month + release_day + "00.0.0/" + tumor_type \
                  + ".rnaseqv2__illuminahiseq_rnaseqv2__unc_edu__Level_3__RSEM_genes_normalized__data.data.txt"

    if not os.path.exists(rnaseq_file):
        rnaseq_file = root_raw_dir + "/" + tumor_type + "/gdac.broadinstitute.org_" + tumor_type \
                  + ".Merge_rnaseqv2__illuminahiseq_rnaseqv2__unc_edu__Level_3__RSEM_genes_normalized__data.Level_3."\
                  + release_year + release_month + release_day + "00.1.0/" + tumor_type \
                  + ".rnaseqv2__illuminahiseq_rnaseqv2__unc_edu__Level_3__RSEM_genes_normalized__data.data.txt"

    output_file_name = root_expression_dir + "/" + tumor_type + "/rnaseq_matrix.txt"

    if not os.path.exists(os.path.dirname(output_file_name)):
        os.makedirs(os.path.dirname(output_file_name))

    filewriter = open(output_file_name, "a")

    ## Parsing the raw file and get the columns those are all tumors samples.
    labels = []
    sample_name_list = []
    rnaseq_table = pd.read_table(rnaseq_file)

    for index, sample_name in enumerate(list(rnaseq_table.columns.values)):

        if index == 0:
            labels.append(1)
        elif index > 0:
            ## sample type with starting with 0 is tumor, otherwise normal.
            if sample_name[13:14] == "0":
                labels.append(1)
                sample_name_list.append(sample_name[:12])
            else:
                labels.append(0)


    ## print out the expression matrix
    header = "gene_id\t"
    for sample_name in sample_name_list:
        header = header + sample_name + "\t"

    filewriter.write(header[:-1] + "\n")

    rows = rnaseq_table[1:].values
    for row in rows:
        value_str = ""
        ignore = False
        for index, value in enumerate(list(row)):
            if index == 0:
                gene_id = value[:value.index("|")]
                if gene_id == "?":
                    ignore = True
                else:
                    value_str = value_str + gene_id + "\t"

            if index > 0 and labels[index] == 1:
                value_str = value_str + str(value) + "\t"

            if ignore:
                break

        if not ignore:
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