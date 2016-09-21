__author__ = 'guorongxu'

import re
import os
import sys

## To parse Drugbank JSON files and extract the gene list.
def process_drugbank_json(workspace, data_set):
    root_json_dir = workspace + "/" + data_set + "/json_files"
    gene_hash = {}

    for dirpath, directories, filenames in os.walk(root_json_dir):
        for filename in filenames:
            if filename.endswith(".json.new"):
                input_file = os.path.join(dirpath, filename)

                print input_file

                with open(input_file) as fp:
                    lines = fp.readlines()
                    doc_id = ""
                    node_name = ""
                    drugbank_id = ""
                    for line in lines:
                        if line.find("curl") > -1:
                            doc_id = line[55:-6]
                        if line.find("node_name") > -1:
                            node_name = line[line.find(":") + 3:-3]
                        if line.find("drugbank_id") > -1:
                            drugbank_id = line[line.find(":") + 3:-3]
                        if line.find("node_list") > -1:
                            gene_list = line[line.find("[") + 1: line.find("]")]
                            fields = re.split(r', ', gene_list)
                            for field in fields:
                                gene_name = field[field.find(":") + 3: -2]
                                if len(gene_name) > 0 and gene_name not in gene_hash:
                                    drug_list = []
                                    drug_list.append([doc_id, node_name, drugbank_id])
                                    gene_hash.update({gene_name:drug_list})
                                elif len(gene_name) > 0 and gene_name in gene_hash:
                                    drug_list = gene_hash.get(gene_name)
                                    drug = [doc_id, node_name, drugbank_id]
                                    drug_list.append(drug)
                                    gene_hash.update({gene_name:drug_list})

                            doc_id = ""
                            node_name = ""
                            drugbank_id = ""


                fp.closed
    return gene_hash

## To parse cluster JSON files and output cluster_drug document.
def process_cluster_json(workspace, data_set, cluster_data_set, gene_hash):
    cluster_json_dir = workspace + "/" + cluster_data_set + "/oslom_undirected_json_files"
    output_file = workspace + "/" + data_set + "/json_files" + "/druggable_cluster." + cluster_data_set + ".json"

    if not os.path.exists(os.path.dirname(output_file)):
        os.makedirs(os.path.dirname(output_file))

    print data_set + ": " + cluster_data_set
    
    filewriter = open(output_file, "a")

    for dirpath, directories, filenames in os.walk(cluster_json_dir):
        for filename in filenames:
            if filename.find("gamma") > -1 and filename.endswith(".json.new"):
                input_file = os.path.join(dirpath, filename)
                with open(input_file) as fp:

                    print input_file

                    lines = fp.readlines()
                    doc_id = ""

                    for line in lines:
                        if line.find("curl") > -1:
                            doc_id = line[line.rindex("/") + 1:-6]
                        if line.find("query_node_list") > -1:
                            druggable_gene_list = []
                            gene_list = line[line.find("[") + 1: line.find("]")]
                            fields = re.split(r', ', gene_list)

                            for field in fields:
                                gene_name = field[field.find(":") + 3: -2]
                                if gene_name in gene_hash:
                                    if len(gene_name) > 0:
                                        druggable_gene_list.append(gene_name)

                            ## print out the json for each cluster id with the druggable genes
                            if (len(druggable_gene_list) > 0):
                                print_json(filewriter, doc_id, druggable_gene_list, gene_hash)
                            else:
                                print doc_id + " has no druggable genes!"
                            doc_id = ""
                fp.closed

    filewriter.close()

def print_json(filewriter, doc_id, druggable_gene_list, gene_hash):
    prefix = "clusters_drugs"

    filewriter.write("curl -XPOST http://localhost:9200/groups/" + prefix + " -d \'\n")
    filewriter.write("{\n")
    filewriter.write("\t\"source\": \"clusters_drugs\",\n")
    filewriter.write("\t\"version\": \"2016_07_28\",\n")
    filewriter.write("\t\"species\": \"human\",\n")
    filewriter.write("\t\"network_name\": \"" + prefix + "\",\n")
    filewriter.write("\t\"network_full_name\": \"" + prefix + "\",\n")
    filewriter.write("\t\"node_name\": \"" + doc_id + "\",\n")
    filewriter.write("\t\"node_type\": \"d\",\n")
    filewriter.write("\t\"node_list\": [")

    node_string = ""
    for gene_name in druggable_gene_list:
        drug_list = gene_hash.get(gene_name)
        for node_name in drug_list:
            node_string = node_string + "{\"gene\": \"" + gene_name + "\", " \
                      + "\"doc_id\": \"" + node_name[0] + "\", \"drug_name\": \"" + node_name[1] + "\"" \
                      + ", \"drug_id\": \"" + node_name[2] + "\"}, "
    filewriter.write(node_string[:-2] + "]\n")
    filewriter.write("}\n")
    filewriter.write("'\n")

def process(workspace, data_set):

    drugbank_data_set = "Drugbank"
    gene_hash = process_drugbank_json(workspace, drugbank_data_set)

    print "The length of gene hash:" + str(len(gene_hash))

    cluster_data_set = "TCGA"
    process_cluster_json(workspace, data_set, cluster_data_set, gene_hash)

    cluster_data_set = "GEO"
    process_cluster_json(workspace, data_set, cluster_data_set, gene_hash)

## Main entry
if __name__ == "__main__":

    workspace = sys.argv[1]
    data_set = sys.argv[2]
    #workspace = "/Users/guorongxu/Desktop/SearchEngine"
    #data_set = "clusters_drugs"
    process(workspace, data_set)
