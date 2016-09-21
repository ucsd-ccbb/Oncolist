__author__ = 'guorongxu'

import sys
import re
import os
import math
import logging
import Helper
from GO import GOLocusParser
from Utils import HypergeomCalculator

## To print JSON file for each cluster.
def print_json(output_file, tumor_type, network_type, gamma, cluster_list, prefix):

    for cluster_ID in cluster_list:
        edge_list = cluster_list.get(cluster_ID)

        x_node_list, y_node_list, length_x_node_list, length_y_node_list = get_node_list(edge_list)
        query_node_list = list(set(x_node_list) | set(y_node_list))
        cluster_size = len(query_node_list)

        ## We only keep the cluster with the size with the range of 20-500.
        if cluster_size <= 2000 and cluster_size >= 20:
            filewriter = open(output_file, "a")
            filewriter.write("curl -XPOST http://localhost:9200/clusters/" + prefix + " -d \'\n")
            filewriter.write("{\n")
            filewriter.write("\t\"source\": \"TCGA\",\n")
            filewriter.write("\t\"species\": \"human\",\n")
            filewriter.write("\t\"network_name\": \"" + tumor_type + "\",\n")
            filewriter.write("\t\"network_full_name\": \"" + Helper.get_full_tumor_name(tumor_type) + "\",\n")
            filewriter.write("\t\"network_type\": \"" + network_type + "\",\n")
            filewriter.write("\t\"author_name\": \"\",\n")
            filewriter.write("\t\"gse_number\": \"\",\n")
            filewriter.write("\t\"array_num\": \"\",\n")
            filewriter.write("\t\"institution_name\": \"\",\n")
            filewriter.write("\t\"gamma\": \"" + gamma + "\",\n")
            filewriter.write("\t\"node_name\": \"" + cluster_ID + "\",\n")
            filewriter.write("\t\"hypergeometric_scores\": [],\n")
            filewriter.write("\t\"x_node_list_type\": \"" + get_type(network_type[:network_type.index("_vs_")]) + "\",\n")

            x_node_string = ""
            for x_node_name in x_node_list:
                if x_node_name.find("_v") > 0:
                    x_node_string = x_node_string + "{\"name\": \"" + x_node_name[:-2] + "\"}, "
                else:
                    x_node_string = x_node_string + "{\"name\": \"" + x_node_name + "\"}, "
            filewriter.write("\t\"x_node_list\": [" + x_node_string[:-2] + "],\n")
            filewriter.write("\t\"x_node_list_degree\": " + str(len(x_node_list)) + ",\n")

            y_node_string = ""
            for y_node_name in y_node_list:
                if y_node_string.find("_v") > 0:
                    y_node_string = y_node_string + "{\"name\": \"" + y_node_name[:-2] + "\"}, "
                else:
                    y_node_string = y_node_string + "{\"name\": \"" + y_node_name + "\"}, "
            filewriter.write("\t\"y_node_list_type\": \"" + get_type(network_type[network_type.index("_vs_") + 4:]) + "\",\n")
            filewriter.write("\t\"y_node_list\": [" + y_node_string[:-2] + "],\n")
            filewriter.write("\t\"y_node_list_degree\": " + str(len(y_node_list)) + ",\n")

            query_node_string = ""
            for query_node_name in query_node_list:
                if query_node_name.find("_v") > 0:
                    query_node_string = query_node_string + "{\"name\": \"" + query_node_name[:-2] + "\"}, "
                else:
                    query_node_string = query_node_string + "{\"name\": \"" + query_node_name + "\"}, "
            filewriter.write("\t\"query_node_list\": [" + query_node_string[:-2] + "],\n")

            filewriter.write("\t\"correlation_matrix\": [")

            correlationStr = ""
            cut_off = get_cut_off(edge_list)

            for i in range(0, len(edge_list)):
                if cluster_size > 500:
                    x_loc = i / length_y_node_list
                    y_loc = i % length_y_node_list
                    edge = edge_list[i]
                    if math.fabs(float(edge[4])) > cut_off:
                        if i < (len(edge_list) - 1):
                            if correlationStr == "":
                                correlationStr = "{\"x_loc\": " + str(x_loc) + ", \"y_loc\": " + str(y_loc) \
                                        + ", \"correlation_value\": " + str(edge[4][:-1]) + ", \"p_value\": 0}, "
                            else:
                                filewriter.write(correlationStr)
                                correlationStr = "{\"x_loc\": " + str(x_loc) + ", \"y_loc\": " + str(y_loc) \
                                        + ", \"correlation_value\": " + str(edge[4][:-1]) + ", \"p_value\": 0}, "
                else:
                    x_loc = i / length_y_node_list
                    y_loc = i % length_y_node_list
                    edge = edge_list[i]
                    if math.fabs(float(edge[4])) > 0:
                        if i < (len(edge_list) - 1):
                            if correlationStr == "":
                                correlationStr = "{\"x_loc\": " + str(x_loc) + ", \"y_loc\": " + str(y_loc) \
                                        + ", \"correlation_value\": " + str(edge[4][:-1]) + ", \"p_value\": 0}, "
                            else:
                                filewriter.write(correlationStr)
                                correlationStr = "{\"x_loc\": " + str(x_loc) + ", \"y_loc\": " + str(y_loc) \
                                        + ", \"correlation_value\": " + str(edge[4][:-1]) + ", \"p_value\": 0}, "

            filewriter.write(correlationStr[:-2])
            filewriter.write("],\n")
            filewriter.write("\t\"correlation_matrix_degree\": " + str(len(edge_list)) + "\n")
            filewriter.write("}\n")
            filewriter.write("'\n")
            filewriter.close()

