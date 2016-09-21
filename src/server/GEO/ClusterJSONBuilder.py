__author__ = 'guorongxu'

import os
import re
import sys
import math
import logging

import Helper
from GO import GOLocusParser
from Utils import HypergeomCalculator, RawFileParser


## To print JSON file for each cluster.
def print_json(prefix, output_file, network_type, cluster_list,
               GO_ID_list, total_unique_gene, GO_Term_list, gene_expression_list):

    if not os.path.exists(os.path.dirname(output_file)):
        os.makedirs(os.path.dirname(output_file))

    project_info = parse_file_name(output_file)

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
        filewriter.write("\t\"source\": \"GEO\",\n")
        filewriter.write("\t\"version\": \"2016_07_28\",\n")
        filewriter.write("\t\"species\": \"human\",\n")
        filewriter.write("\t\"network_name\": \"" + Helper.get_abbreviation_tumor_name(project_info[2]) + "\",\n")
        filewriter.write("\t\"network_full_name\": \"" + Helper.get_full_tumor_name(project_info[2]) + "\",\n")
        filewriter.write("\t\"network_type\": \"RNA expression_vs_RNA expression\",\n")
        filewriter.write("\t\"author_name\": \"" + project_info[1] + "\",\n")
        filewriter.write("\t\"gse_number\": \"" + project_info[0] + "\",\n")
        filewriter.write("\t\"array_num\": \"" + project_info[4] + "\",\n")
        filewriter.write("\t\"institution_name\": \"" + project_info[5] + "\",\n")
        filewriter.write("\t\"gamma\": \"" + project_info[6] + "\",\n")
        filewriter.write("\t\"node_name\": \"" + cluster_ID[:-2] + "\",\n")

        if network_type.find("rnaseq") <= 0:
            enriched_list = HypergeomCalculator.calc_enrichment(x_node_list, GO_ID_list, total_unique_gene, GO_Term_list)
        elif network_type.find("rnaseq") > 0:
            enriched_list = HypergeomCalculator.calc_enrichment(y_node_list, GO_ID_list, total_unique_gene, GO_Term_list)

        annotation_list, max_anno_conf = get_go_info(enriched_list)
        filewriter.write("\t\"hypergeometric_scores\": [" + annotation_list + "],\n")
        filewriter.write("\t\"max_annotation_conf\": " + str(max_anno_conf) + ",\n")
        filewriter.write("\t\"x_node_list_type\": \"" + get_type(network_type[:network_type.index("_vs_")]) + "\",\n")

        x_node_string = ""
        for x_node_name in x_node_list:
            x_node_string = x_node_string + "{\"name\": \"" + x_node_name + "\", \"value\": " + str(gene_expression_list.get(x_node_name)) + "}, "
        filewriter.write("\t\"x_node_list\": [" + x_node_string[:-2] + "],\n")
        filewriter.write("\t\"x_node_list_degree\": " + str(len(x_node_list)) + ",\n")

        y_node_string = ""
        for y_node_name in y_node_list:
            y_node_string = y_node_string + "{\"name\": \"" + y_node_name + "\", \"value\": " + str(gene_expression_list.get(y_node_name)) + "}, "
        filewriter.write("\t\"y_node_list_type\": \"" + get_type(network_type[network_type.index("_vs_") + 4:]) + "\",\n")
        filewriter.write("\t\"y_node_list\": [" + y_node_string[:-2] + "],\n")
        filewriter.write("\t\"y_node_list_degree\": " + str(len(y_node_list)) + ",\n")

        query_node_string = ""
        for query_node_name in query_node_list:
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
                if i < (len(edge_list) - 1):
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

def get_nonzero_edges(edge_list):
    nonzero_edges = 0
    for i in range(0, len(edge_list)):
        edge = edge_list[i]
        if math.fabs(float(edge[0])) > 0:
            nonzero_edges = nonzero_edges + 1

    return nonzero_edges

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
            y_node_list.append(edge[ 4].rstrip())
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

    gamma = cluster_file[cluster_file.index("gamma_") + len("gamma_"):-4]
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

