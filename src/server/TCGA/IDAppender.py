__author__ = 'guorongxu'

import os
import sys

## To process JSON files and append an id for each document.
def process_louvain_cluster_json(workspace, data_set):
    root_json_dir = workspace + "/" + data_set + "/louvain_json_files"
    ##id number rule:
    # the first digital "2" is the cluster index id;
    # the first two digital "02" is the TCGA louvain cluster type id;
    # the last sever digital "0000000" is the id.
    id_num = 2020000000

    for dirpath, directories, filenames in os.walk(root_json_dir):
        for filename in filenames:
            if filename.find(".json") > -1 and filename.find("gamma") > -1:
                input_file = os.path.join(dirpath, filename)
                output_file = input_file.replace(".json", ".json.new")

                if not os.path.exists(output_file):
                    filewriter = open(output_file, "a")
                    with open(input_file) as fp:
                        lines = fp.readlines()

                        for line in lines:
                            if line.startswith("curl -XPOST"):
                                filewriter.write(line.replace(" -d", "/" + str(id_num) + " -d"))
                                id_num = id_num + 1
                            else:
                                filewriter.write(line)
                    fp.closed
                    filewriter.close()

## To process JSON files and append an id for each document.
def process_ivanovska_cluster_json(workspace, data_set):
    root_json_dir = workspace + "/" + data_set + "/ivanovska_json_files"
    ##id number rule:
    # the first digital "2" is the cluster index id;
    # the first two digital "03" is the TCGA ivanovska cluster type id;
    # the last sever digital "0000000" is the id.
    id_num = 2030000000

    for dirpath, directories, filenames in os.walk(root_json_dir):
        for filename in filenames:
            if filename.find(".json") > -1 and filename.find("gamma") > -1:
                input_file = os.path.join(dirpath, filename)
                output_file = input_file.replace(".json", ".json.new")

                if not os.path.exists(output_file):
                    filewriter = open(output_file, "a")
                    with open(input_file) as fp:
                        lines = fp.readlines()

                        for line in lines:
                            if line.startswith("curl -XPOST"):
                                filewriter.write(line.replace(" -d", "/" + str(id_num) + " -d"))
                                id_num = id_num + 1
                            else:
                                filewriter.write(line)
                    fp.closed
                    filewriter.close()

## To process JSON files and append an id for each document.
def process_oslom_cluster_json(workspace, data_set):
    root_json_dir = workspace + "/" + data_set + "/oslom_undirected_json_files"
    ##id number rule:
    # the first digital "2" is the cluster index id;
    # the first two digital "04" is the TCGA oslom cluster type id;
    # the last sever digital "0000000" is the id.
    id_num = 2040000000

    for dirpath, directories, filenames in os.walk(root_json_dir):
        for filename in filenames:
            if filename.find(".json") > -1 and filename.find("gamma") > -1:
                input_file = os.path.join(dirpath, filename)
                output_file = input_file.replace(".json", ".json.new")

                if not os.path.exists(output_file):
                    filewriter = open(output_file, "a")
                    with open(input_file) as fp:
                        lines = fp.readlines()

                        for line in lines:
                            if line.startswith("curl -XPOST"):
                                filewriter.write(line.replace(" -d", "/" + str(id_num) + " -d"))
                                id_num = id_num + 1
                            else:
                                filewriter.write(line)
                    fp.closed
                    filewriter.close()

## To process JSON files and append an id for each document.
def process_star_json(workspace, data_set):
    root_json_dir = workspace + "/" + data_set + "/json_files"
    ##id number rule:
    # the first digital "1" is the genes index id;
    # the first two digital "02" is the TCGA star type id;
    # the last sever digital "0000000" is the id.
    id_num = 1020000000

    for dirpath, directories, filenames in os.walk(root_json_dir):
        for filename in filenames:
            if filename.find(".json") > -1 and filename.find("genes_tcga") > -1:
                input_file = os.path.join(dirpath, filename)
                output_file = input_file.replace(".json", ".json.new")

                if not os.path.exists(output_file):
                    filewriter = open(output_file, "a")
                    with open(input_file) as fp:
                        lines = fp.readlines()

                        for line in lines:
                            if line.startswith("curl -XPOST"):
                                filewriter.write(line.replace(" -d", "/" + str(id_num) + " -d"))
                                id_num = id_num + 1
                            else:
                                filewriter.write(line)
                    fp.closed
                    filewriter.close()

## Main entry
if __name__ == "__main__":

    workspace = sys.argv[1]
    data_set = sys.argv[2]
    #workspace = "/Users/guorongxu/Desktop/SearchEngine"
    #data_set = "TCGA"

    process_oslom_cluster_json(workspace, data_set)
    #process_star_json(workspace, data_set)
