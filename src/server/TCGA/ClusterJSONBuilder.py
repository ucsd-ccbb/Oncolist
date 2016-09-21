__author__ = 'guorongxu'

import sys
import re
import os
import math
import logging
import Helper
from GO import GOLocusParser
from Utils import HypergeomCalculator, RawFileParser

## To print JSON file for each cluster.
def print_json(output_file, tumor_type, network_type, gamma, cluster_list,
               GO_ID_list, total_unique_gene, GO_Term_list, prefix, gene_expression_list):

    for cluster_ID in cluster_list:
        edge_list = cluster_list.get(cluster_ID)

        x_node_list, y_node_list, length_x_node_list, length_y_node_list = get_node_list(edge_list)
        query_node_list = list(set(x_node_list) | set(y_node_list))
        cluster_size = len(query_node_list)

        ## Currently, Elasticsearch cannot handle the clusters with more than
        ## 250K edges. So we will kick them out.
        if get_nonzero_edges(edge_list) > 250000 or cluster_size > 2000:
            continue

        filewriter = open(output_file, "a")
        filewriter.write("curl -XPOST http://localhost:9200/clusters/" + prefix + " -d \'\n")
        filewriter.write("{\n")
        filewriter.write("\t\"source\": \"TCGA\",\n")
        filewriter.write("\t\"version\": \"2016_01_28\",\n")
        filewriter.write("\t\"species\": \"human\",\n")
        filewriter.write("\t\"network_name\": \"" + Helper.get_abbreviation_tumor_name(tumor_type) + "\",\n")
        filewriter.write("\t\"network_full_name\": \"" + Helper.get_full_tumor_name(tumor_type) + "\",\n")
        filewriter.write("\t\"network_type\": \"" + get_network_type(network_type) + "\",\n")
        filewriter.write("\t\"author_name\": \"\",\n")
        filewriter.write("\t\"gse_number\": \"\",\n")
        filewriter.write("\t\"array_num\": \"\",\n")
        filewriter.write("\t\"institution_name\": \"\",\n")
        filewriter.write("\t\"gamma\": \"" + gamma + "\",\n")
        filewriter.write("\t\"node_name\": \"" + cluster_ID[:-2] + "\",\n")

        enriched_list = []
        if network_type.find("rnaseq_vs_") == 0:
            enriched_list = HypergeomCalculator.calc_enrichment(x_node_list, GO_ID_list, total_unique_gene, GO_Term_list)
        elif network_type.find("_vs_rnaseq") > 0:
            enriched_list = HypergeomCalculator.calc_enrichment(y_node_list, GO_ID_list, total_unique_gene, GO_Term_list)
        if network_type.find("mutation_vs_mutation") == 0:
            enriched_list = HypergeomCalculator.calc_enrichment(get_gene_list(x_node_list), GO_ID_list, total_unique_gene, GO_Term_list)

        annotation_list, max_anno_conf = get_go_info(enriched_list)
        filewriter.write("\t\"hypergeometric_scores\": [" + annotation_list + "],\n")
        filewriter.write("\t\"max_annotation_conf\": " + str(max_anno_conf) + ",\n")
        filewriter.write("\t\"x_node_list_type\": \"" + get_type(network_type[:network_type.index("_vs_")]) + "\",\n")

        x_node_string = ""
        for x_node_name in x_node_list:
            if x_node_name.find("_v") > 0:
                x_node_string = x_node_string + "{\"name\": \"" + x_node_name[:-2] + "\", \"value\": " + str(gene_expression_list.get(x_node_name)) + "}, "
            else:
                x_node_string = x_node_string + "{\"name\": \"" + x_node_name + "\", \"value\": " + str(gene_expression_list.get(x_node_name)) + "}, "
        filewriter.write("\t\"x_node_list\": [" + x_node_string[:-2] + "],\n")
        filewriter.write("\t\"x_node_list_degree\": " + str(len(x_node_list)) + ",\n")

        y_node_string = ""
        for y_node_name in y_node_list:
            if y_node_name.find("_v") > 0:
                y_node_string = y_node_string + "{\"name\": \"" + y_node_name[:-2] + "\", \"value\": " + str(gene_expression_list.get(y_node_name)) + "}, "
            else:
                y_node_string = y_node_string + "{\"name\": \"" + y_node_name + "\", \"value\": " + str(gene_expression_list.get(y_node_name)) + "}, "
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
        correlation_matrix_degree = 0

        for i in range(0, len(edge_list)):
            x_loc = i / length_y_node_list
            y_loc = i % length_y_node_list
            edge = edge_list[i]
            if math.fabs(float(edge[0])) > 0:
                correlation_matrix_degree = correlation_matrix_degree + 1
                if correlationStr == "":
                    correlationStr = "{\"x_loc\": " + str(x_loc) + ", \"y_loc\": " + str(y_loc) \
                            + ", \"correlation_value\": " + str(edge[0]) + ", \"p_value\": " + str(edge[2]) + "}, "
                else:
                    filewriter.write(correlationStr)
                    correlationStr = "{\"x_loc\": " + str(x_loc) + ", \"y_loc\": " + str(y_loc) \
                            + ", \"correlation_value\": " + str(edge[0]) + ", \"p_value\": " + str(edge[2]) + "}, "

        filewriter.write(correlationStr[:-2])
        filewriter.write("],\n")
        filewriter.write("\t\"correlation_matrix_degree\": " + str(correlation_matrix_degree) + "\n")
        filewriter.write("}\n")
        filewriter.write("'\n")
        filewriter.close()

