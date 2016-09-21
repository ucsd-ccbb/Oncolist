__author__ = 'guorongxu'

import os
import re

## Parsing the go term file and return GO ID list with descriptions.
def parse_correlation_file(input_file):

    node_hash = {}

    if os.path.exists(input_file):
        with open(input_file) as fp:
            lines = fp.readlines()
            for line in lines:
                fields = re.split(r'\t', line)

                node_0 = fields[0] + "+g"
                node_1 = fields[1] + "+g"

                if node_0 in node_hash:
                    node_list = node_hash.get(node_0)
                    node_list.append([fields[1], fields[2], fields[3][:-1], "g"])
                else:
                    node_list = []
                    node_list.append([fields[1], fields[2], fields[3][:-1], "g"])
                    node_hash.update({node_0:node_list})

                if node_1 in node_hash:
                    node_list = node_hash.get(node_1)
                    node_list.append([fields[0], fields[2], fields[3][:-1], "g"])
                else:
                    node_list = []
                    node_list.append([fields[0], fields[2], fields[3][:-1], "g"])
                    node_hash.update({node_1:node_list})

        fp.closed

    return node_hash

## Main entry
if __name__ == "__main__":
    workspace = "/Users/guorongxu/Desktop/SearchEngine"
    data_set = "TCGA"
    tumor_type = "LIHC"
    parse_correlation_file(workspace, data_set, tumor_type)