def get_cut_off(edge_list):
    new_edge_list = list(edge_list)
    new_edge_list.sort(key=lambda x: x[4], reverse=True)

    if len(new_edge_list) > 500:
        return float(new_edge_list[500][4])
    else:
        return float(new_edge_list[-1][4])

## Convert types
def get_type(data_type):
    if data_type == "mirna":
        return "m"
    elif data_type == "rna":
        return "g"
    elif data_type == "mutation":
        return "v"
    elif data_type == "go":
        return "a"

## To get the node list by providing edge list.
def get_node_list(edge_list):
    x_node_list = {}
    y_node_list = {}
    for edge in edge_list:
        if edge[0] not in x_node_list:
            x_node_list.update({edge[0]: edge[0]})
        if edge[2] not in y_node_list:
            y_node_list.update({edge[2]: edge[2]})
    return x_node_list.keys(), y_node_list.keys(), len(x_node_list), len(y_node_list)

## To parse cluster file and get the cluster info and then to print JSON file.
def parse_cluster_file(cluster_file):
    cluster_list = {}

    logging.info("The system is parsing cluster files.")
    with open(cluster_file) as fp:
        lines = fp.readlines()

        for line in lines:
            fields = re.split(r'\t+', line)
            if fields[0] != "GO_name":
                if fields[3] in cluster_list:
                    edge_list = cluster_list.get(fields[3])
                    edge_list.append(fields)
                else:
                    edge_list = []
                    edge_list.append(fields)

                cluster_list.update({fields[3]: edge_list})

    fp.closed

    return cluster_list

def process(cluster_file, output_file, tumor_type, network_type, gamma, prefix):
    logging.info("Cluster file: " + cluster_file)
    logging.info("Output file: " + output_file)

    cluster_list = parse_cluster_file(cluster_file)

    print_json(output_file, tumor_type, network_type, gamma, cluster_list, prefix)

## Main entry
if __name__ == "__main__":
    #workspace = "/Users/guorongxu/Desktop/SearchEngine"
    #data_set = "TCGA"
    #cluster_file = "/Users/guorongxu/Desktop/SearchEngine/TCGA/ivanovska_files/LIHC/rnaseq_vs_rnaseq.tsv"
    #output_file = "/Users/guorongxu/Desktop/SearchEngine/TCGA/ivanovska_files/LIHC/rnaseq_vs_rnaseq.json"
    #tumor_type = "LIHC"
    #network_type = "go_vs_rna"
    workspace = sys.argv[1]
    cluster_file = sys.argv[2]
    output_file = sys.argv[3]
    tumor_type = sys.argv[4]
    network_type = sys.argv[5].replace("rnaseq", "rna")
    prefix = sys.argv[6]
    gamma = "1"

    if os.path.exists(cluster_file) and not os.path.exists(output_file):
        process(cluster_file, output_file, tumor_type, network_type, gamma, prefix)