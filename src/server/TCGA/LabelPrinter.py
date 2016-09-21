__author__ = 'guorongxu'

import sys
import os
import re

## To print JSON file for each cluster.
def print_label(workspace, data_set, tumor_type, data_type):
    input_file = workspace + "/" + data_set + "/expression_files/" + tumor_type + "/" + data_type + "_matrix.txt"
    root_label_dir = workspace + "/" + data_set + "/label_files"
    output_file = root_label_dir + "/" + tumor_type + "/" + data_type + "_label.txt"
    try:
        if not os.path.exists(os.path.dirname(output_file)):
            os.makedirs(os.path.dirname(output_file))
    except:
        print "File exists:" + output_file

    filewriter = open(output_file, "a")

    with open(input_file) as fp:
        lines = fp.readlines()
        for index in range(1,len(lines)):
            fields = re.split(r'\t', lines[index])
            if data_type == "mutation":
                filewriter.write(fields[0][:-2] + "\t" + get_type(data_type) + "\n")
            else:
                filewriter.write(fields[0] + "\t" + get_type(data_type) + "\n")

    filewriter.close()

## Convert types
def get_type(data_type):
    if data_type == "mirna":
        return "m"
    elif data_type == "rnaseq":
        return "g"
    elif data_type == "mutation":
        return "v"

def process(workspace, data_set, tumor_type, data_type):
    print_label(workspace, data_set, tumor_type, data_type)

## Main entry
if __name__ == "__main__":

    workspace = sys.argv[1]
    data_set = sys.argv[2]
    tumor_type = sys.argv[3]
    data_type = sys.argv[4]

    process(workspace, data_set, tumor_type, data_type)
