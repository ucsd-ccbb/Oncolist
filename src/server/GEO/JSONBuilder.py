__author__ = 'guorongxu'

import sys
import re
import math
import os
import logging
import IDMapParser

## To print JSON file for each cluster.
def printJSON(outputFileName, project_info, networkType, clusterID, clusterSize, nodeList, nodeNames):
    index_type = "geo_cluster"

    if not os.path.exists(os.path.dirname(outputFileName)):
        os.makedirs(os.path.dirname(outputFileName))
    filewriter = open(outputFileName, "a")
    filewriter.write("curl -XPOST http://localhost:9200/clusters/" + index_type + " -d \'\n")
    filewriter.write("{\n")
    filewriter.write("\t\"source\": \"geo_data\",\n")
    filewriter.write("\t\"species\": \"human\",\n")
    filewriter.write("\t\"network_name\": \"" + project_info[2] + "\",\n")
    filewriter.write("\t\"network_type\": \"" + networkType + "\",\n")
    filewriter.write("\t\"author_name\": \"" + project_info[1] + "\",\n")
    filewriter.write("\t\"gse_number\": \"" + project_info[0] + "\",\n")
    filewriter.write("\t\"array_num\": \"" + project_info[3] + "\",\n")
    filewriter.write("\t\"institution_name\": \"" + project_info[4] + "\",\n")
    filewriter.write("\t\"node_name\": \"" + clusterID + "\",\n")
    filewriter.write("\t\"x_node_list_type\": \"" + "gene" + "\",\n")
    filewriter.write("\t\"x_node_list\": [")

    nodeString = ""
    for nodeName in nodeNames.split(','):
        nodeString = nodeString + "{\"name\": \"" + nodeName + "\"}, "

    filewriter.write(nodeString[:-2] + "],\n")

    filewriter.write("\t\"y_node_list_type\": \"" + "gene" + "\",\n")
    filewriter.write("\t\"y_node_list\": [")
    filewriter.write(nodeString[:-2] + "],\n")
    filewriter.write("\t\"correlation_matrix\": [")

    correlationStr = ""
    for i in range(0, len(nodeList)):
        x_loc = i / clusterSize
        y_loc = i % clusterSize
        node = nodeList[i]
        if math.fabs(float(node[0])) > 0:
            if i < (len(nodeList) - 1):
                if correlationStr == "":
                    correlationStr = "{\"x_loc\": " + str(x_loc) + ", \"y_loc\": " + str(y_loc) \
                            + ", \"correlation_value\": " + str(node[0]) + ", \"p_value\": " + str(node[2]) + "}, "
                else:
                    filewriter.write(correlationStr)
                    correlationStr = "{\"x_loc\": " + str(x_loc) + ", \"y_loc\": " + str(y_loc) \
                            + ", \"correlation_value\": " + str(node[0]) + ", \"p_value\": " + str(node[2]) + "}, "

    filewriter.write(correlationStr[:-2])
    filewriter.write("]\n")
    filewriter.write("}\n")
    filewriter.write("'\n")
    filewriter.close()

## To parse the file name to get the project information.
def parse_file_name(file_name):
    project_info = []
    gse_index = file_name.index("_")
    author_index = file_name.index("_", gse_index + 1)
    disease_index = file_name.index("_", author_index + 1)
    array_index = file_name.index("_Arrays")
    extension_index = file_name.index(".new_with_clusters")

    gse_number = file_name[0:gse_index]
    author_name = file_name[gse_index + 1 :author_index]
    disease_name = file_name[author_index + 1 :array_index]
    array_num = disease_name[disease_name.rindex("_") + 1 :]
    disease_name = disease_name[0:disease_name.rindex("_")]
    institution_name = file_name[array_index + len("_Arrays") : extension_index]

    project_info.append(gse_number)
    project_info.append(author_name)
    project_info.append(disease_name.replace("_", " ").strip())
    project_info.append(array_num)
    project_info.append(institution_name.replace("_", " ").strip())

    return project_info

def process(workspace):
    id_map_folder = workspace + "/ID_Map_tables/"

    logging.info("The system is parsing id map table.")
    id_vs_name_list, name_vs_id_list = IDMapParser.parse(id_map_folder)

    logging.info("The system is parsing cluster files.")
    logging.info("File name\tNumber of cluster")
    for root, directories, filenames in os.walk(workspace + "/cluster_files/"):
        for filename in filenames:
            try:
                if filename.endswith(".tsv"):
                    clusterList = {}
                    project_info = parse_file_name(filename)

                    cluster_file = os.path.join(root,filename)
                    outputFileName = cluster_file[:-4] + ".json"
                    outputFileName = outputFileName.replace("cluster_files", "json_files")
                    with open(cluster_file) as fp:
                        lines = fp.readlines()

                        for line in lines:
                            fields = re.split(r'\t+', line)
                            if fields[0] != "corr":
                                if fields[1] in clusterList:
                                    nodeList = clusterList.get(fields[1])
                                    nodeList.append(fields)
                                else:
                                    nodeList = []
                                    nodeList.append(fields)

                                clusterList.update({fields[1]: nodeList})

                        countedCluster = 0
                        for clusterID in clusterList:
                            nodeList = clusterList.get(clusterID)
                            length = len(nodeList)
                            clusterSize = int(math.sqrt(length))
                            nodeNames = ""

                            ## We only keep the cluster with the size with the range of 20-500.
                            if clusterSize <= 500 and clusterSize >= 20:
                                for i in range(0, clusterSize):
                                    node = nodeList[i]
                                    x_node = node[4][:-1]
                                    nodeNames = nodeNames + id_vs_name_list.get(x_node) + ","

                                printJSON(outputFileName, project_info, "gene_vs_gene", clusterID, clusterSize, nodeList, nodeNames[:-1])
                                countedCluster = countedCluster + 1

                        logging.info(cluster_file[len(workspace + "/cluster_files/"):] + "\t" + str(countedCluster))

                    fp.closed
            except ValueError:
                logging.error(os.path.join(root,filename)[len(workspace + "/cluster_files/"):])

    logging.info("Done.")

## Main entry
if __name__ == "__main__":

    #workspace = sys.argv[1]
    workspace = "/Users/guorongxu/Desktop/SearchEngine/GEO_data"

    process(workspace)