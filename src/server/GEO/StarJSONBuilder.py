__author__ = 'guorongxu'

import sys
import os
import CorrelationParser

## To print JSON file for each cluster.
def print_json(tumor_type, output_file, node_hash):

    if os.path.exists(output_file):
        return

    if not os.path.exists(os.path.dirname(output_file)):
        os.makedirs(os.path.dirname(output_file))

    for key_node in node_hash:
        node_list = node_hash.get(key_node)

        prefix = "genes_geo"
        filewriter = open(output_file, "a")
        filewriter.write("curl -XPOST http://localhost:9200/genes/" + prefix + " -d \'\n")
        filewriter.write("{\n")
        filewriter.write("\t\"source\": \"GEO\",\n")
        filewriter.write("\t\"species\": \"human\",\n")
        filewriter.write("\t\"network_name\": \"" + tumor_type + "\",\n")
        filewriter.write("\t\"network_full_name\": \"" + tumor_type + "\",\n")
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


def process(correlation_file, tumor_type, output_file):
    node_hash = CorrelationParser.parse_correlation_file(correlation_file)

    print_json(tumor_type, output_file, node_hash)

## Main entry
if __name__ == "__main__":

    workspace = sys.argv[1]
    correlation_file = sys.argv[2]
    output_file = sys.argv[3]
    network_type = sys.argv[4]

    #workspace = "/Users/guorongxu/Desktop/SearchEngine"
    #data_set = "GEO"
    #correlation_file = "/Users/guorongxu/Desktop/SearchEngine/GEO/correlation_files/ThyroidCancer/" \
    #                   "GSE33630_Tomas_Thyroid_Cancer_105_Arrays_Brussels/rnaseq_vs_rnaseq.cor"
    #output_file = "/Users/guorongxu/Desktop/SearchEngine/GEO/json_files/ThyroidCancer/" \
    #              "GSE33630_Tomas_Thyroid_Cancer_105_Arrays_Brussels/rnaseq_vs_rnaseq.json"
    #file_name_str = output_file[output_file.find("json_file") + 11: output_file.find("/rnaseq_vs_rnaseq")]
    #tumor_type = file_name_str[:file_name_str.find("/")]
    #network_type = "rnaseq_vs_rnaseq"

    file_name_str = output_file[output_file.find("json_file") + 11: output_file.find("/rnaseq_vs_rnaseq")]
    tumor_type = file_name_str[:file_name_str.find("/")]

    if not os.path.exists(output_file):
        process(correlation_file, tumor_type, output_file)