def get_gene_list(node_list):
    gene_list = []

    for node in node_list:
        gene_list.append(node[:-2])
    return gene_list

def get_nonzero_edges(edge_list):
    nonzero_edges = 0
    for i in range(0, len(edge_list)):
        edge = edge_list[i]
        if math.fabs(float(edge[0])) > 0:
            nonzero_edges = nonzero_edges + 1

    return nonzero_edges

## Convert types
def get_network_type(network_type):
    if network_type.find("rnaseq") > -1:
        network_type = network_type.replace("rnaseq", "RNA expression")
    if network_type.find("mutation") > -1:
        network_type = network_type.replace("mutation", "DNA mutation")
    if network_type.find("mirna") > -1:
        network_type = network_type.replace("mirna", "miRNA")
    return network_type

## Convert types
def get_type(data_type):
    if data_type == "mirna":
        return "m"
    elif data_type == "rnaseq":
        return "g"
    elif data_type == "mutation":
        return "v"

## To get the node list by providing edge list.
def get_node_list(edge_list):
    x_node_hash = {}
    y_node_hash = {}
    x_node_list = []
    y_node_list = []
    for edge in edge_list:
        if edge[3] not in x_node_hash:
            x_node_hash.update({edge[3]: edge[3]})
            x_node_list.append(edge[3])
        if edge[4].rstrip() not in y_node_hash:
            y_node_hash.update({edge[4].rstrip(): edge[4].rstrip()})
            y_node_list.append(edge[4].rstrip())
    return x_node_list, y_node_list, len(x_node_list), len(y_node_list)

## To get the GO annotation information
def get_go_info(enriched_list):
    annotation_list = ""
    max_anno_conf = 0

    for index, value in enumerate(enriched_list):
        if index >= 5:
            break

        annotation_list = annotation_list + "{\"name\": \"" + value.get("name") + "\", "
        annotation_list = annotation_list + "\"GO_id\": \"" + value.get("go_id") + "\", "
        annotation_list = annotation_list + "\"pvalue\": " + str(value.get("pvalue")) + ", "
        annotation_list = annotation_list + "\"qvalueLog\": " + str(value.get("qvalue")) + ", "
        annotation_list = annotation_list + "\"overlap\": " + str(len(value.get("overlap"))) + ", "
        annotation_list = annotation_list + "\"genes_from_list\": " + str(value.get("genes_from_list")) + ", "
        annotation_list = annotation_list + "\"genes_from_GO\": " + str(value.get("genes_from_go")) + ", "
        annotation_list = annotation_list + "\"description\": \"" + value.get("description") + "\"}, "

        if max_anno_conf < value.get("qvalue"):
            max_anno_conf = value.get("qvalue")

    if annotation_list == "":
        return "", 0
    else:
        return annotation_list[:-2], max_anno_conf

