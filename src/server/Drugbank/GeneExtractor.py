__author__ = 'guorongxu'

import re
import os
import sys

## To parse JSON files and extract the gene list.
def process_json(workspace, data_set):
    root_json_dir = workspace + "/" + data_set + "/json_files"
    output_file = root_json_dir + "/druggable_gene_name.txt"
    filewriter = open(output_file, "a")

    for dirpath, directories, filenames in os.walk(root_json_dir):
        for filename in filenames:
            if filename.endswith(".json"):
                input_file = os.path.join(dirpath, filename)
                with open(input_file) as fp:
                    lines = fp.readlines()

                    drug_name = ""
                    drug_id = ""

                    for line in lines:
                        if line.find("curl") > -1:
                            drug_name = ""
                            drug_id = ""
                        if line.find("node_name") > -1:
                            drug_name = line[line.find(":") + 3: -3]
                        if line.find("drugbank_id") > -1:
                            drug_id = line[line.find(":") + 3: -3]
                        if line.find("node_list") > -1:
                            gene_list = line[line.find("[") + 1: line.find("]")]
                            fields = re.split(r', ', gene_list)
                            for field in fields:
                                gene_name = field[field.find(":") + 3: -2]
                                filewriter.write(drug_id + "\t" + drug_name + "\t" + gene_name + "\n")


                fp.closed

    filewriter.close()

## Main entry
if __name__ == "__main__":

    #workspace = sys.argv[1]
    #data_set = sys.argv[2]
    workspace = "/Users/guorongxu/Desktop/SearchEngine"
    data_set = "Drugbank"

    process_json(workspace, data_set)