def process(prefix, cluster_file, output_file, network_type, GO_ID_list, total_unique_gene, GO_Term_list, gene_expression_list):
    #logging.basicConfig(filename='search_engine.log',level=logging.DEBUG)
    logging.info("Cluster file: " + cluster_file)
    logging.info("Output file: " + output_file)

    cluster_list, gamma = parse_cluster_file(cluster_file)

    if len(cluster_list) == 0:
        logging.info("Cluster file: " + cluster_file + " is empty!!!")
        return

    print_json(prefix, output_file, network_type, cluster_list, GO_ID_list, total_unique_gene, GO_Term_list, gene_expression_list)

## To parse the file name to get the project information.
def parse_file_name(file_name):
    project_info = []
    file_name_str = file_name[file_name.find("json_file") + 11: file_name.find("/rnaseq_vs_rnaseq")]
    disease_full_name = file_name_str[:file_name_str.find("/")]

    full_file_name = file_name_str[file_name_str.find("/") + 1:]
    gse_index = full_file_name.index("_")
    author_index = full_file_name.index("_", gse_index + 1)
    disease_index = full_file_name.index("_", author_index + 1)
    array_index = full_file_name.index("_Arrays_")
    gamma_index = full_file_name.index("_gamma_")

    gse_number = full_file_name[0:gse_index]
    author_name = full_file_name[gse_index + 1 :author_index]
    disease_name = full_file_name[author_index + 1 :array_index]
    array_num = disease_name[disease_name.rindex("_") + 1 :]
    disease_name = disease_name[0:disease_name.rindex("_")]
    institution_name = full_file_name[array_index + len("_Arrays_") : gamma_index]
    gamma = full_file_name[gamma_index + len("_gamma_") : ]

    project_info.append(gse_number)
    project_info.append(author_name)
    project_info.append(disease_full_name)
    project_info.append(disease_name.replace("_", " ").strip())
    project_info.append(array_num)
    project_info.append(institution_name.replace("_", " ").strip())
    project_info.append(gamma)

    return project_info

## Main entry
if __name__ == "__main__":
    workspace = sys.argv[1]
    cluster_file = sys.argv[2]
    output_file = sys.argv[3]
    network_type = sys.argv[4]
    cluster_algorithm = sys.argv[5]

    #workspace = "/Users/guorongxu/Desktop/SearchEngine"
    #cluster_file = "/Users/guorongxu/Desktop/SearchEngine/GEO/oslom_cluster_files/InflammationBlood/GSE65270_Morgan_Inflammation_Rectal_Biopsies_UC_273_Arrays_Toronto_gamma_1/rnaseq_vs_rnaseq_gamma_1.tsv"
    #output_file = "/Users/guorongxu/Desktop/SearchEngine/GEO/oslom_json_files/InflammationBlood/GSE65270_Morgan_Inflammation_Rectal_Biopsies_UC_273_Arrays_Toronto_gamma_1/rnaseq_vs_rnaseq_gamma_1.json"
    #network_type = "rnaseq_vs_rnaseq"
    #cluster_algorithm = "print_oslom_cluster_json"

    if not os.path.exists(output_file):
        ## parsing the raw expression file to get the list of the average gene expression value.
        if cluster_algorithm == "print_louvain_cluster_json":
            raw_expression_file = cluster_file.replace("unique_louvain_cluster_files","raw_files")
            prefix = "clusters_geo_louvain"
        elif cluster_algorithm == "print_oslom_cluster_json":
            raw_expression_file = cluster_file.replace("oslom_cluster_files","raw_files")
            prefix = "clusters_geo_oslom"

        raw_expression_file = raw_expression_file[:raw_expression_file.find("_gamma")]
        gene_expression_list = RawFileParser.parse_geo_expression(raw_expression_file + ".txt")

        ## parsing the GO annotation database
        GO_ID_list, total_unique_gene, GO_Term_list = parseGO(workspace)

        process(prefix, cluster_file, output_file, network_type, GO_ID_list, total_unique_gene, GO_Term_list, gene_expression_list)
