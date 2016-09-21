__author__ = 'guorongxu'

import sys
import os
import Helper
import CorrelationParser

## To print JSON file for each cluster.
def print_json(workspace, data_set, tumor_type, node_hash):

    root_json_dir = workspace + "/" + data_set + "/json_files"
    output_file = root_json_dir + "/" + tumor_type + "/genes_tcga.json"

    if os.path.exists(output_file):
        return

    if not os.path.exists(os.path.dirname(output_file)):
        os.makedirs(os.path.dirname(output_file))

    for key_node in node_hash:
        node_list = node_hash.get(key_node)

        prefix = "genes_tcga"
        filewriter = open(output_file, "a")
        filewriter.write("curl -XPOST http://localhost:9200/genes/" + prefix + " -d \'\n")
        filewriter.write("{\n")
        filewriter.write("\t\"source\": \"TCGA\",\n")
        filewriter.write("\t\"species\": \"human\",\n")
        filewriter.write("\t\"network_name\": \"" + tumor_type + "\",\n")
        filewriter.write("\t\"network_full_name\": \"" + Helper.get_full_tumor_name(tumor_type) + "\",\n")
        node_name_string = key_node[:key_node.index("+")]
        if node_name_string.find("_v") > 0:
            filewriter.write("\t\"node_name\": \"" + node_name_string[:-2] + "\",\n")
        else:
            filewriter.write("\t\"node_name\": \"" + node_name_string + "\",\n")
        filewriter.write("\t\"node_type\": \"" + key_node[key_node.index("+") + 1:] + "\",\n")
        filewriter.write("\t\"degree\": " + str(len(node_list)) + ",\n")
        filewriter.write("\t\"node_list\": [")

        node_string = ""
        for node_name in node_list:
            if node_name[0].find("_v") > 0:
                node_string = node_string + "{\"name\": \"" + node_name[0][:-2] + "\", " \
                          + "\"type\": \"" + node_name[3] + "\", \"correlation_value\": " + node_name[1] \
                          + ", \"p_value\": " + node_name[2]+ "}, "
            else:
                 node_string = node_string + "{\"name\": \"" + node_name[0] + "\", " \
                          + "\"type\": \"" + node_name[3] + "\", \"correlation_value\": " + node_name[1] \
                          + ", \"p_value\": " + node_name[2] + "}, "
        filewriter.write(node_string[:-2] + "]\n")
        filewriter.write("}\n")
        filewriter.write("'\n")
        filewriter.close()


def process(workspace, data_set, tumor_type):
    node_hash = CorrelationParser.parse_correlation_file(workspace, data_set, tumor_type)

    print_json(workspace, data_set, tumor_type, node_hash)

## Main entry
if __name__ == "__main__":

    workspace = sys.argv[1]
    data_set = sys.argv[2]
    tumor_type = sys.argv[3]

    process(workspace, data_set, tumor_type)
