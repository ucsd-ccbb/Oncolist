__author__ = 'guorongxu'

import os
import re
import itertools

## Parsing the go term file and return GO ID list with descriptions.
def parse_correlation_file(workspace, data_set, tumor_type):

    node_hash = {}
    root_correlation_dir = workspace + "/" + data_set + "/correlation_files"

    ## Iterate all combinations
    data_type = ["mirna", "rnaseq", "mutation"]
    combinations = list(itertools.combinations_with_replacement(data_type, 2))

    for combination in combinations:
        input_file = root_correlation_dir + "/" + tumor_type + "/" + combination[0] + "_vs_" + combination[1] + ".cor"
        if os.path.exists(input_file):
            with open(input_file) as fp:
                lines = fp.readlines()
                for line in lines:
                    fields = re.split(r'\t', line)

                    node_0 = fields[0] + "+" + get_type(combination[0])
                    node_1 = fields[1] + "+" + get_type(combination[1])

                    if node_0 in node_hash:
                        node_list = node_hash.get(node_0)
                        node_list.append([fields[1], fields[2], fields[3][:-1], get_type(combination[1])])
                    else:
                        node_list = []
                        node_list.append([fields[1], fields[2], fields[3][:-1], get_type(combination[1])])
                        node_hash.update({node_0:node_list})

                    if node_1 in node_hash:
                        node_list = node_hash.get(node_1)
                        node_list.append([fields[0], fields[2], fields[3][:-1], get_type(combination[0])])
                    else:
                        node_list = []
                        node_list.append([fields[0], fields[2], fields[3][:-1], get_type(combination[0])])
                        node_hash.update({node_1:node_list})

            fp.closed

    return node_hash

## Convert types
def get_type(data_type):
    if data_type == "mirna":
        return "m"
    elif data_type == "rnaseq":
        return "g"
    elif data_type == "mutation":
        return "v"


## Main entry
if __name__ == "__main__":
    workspace = "/Users/guorongxu/Desktop/SearchEngine"
    data_set = "TCGA"
    tumor_type = "LIHC"
    parse_correlation_file(workspace, data_set, tumor_type)