## To parse cluster file and get the cluster info and then to print JSON file.
def parse_cluster_file(cluster_file):
    gamma_index = cluster_file.rfind("gamma_")
    gamma = cluster_file[gamma_index + len("gamma_"):cluster_file.find(".", gamma_index)]
    cluster_list = {}

    logging.info("The system is parsing cluster files.")
    with open(cluster_file) as fp:
        lines = fp.readlines()

        for line in lines:
            fields = re.split(r'\t+', line)
            if fields[0] != "corr":
                if fields[1] in cluster_list:
                    edge_list = cluster_list.get(fields[1])
                    edge_list.append(fields)
                else:
                    edge_list = []
                    edge_list.append(fields)

                cluster_list.update({fields[1]: edge_list})

        logging.info("The system is printing JSON file.")
        logging.info(cluster_file + "\t" + str(len(cluster_list)))

    fp.closed

    return cluster_list, gamma

## Parsing GO database
def parseGO(workspace):

    go_gene_file = workspace + "/GO/GO2all_locus.txt"
    gene_info_file = workspace + "/GO/Homo_sapiens.gene_info"
    go_term_file = workspace + "/GO/go.obo"

    logging.info("parsing GO gene and term files...")

    GO_ID_list, total_unique_gene, GO_Term_list = GOLocusParser.parse(go_gene_file, gene_info_file, go_term_file)

    return GO_ID_list, total_unique_gene, GO_Term_list

def process(cluster_file, output_file, tumor_type, network_type, GO_ID_list, total_unique_gene, GO_Term_list, prefix, gene_expression_list):

    cluster_list, gamma = parse_cluster_file(cluster_file)

    print cluster_file + ": " + str(len(cluster_list))

    if len(cluster_list) == 0:
        return

    print_json(output_file, tumor_type, network_type, gamma, cluster_list, GO_ID_list, total_unique_gene, GO_Term_list, prefix, gene_expression_list)

## Main entry
if __name__ == "__main__":
    workspace = sys.argv[1]
    cluster_file = sys.argv[2]
    output_file = sys.argv[3]
    tumor_type = sys.argv[4]
    network_type = sys.argv[5]
    prefix = sys.argv[6]

    #workspace = "/Users/guorongxu/Desktop/SearchEngine/"
    #cluster_file = "/Users/guorongxu/Desktop/SearchEngine/TCGA/louvain_unique_cluster_files/LIHC/rnaseq_vs_rnaseq_gamma_20/rnaseq_vs_rnaseq_gamma_20.louvain.unique.tsv"
    #output_file = "/Users/guorongxu/Desktop/SearchEngine/TCGA/louvain_json_files/LIHC/rnaseq_vs_rnaseq_gamma_20/rnaseq_vs_rnaseq_gamma_20.json"
    #tumor_type = "LIHC"
    #network_type = "rnaseq_vs_rnaseq"
    #prefix = "clusters_tcga_louvain"

    if not os.path.exists(os.path.dirname(output_file)):
        os.makedirs(os.path.dirname(output_file))

    logging.basicConfig(filename='search_engine.log',level=logging.DEBUG)
    logging.info("Cluster file: " + cluster_file)
    logging.info("Output file: " + output_file)

    if os.path.exists(cluster_file) and not os.path.exists(output_file):
        raw_expression_folder = cluster_file[:cluster_file.find(tumor_type)] + tumor_type
        if "louvain" in prefix:
            raw_expression_folder = raw_expression_folder.replace("louvain_unique_cluster_files", "expression_files")
        if "oslom" in prefix:
            raw_expression_folder = raw_expression_folder.replace("oslom_undirected_cluster_files", "expression_files")
        gene_expression_list = RawFileParser.parse_tcga_expression(raw_expression_folder)

        GO_ID_list, total_unique_gene, GO_Term_list = parseGO(workspace)
        process(cluster_file, output_file, tumor_type, network_type, GO_ID_list, total_unique_gene, GO_Term_list, prefix, gene_expression_list)
