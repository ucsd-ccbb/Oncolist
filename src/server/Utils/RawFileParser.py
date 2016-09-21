__author__ = 'Guorong Xu<g1xu@ucsd.edu>'

import re
import os
import math

## Parsing the raw expression file and return the average expression value for each gene.
def parse_geo_expression(raw_expression_file):

    gene_expression_list = {}

    with open(raw_expression_file) as fp:
        lines = fp.readlines()

        for index, line in enumerate(lines):
            if index == 0:
                continue

            fields = re.split(r'\t+', line)

            if len(fields) == 1:
                print raw_expression_file + " ZeroDivisionError!!!"
                continue

            if fields[0] not in gene_expression_list:
                average_value = 0
                for i in range(1, len(fields)):
                    if float(fields[i].rstrip()) > 1000:
                        average_value = average_value + 1000
                    elif float(fields[i].rstrip()) < -1000:
                        average_value = average_value - 1000
                    else:
                        average_value = average_value + float(fields[i].rstrip())
                gene_expression_list.update({fields[0]: average_value/(len(fields) - 1) + 1})

    fp.closed

    return gene_expression_list

## Parsing the raw expression file and return the average expression value for each gene.
def parse_tcga_expression(raw_expression_folder):
    gene_expression_list = {}

    for dirpath, directories, filenames in os.walk(raw_expression_folder):
        for filename in filenames:
            if not filename.endswith(".txt"):
                continue
            raw_expression_file = os.path.join(dirpath, filename)
            with open(raw_expression_file) as fp:
                lines = fp.readlines()

                for index, line in enumerate(lines):
                    if index == 0:
                        continue

                    fields = re.split(r'\t+', line)

                    if len(fields) == 1:
                        print raw_expression_file + " ZeroDivisionError!!!"
                        continue

                    if fields[0] not in gene_expression_list:
                        average_value = 0
                        for i in range(1, len(fields)):
                            average_value = average_value + float(fields[i].rstrip())
                        gene_expression_list.update({fields[0]: math.log10(average_value/(len(fields) - 1) + 1)})
            fp.closed

    return gene_expression_list

## Main entry
if __name__ == "__main__":
    raw_expression_file = "/Users/guorongxu/Desktop/SearchEngine/GEO/raw_files/ColonAdenocarcinoma/GSE42284_Roepman_Colon_Cancer188_Arrays_Amsterdam_Agendia.txt.new"
    parse_geo_expression(raw_expression_file)
